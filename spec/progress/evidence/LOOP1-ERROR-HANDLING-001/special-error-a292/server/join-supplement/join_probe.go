package main
import("context";"encoding/binary";"errors";"fmt";"io";"net";"time";"github.com/jackc/pgx/v5/pgconn";"github.com/jackc/pgx/v5/pgxpool")
func main(){
 ips,e:=net.LookupHost("localhost");if e!=nil{panic(e)};fmt.Println("Default localhost lookup:",ips)
 l,e:=net.Listen("tcp4","127.0.0.1:0");if e!=nil{panic(e)};defer l.Close();port:=l.Addr().(*net.TCPAddr).Port
 done:=make(chan error,1);go func(){c,e:=l.Accept();if e!=nil{done<-e;return};defer c.Close();c.SetDeadline(time.Now().Add(3*time.Second));var b [4]byte;if _,e=io.ReadFull(c,b[:]);e!=nil{done<-e;return};length:=binary.BigEndian.Uint32(b[:]);if length>65536||length<8{done<-fmt.Errorf("invalid startup length");return};if _,e=io.CopyN(io.Discard,c,int64(length-4));e!=nil{done<-e;return};payload:=[]byte("SFATAL\x00CXX000\x00Mcontrolled internal PostgreSQL failure\x00\x00");packet:=make([]byte,5+len(payload));packet[0]='E';binary.BigEndian.PutUint32(packet[1:5],uint32(4+len(payload)));copy(packet[5:],payload);_,e=c.Write(packet);done<-e}()
 cfg,e:=pgxpool.ParseConfig(fmt.Sprintf("postgres://join-audit@localhost:%d/test?sslmode=disable",port));if e!=nil{panic(e)};db,e:=pgxpool.NewWithConfig(context.Background(),cfg);if e!=nil{panic(e)};defer db.Close();ctx,cancel:=context.WithTimeout(context.Background(),4*time.Second);defer cancel();_,e=db.Begin(ctx);if e==nil{panic("unexpected BEGIN success")}
 var n net.Error;var p *pgconn.PgError;known:=errors.As(e,&n);unknown:=errors.As(e,&p)&&p.Code=="XX000";fmt.Printf("Actual pgxpool.Begin error type=%T knownNetwork=%t internalSQLSTATE=%t\n",e,known,unknown);fmt.Println(e.Error());if !known||!unknown{panic("mixed root not reproduced")};if se:=<-done;se!=nil{panic(se)}
 fmt.Println("REPRODUCED: current Outbox errors.As(net.Error) branch treats this complete mixed Begin error as retryable; unknown XX000 root does not propagate")
}
