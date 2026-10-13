package core

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgxpool"
	"net/http/httptest"
	"testing"
)

func TestOutboxBatchAndDispatcherDoNotDiscardClosedPoolFailure(t *testing.T) {
	db, err := pgxpool.New(context.Background(), "postgres://localhost/unused")
	if err != nil {
		t.Fatal(err)
	}
	db.Close()
	if err = relaySessionBatch(context.Background(), db, nil); err == nil {
		t.Fatal("closed database silently accepted")
	}
	if err = RelaySessionRevocations(context.Background(), db, nil); err == nil {
		t.Fatal("dispatcher reported success")
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if err = RelaySessionRevocations(ctx, db, nil); !errors.Is(err, context.Canceled) {
		t.Fatalf("lost cancellation: %v", err)
	}
}
func TestUnsupportedInternalResponseDoesNotBecomeEmptySuccess(t *testing.T) {
	writer := httptest.NewRecorder()
	defer func() {
		if recover() == nil {
			t.Fatal("internal encoding error swallowed")
		}
		if writer.Body.Len() != 0 || writer.Code != 200 {
			t.Fatal("internal error wrote false result")
		}
	}()
	writeJSON(writer, 200, make(chan int))
}
func TestUnknownMessageCommitPreservesOriginalCause(t *testing.T) {
	original := errors.New("controlled commit transport failure")
	err := newMessageCommitError(original)
	if !errors.Is(err, original) || !errors.Is(err, errCommitUnknown) {
		t.Fatal("commit cause or uncertainty marker lost")
	}
}
