package gateway

import (
 "context"
 "encoding/binary"
 "errors"
 "fmt"
 "io"
 "net"
 "net/http"
 "net/http/httptest"
 "strings"
 "github.com/gorilla/websocket"
 "testing"
 "time"

 "github.com/jackc/pgx/v5/pgconn"
 "github.com/jackc/pgx/v5/pgxpool"
)

func diagnosticTree(t *testing.T, err error, indent string) {
 t.Helper()
 if err == nil { t.Log(indent+"<nil>"); return }
 n, isNetwork := err.(net.Error)
 timeout := false
 if isNetwork { timeout = n.Timeout() }
 t.Logf("%s%T net=%v timeout=%v canceled=%v deadline=%v :: %v", indent, err, isNetwork, timeout, errors.Is(err,context.Canceled), errors.Is(err,context.DeadlineExceeded), err)
 if joined, ok := err.(interface{Unwrap() []error}); ok { for _, e := range joined.Unwrap() { diagnosticTree(t,e,indent+"  ") }; return }
 if wrapped, ok := err.(interface{Unwrap() error}); ok { diagnosticTree(t,wrapped.Unwrap(),indent+"  ") }
}

func diagnosticStalledStartup(t *testing.T, host string) (*pgxpool.Pool, <-chan time.Time) {
 t.Helper()
 listener, err := net.Listen("tcp4","127.0.0.1:0")
 if err != nil { t.Fatal(err) }
 started := make(chan time.Time,1)
 ended := make(chan struct{})
 go func(){
  defer close(ended)
  conn, err := listener.Accept()
  if err != nil { return }
  defer conn.Close()
  var header [4]byte
  if _,err = io.ReadFull(conn,header[:]); err != nil { return }
  n := binary.BigEndian.Uint32(header[:])
  if n<8 || n>65536 { return }
  if _,err = io.CopyN(io.Discard,conn,int64(n-4)); err != nil { return }
  started <- time.Now()
  _,_ = io.Copy(io.Discard,conn)
 }()
 cfg, err := pgxpool.ParseConfig(fmt.Sprintf("host=%s port=%d user=public_fixture dbname=public_fixture sslmode=disable",host,listener.Addr().(*net.TCPAddr).Port))
 if err != nil { t.Fatal(err) }
 if host == "localhost" { cfg.ConnConfig.LookupFunc = func(context.Context,string)([]string,error){ return []string{"127.0.0.1","::1"},nil } }
 pool,err := pgxpool.NewWithConfig(context.Background(),cfg)
 if err != nil { t.Fatal(err) }
 t.Cleanup(func(){pool.Close(); listener.Close(); <-ended})
 return pool,started
}

func TestDiagnosePoolCloseDuringWatch(t *testing.T) {
 for _,host := range []string{"127.0.0.1","localhost"} {
  t.Run(host,func(t *testing.T){
   pool,started := diagnosticStalledStartup(t,host)
   h,cl,token := watchFixture(t,pool)
   closed := make(chan struct{})
   go func(){ <-started; pool.Close(); close(closed) }()
   before:=time.Now()
   result:=observeWatchFailure(t,h,cl,token)
   elapsed:=time.Since(before)
   <-closed
   diagnosticTree(t,result,"")
   var connect *pgconn.ConnectError
   if !errors.As(result,&connect) || !errors.Is(result,context.Canceled) || errors.Is(result,context.DeadlineExceeded) || watchTransportFailure(result) {t.Fatalf("did not reproduce the CI error pattern: %T %v",result,result)}
   if elapsed > 1900*time.Millisecond {t.Fatalf("pool-close result did not arrive before watch deadline: %v",elapsed)}
   t.Logf("REPRODUCED pool.Close canceled real pgx construction during actual watch; elapsed=%v classifier=%v",elapsed,watchTransportFailure(result))
  })
 }
}

func TestDiagnoseWatchDeadlineControl(t *testing.T) {
 pool,_:=diagnosticStalledStartup(t,"127.0.0.1")
 h,cl,token:=watchFixture(t,pool)
 before:=time.Now()
 result:=observeWatchFailure(t,h,cl,token)
 diagnosticTree(t,result,"")
 if !errors.Is(result,context.DeadlineExceeded) || errors.Is(result,context.Canceled) || !watchTransportFailure(result){t.Fatalf("unexpected deadline control: %T %v",result,result)}
 t.Logf("CONTROL actual watch deadline returned %T classifier=%v elapsed=%v",result,watchTransportFailure(result),time.Since(before))
}

func TestDiagnoseAuthenticatePoolCloseContextOwner(t *testing.T) {
 pool,started:=diagnosticStalledStartup(t,"localhost")
 h,_,token:=watchFixture(t,pool)
 ctx,cancel:=context.WithTimeout(context.Background(),30*time.Second)
 defer cancel()
 go func(){<-started; pool.Close()}()
 _,result:=h.auth.authenticate(ctx,token)
 diagnosticTree(t,result,"")
 if ctx.Err()!=nil || !errors.Is(result,context.Canceled) || watchTransportFailure(result){t.Fatalf("cancellation owner not distinguished ctx=%v err=%v",ctx.Err(),result)}
 t.Logf("OWNER query ctx.Err=%v while result wraps context.Canceled; cancellation belongs to pool constructor base context",ctx.Err())
}

// Match fixture retirement ordering: peer close -> outer HTTP handler returns ->
// pool close, while the production watch is already waiting in authentication.
func TestDiagnoseRetiredSocketDoesNotJoinWatch(t *testing.T) {
 pool,started:=diagnosticStalledStartup(t,"localhost")
 h,cl,token:=watchFixture(t,pool)
 resultC:=make(chan error,1)
 handlerReturned:=make(chan struct{})
 retired:=make(chan struct{})
 server:=httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){
  ws,err:=(&websocket.Upgrader{}).Upgrade(w,r,nil)
  if err!=nil {return}
  c:=&connection{ws:ws,done:make(chan struct{}),bound:&cl,token:token}
  defer close(handlerReturned)
  defer c.close()
  go func(){resultC<-h.watch(c,cl);close(retired)}()
  _,_,_=ws.ReadMessage()
 }))
 defer server.Close()
 peer,_,err:=websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL,"http"),nil)
 if err!=nil {t.Fatal(err)}
 defer peer.Close()
 <-started
 if err=peer.Close();err!=nil {t.Fatal(err)}
 <-handlerReturned
 select {case <-retired:t.Fatal("watch unexpectedly ended before pool close");default:}
 pool.Close()
 result:=<-resultC
 diagnosticTree(t,result,"")
 if !errors.Is(result,context.Canceled)||watchTransportFailure(result){t.Fatalf("did not reproduce retirement failure: %v",result)}
 t.Log("REPRODUCED actual connection.close/c.done and outer handler return did not join in-flight production watch; pool.Close still canceled its pgx constructor")
}
