package gateway

import (
	"github.com/gorilla/websocket"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestFailedWebSocketWriteRetiresConnection(t *testing.T) {
	sockets := make(chan *websocket.Conn, 1)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		u := websocket.Upgrader{}
		ws, err := u.Upgrade(w, r, nil)
		if err != nil {
			return
		}
		sockets <- ws
	}))
	defer server.Close()
	peer, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer peer.Close()
	ws := <-sockets
	defer ws.Close()
	c := &connection{ws: ws, done: make(chan struct{})}
	if err = ws.UnderlyingConn().Close(); err != nil {
		t.Fatal(err)
	}
	if err = c.send(frame("pong", "10000000-0000-4000-8000-000000000001", map[string]any{})); err == nil {
		t.Fatal("write failure ignored")
	}
	select {
	case <-c.done:
	default:
		t.Fatal("failed socket remained active")
	}
	c.close()
}
