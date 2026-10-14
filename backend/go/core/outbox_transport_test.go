package core

import (
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"net"
	"os"
	"syscall"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
)

// This is a controlled PostgreSQL wire endpoint, not a real database fixture.
// Default pgx DNS/Dial must create the connection error tree itself.
func outboxInternalEndpoint(t *testing.T) int {
	t.Helper()
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	done := make(chan struct{})
	go func() {
		defer close(done)
		for {
			conn, err := listener.Accept()
			if err != nil {
				return
			}
			func() {
				defer conn.Close()
				conn.SetDeadline(time.Now().Add(2 * time.Second))
				var header [4]byte
				if _, err := io.ReadFull(conn, header[:]); err != nil {
					return
				}
				length := binary.BigEndian.Uint32(header[:])
				if length < 8 || length > 65536 {
					return
				}
				if _, err := io.CopyN(io.Discard, conn, int64(length-4)); err != nil {
					return
				}
				payload := []byte("SFATAL\x00CXX000\x00Mcontrolled internal PostgreSQL failure\x00\x00")
				packet := make([]byte, 5+len(payload))
				packet[0] = 'E'
				binary.BigEndian.PutUint32(packet[1:5], uint32(4+len(payload)))
				copy(packet[5:], payload)
				conn.Write(packet)
			}()
		}
	}()
	t.Cleanup(func() { listener.Close(); <-done })
	return listener.Addr().(*net.TCPAddr).Port
}

func outboxConnectionPool(t *testing.T, host string, port int) *pgxpool.Pool {
	t.Helper()
	cfg, err := pgxpool.ParseConfig(fmt.Sprintf("postgres://outbox-test@%s:%d/test?sslmode=disable&connect_timeout=2", host, port))
	if err != nil {
		t.Fatal(err)
	}
	db, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(db.Close)
	return db
}

func TestOutboxMixedDefaultConnectErrorPropagates(t *testing.T) {
	addresses, err := net.LookupHost("localhost")
	if err != nil {
		t.Fatal(err)
	}
	v4, v6 := false, false
	for _, address := range addresses {
		ip := net.ParseIP(address)
		if ip != nil && ip.IsLoopback() {
			if ip.To4() != nil {
				v4 = true
			} else {
				v6 = true
			}
		}
	}
	if !v4 || !v6 {
		t.Skipf("default localhost dual-address producer unavailable: %v", addresses)
	}
	db := outboxConnectionPool(t, "localhost", outboxInternalEndpoint(t))
	_, original := db.Begin(context.Background())
	var network net.Error
	var internal *pgconn.PgError
	if !errors.As(original, &network) || !errors.As(original, &internal) || internal.Code != "XX000" {
		t.Fatalf("default driver did not produce both roots: %T %v", original, original)
	}
	for _, failure := range []error{
		original,
		fmt.Errorf("actual connect wrapper: %w", original),
		errors.Join(nats.ErrTimeout, fmt.Errorf("actual connect wrapper: %w", errors.Join(original, network))),
	} {
		if outboxTransportFailure(failure) || !errors.Is(failure, original) {
			t.Fatal("actual nested mixed connection error reclassified or root lost")
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 1300*time.Millisecond)
	defer cancel()
	started := time.Now()
	result := RelaySessionRevocations(ctx, db, nil)
	var connect *pgconn.ConnectError
	if !errors.As(result, &connect) || !errors.As(result, &network) || !errors.As(result, &internal) || internal.Code != "XX000" {
		t.Fatalf("dispatcher lost complete mixed driver error: %T %v", result, result)
	}
	if errors.Is(result, context.DeadlineExceeded) || ctx.Err() != nil {
		t.Fatal("internal failure was retried until cancellation")
	}
	t.Logf("default mixed driver roots preserved by actual Relay in %s", time.Since(started))
}

func TestOutboxInternalOnlyDefaultConnectErrorPropagates(t *testing.T) {
	db := outboxConnectionPool(t, "127.0.0.1", outboxInternalEndpoint(t))
	ctx, cancel := context.WithTimeout(context.Background(), 1300*time.Millisecond)
	defer cancel()
	result := RelaySessionRevocations(ctx, db, nil)
	var internal *pgconn.PgError
	if !errors.As(result, &internal) || internal.Code != "XX000" || ctx.Err() != nil {
		t.Fatalf("internal-only error lost: %T %v", result, result)
	}
}

func TestOutboxAllNetworkDefaultConnectErrorsRetryUntilCancellation(t *testing.T) {
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	port := listener.Addr().(*net.TCPAddr).Port
	listener.Close()
	db := outboxConnectionPool(t, "localhost", port)
	ctx, cancel := context.WithTimeout(context.Background(), 1300*time.Millisecond)
	defer cancel()
	started := time.Now()
	result := RelaySessionRevocations(ctx, db, nil)
	if !errors.Is(result, context.DeadlineExceeded) || time.Since(started) < time.Second {
		t.Fatalf("known connection refusal stopped retry: %T %v", result, result)
	}
}

func TestOutboxCompleteTransportClassification(t *testing.T) {
	network := &net.OpError{Op: "dial", Net: "tcp", Err: os.NewSyscallError("connect", syscall.ECONNREFUSED)}
	unknown := errors.New("controlled internal invariant failure")
	pgInternal := &pgconn.PgError{Code: "XX000", Message: "controlled internal failure"}
	tests := []struct {
		name  string
		err   error
		retry bool
	}{
		{"network syscall wrapper", network, true},
		{"wrapped network", fmt.Errorf("connect: %w", network), true},
		{"closed NATS", nats.ErrConnectionClosed, true},
		{"disconnected NATS", nats.ErrDisconnected, true},
		{"NATS timeout", nats.ErrTimeout, true},
		{"deadline", context.DeadlineExceeded, true},
		{"all known joined", errors.Join(network, nats.ErrDisconnected, context.DeadlineExceeded), true},
		{"nested known joined", fmt.Errorf("connect: %w", errors.Join(fmt.Errorf("attempt: %w", network), errors.Join(nats.ErrTimeout, network))), true},
		{"unknown only", unknown, false},
		{"internal PG only", pgInternal, false},
		{"wrapped internal", fmt.Errorf("connect: %w", pgInternal), false},
		{"known first mixed", errors.Join(network, pgInternal), false},
		{"unknown first mixed", errors.Join(unknown, network), false},
		{"known deadline mixed", errors.Join(context.DeadlineExceeded, unknown), false},
		{"known NATS mixed", errors.Join(nats.ErrConnectionClosed, unknown), false},
		{"wrapped nested mixed", fmt.Errorf("connect: %w", errors.Join(network, errors.Join(nats.ErrTimeout, pgInternal))), false},
		{"network wrapper around mixed", &net.OpError{Op: "dial", Net: "tcp", Err: errors.Join(network, unknown)}, false},
		{"normal cancellation", context.Canceled, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := outboxTransportFailure(tt.err); got != tt.retry {
				t.Fatalf("retry=%t want=%t for %T", got, tt.retry, tt.err)
			}
		})
	}
}
