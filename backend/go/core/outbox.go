package core

import (
	"context"
	"log"
	"net"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
)

// Session and message events are stored in the same transaction as their writes.
// Publishing can repeat after a crash; the gateway handles duplicate events.
func RelaySessionRevocations(ctx context.Context, db *pgxpool.Pool, nc *nats.Conn) error {
	ticker := time.NewTicker(500 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			if err := relaySessionBatch(ctx, db, nc); err != nil {
				if ctx.Err() != nil {
					return ctx.Err()
				}
				if outboxTransportFailure(err) {
					log.Print("Outbox transport batch failed; pending events retained for next tick")
					continue
				}
				return err
			}
		}
	}
}

// pgx may join failures from multiple connection attempts. Retry only when
// every branch is a known transport fault; keep the original error for callers.
func outboxTransportFailure(err error) bool {
	known := false
	for err != nil {
		if joined, ok := err.(interface{ Unwrap() []error }); ok {
			branches := joined.Unwrap()
			if len(branches) == 0 {
				return false
			}
			for _, branch := range branches {
				if !outboxTransportFailure(branch) {
					return false
				}
			}
			return true
		}
		if _, ok := err.(net.Error); ok {
			// net.OpError wraps a syscall error that does not itself implement net.Error.
			known = true
		}
		if err == nats.ErrConnectionClosed || err == nats.ErrDisconnected || err == nats.ErrTimeout || err == context.DeadlineExceeded {
			known = true
		}
		if wrapped, ok := err.(interface{ Unwrap() error }); ok {
			err = wrapped.Unwrap()
			continue
		}
		return known
	}
	return false
}

func relaySessionBatch(ctx context.Context, db *pgxpool.Pool, nc *nats.Conn) error {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	tx, err := db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)
	rows, err := tx.Query(ctx, `SELECT event_id,event_type,payload,conversation_id FROM outbox_events WHERE event_type IN ('session.revoked','message.created') AND published_at IS NULL ORDER BY created_at,event_id LIMIT 32 FOR UPDATE SKIP LOCKED`)
	if err != nil {
		return err
	}
	type event struct {
		id           string
		payload      []byte
		kind         string
		conversation *string
	}
	var events []event
	for rows.Next() {
		var e event
		if err = rows.Scan(&e.id, &e.kind, &e.payload, &e.conversation); err != nil {
			rows.Close()
			return err
		}
		events = append(events, e)
	}
	err = rows.Err()
	rows.Close()
	if err != nil {
		return err
	}
	for _, e := range events {
		if e.kind == "session.revoked" {
			if err = nc.Publish("session.revoked", e.payload); err != nil {
				return err
			}
		} else {
			// Core owns recipient membership. Subjects are private routing
			// locators; every payload remains the canonical created frame.
			members, err := tx.Query(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, e.conversation)
			if err != nil {
				return err
			}
			var users []string
			for members.Next() {
				var user string
				if err = members.Scan(&user); err != nil {
					members.Close()
					return err
				}
				users = append(users, user)
			}
			err = members.Err()
			members.Close()
			if err != nil {
				return err
			}
			for _, user := range users {
				if err = nc.Publish("message.created."+user, e.payload); err != nil {
					return err
				}
			}
		}
	}
	if len(events) > 0 {
		if err = nc.FlushTimeout(2 * time.Second); err != nil {
			return err
		}
	}
	for _, e := range events {
		if _, err = tx.Exec(ctx, `UPDATE outbox_events SET published_at=now(),attempts=attempts+1 WHERE event_id=$1`, e.id); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
}
