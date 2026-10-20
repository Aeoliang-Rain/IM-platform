package core

import (
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"reflect"
	"slices"
	"sort"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgproto3"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
)

// These tests use the existing CI disposable database. The local execution owner
// additionally qualifies its server and supplies a newly owned, exact search_path.
type groupFixture struct {
	t      *testing.T
	db     *pgxpool.Pool
	s      *authService
	users  []string
	claims []claims
	tokens []string
}

func groupUUID(t *testing.T) string {
	t.Helper()
	id, err := uuid()
	if err != nil {
		t.Fatal(err)
	}
	return id
}

func groupPool(t *testing.T, cfg *pgxpool.Config) *pgxpool.Pool {
	t.Helper()
	db, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(db.Close)
	if err = db.Ping(context.Background()); err != nil {
		t.Fatal(err)
	}
	if options := os.Getenv("PGOPTIONS"); strings.HasPrefix(options, "-c search_path=") {
		var path string
		if err = db.QueryRow(context.Background(), `SHOW search_path`).Scan(&path); err != nil {
			t.Fatal(err)
		}
		if path != strings.TrimPrefix(options, "-c search_path=") {
			t.Fatalf("pool search_path %q differs from owned execution input", path)
		}
	}
	return db
}

func newGroupFixture(t *testing.T, n int) *groupFixture {
	t.Helper()
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	cfg, err := pgxpool.ParseConfig("")
	if err != nil {
		t.Fatal(err)
	}
	cfg.MaxConns = 20
	cfg.ConnConfig.RuntimeParams["application_name"] = "group-test-" + groupUUID(t)
	db := groupPool(t, cfg)
	f := &groupFixture{t: t, db: db, s: &authService{db: db, codec: &shared.Codec{Key: []byte("group-test-only-signing-key-at-least-32-bytes"), Now: time.Now}, now: time.Now}}
	// Register cleanup before inserting anything. All deletes are scoped to this
	// fixture's UUID users and their conversations, including every receipt FK.
	t.Cleanup(func() {
		ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()
		queries := []string{
			`DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=ANY($1::uuid[]) AND event_type='session.revoked')`,
			`DELETE FROM outbox_events WHERE aggregate_id=ANY($1::uuid[]) OR conversation_id IN (SELECT conversation_id FROM conversations WHERE created_by=ANY($1::uuid[]))`,
			`DELETE FROM user_sync_events WHERE user_id=ANY($1::uuid[])`,
			`DELETE FROM group_operation_receipts WHERE actor_id=ANY($1::uuid[]) OR conversation_id IN (SELECT conversation_id FROM conversations WHERE created_by=ANY($1::uuid[]))`,
			`DELETE FROM messages WHERE conversation_id IN (SELECT conversation_id FROM conversations WHERE created_by=ANY($1::uuid[]))`,
			`DELETE FROM friendships WHERE user_low_id=ANY($1::uuid[]) OR user_high_id=ANY($1::uuid[])`,
			`DELETE FROM conversation_members WHERE conversation_id IN (SELECT conversation_id FROM conversations WHERE created_by=ANY($1::uuid[]))`,
			`DELETE FROM conversations WHERE created_by=ANY($1::uuid[])`,
			`DELETE FROM sessions WHERE user_id=ANY($1::uuid[])`,
			`DELETE FROM users WHERE user_id=ANY($1::uuid[])`,
		}
		for _, q := range queries {
			if _, err := db.Exec(ctx, q, f.users); err != nil {
				t.Errorf("fixture cleanup: %v", err)
			}
		}
	})
	for i := 0; i < n; i++ {
		id := groupUUID(t)
		f.users = append(f.users, id)
		f.exec(`INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,'Same display name','group-test-only')`, id, "g"+id)
		sid, epoch, _, _, err := f.s.newSession(context.Background(), id, clientInput{ClientType: "WEB", DeviceID: "group-test"})
		if err != nil {
			t.Fatal(err)
		}
		c := claims{UserID: id, SessionID: sid, SessionEpoch: epoch, ClientType: "WEB", IssuedAt: time.Now().Unix(), ExpiresAt: time.Now().Add(time.Hour).Unix()}
		token, err := f.s.codec.Sign(c)
		if err != nil {
			t.Fatal(err)
		}
		f.claims = append(f.claims, c)
		f.tokens = append(f.tokens, token)
	}
	return f
}

func (f *groupFixture) exec(q string, args ...any) {
	f.t.Helper()
	if _, err := f.db.Exec(context.Background(), q, args...); err != nil {
		f.t.Fatal(err)
	}
}
func (f *groupFixture) count(q string, args ...any) int {
	f.t.Helper()
	var n int
	if err := f.db.QueryRow(context.Background(), q, args...).Scan(&n); err != nil {
		f.t.Fatal(err)
	}
	return n
}
func (f *groupFixture) friend(a, b int) string {
	f.t.Helper()
	tx, err := f.db.Begin(context.Background())
	if err != nil {
		f.t.Fatal(err)
	}
	low, high := pair(f.users[a], f.users[b])
	id, _, err := assembleFriendship(context.Background(), tx, low, high, f.users[a])
	if err != nil {
		var cause error = err
		groupRollback(context.Background(), tx, &cause)
		f.t.Fatal(cause)
	}
	if err = tx.Commit(context.Background()); err != nil {
		f.t.Fatal(err)
	}
	return id
}
func (f *groupFixture) change(actor int, input groupRequest, conversation string) (groupResult, error) {
	return f.s.changeGroup(context.Background(), f.tokens[actor], f.claims[actor], input, conversation)
}
func (f *groupFixture) create(actor int, targets ...int) groupResult {
	f.t.Helper()
	in := groupRequest{RequestID: groupUUID(f.t)}
	for _, i := range targets {
		in.Members = append(in.Members, f.users[i])
	}
	sort.Strings(in.Members)
	v, err := f.change(actor, in, "")
	if err != nil {
		f.t.Fatal(err)
	}
	return v
}
func (f *groupFixture) request(method, path, body, token, media string) *httptest.ResponseRecorder {
	f.t.Helper()
	r := httptest.NewRequest(method, path, strings.NewReader(body))
	if token != "" {
		r.Header.Set("Authorization", "Bearer "+token)
	}
	if media != "" {
		r.Header.Set("Content-Type", media)
	}
	w := httptest.NewRecorder()
	NewHandler(f.db, f.s.codec.Key).ServeHTTP(w, r)
	return w
}
func groupBody(t *testing.T, v any) string {
	t.Helper()
	b, e := json.Marshal(v)
	if e != nil {
		t.Fatal(e)
	}
	return string(b)
}
func groupCode(t *testing.T, w *httptest.ResponseRecorder, status int, code string) {
	t.Helper()
	var v struct {
		RequestID string `json:"requestId"`
		Error     struct {
			Code string `json:"code"`
		} `json:"error"`
	}
	if w.Code != status || json.Unmarshal(w.Body.Bytes(), &v) != nil || v.Error.Code != code || !groupID.MatchString(v.RequestID) || w.Header().Get("Cache-Control") != "no-store" {
		t.Fatalf("HTTP %d %s, want %d/%s", w.Code, w.Body.String(), status, code)
	}
}
func groupKnown(t *testing.T, err error, status int, code string) {
	t.Helper()
	e, ok := err.(apiError)
	if !ok || e.Status != status || e.Code != code {
		t.Fatalf("got %v, want %d/%s", err, status, code)
	}
}

func (f *groupFixture) effects() []int {
	f.t.Helper()
	var out []int
	for _, q := range []string{
		`SELECT count(*) FROM conversations WHERE created_by=ANY($1::uuid[])`,
		`SELECT count(*) FROM conversation_members WHERE conversation_id IN(SELECT conversation_id FROM conversations WHERE created_by=ANY($1::uuid[]))`,
		`SELECT count(*) FROM group_operation_receipts WHERE actor_id=ANY($1::uuid[])`,
		`SELECT count(*) FROM user_sync_events WHERE user_id=ANY($1::uuid[])`,
		`SELECT count(*) FROM outbox_events WHERE aggregate_id=ANY($1::uuid[])`,
	} {
		out = append(out, f.count(q, f.users))
	}
	return out
}

func TestGroupHTTPJSONEncodingPrecedence(t *testing.T) {
	server := httptest.NewServer(NewHandler(nil, []byte("group-http-input-test-key")))
	t.Cleanup(server.Close)
	id := groupUUID(t)
	prefix := `{"requestId":"` + id + `","memberUserIds":["`
	suffix := `"]}`
	for _, route := range []struct{ name, path string }{
		{"create", "/v1/groups"},
		{"add", "/v1/groups/30000000-0000-4000-8000-000000000001/members"},
	} {
		t.Run(route.name, func(t *testing.T) {
			for _, tc := range []struct {
				name, body, code string
				status           int
				correlated       bool
			}{
				{"valid", prefix + "10000000-0000-4000-8000-000000000002" + suffix, "AUTH_REQUIRED", 401, true},
				{"valid-unicode-before-shape", prefix + "é" + suffix, "AUTH_REQUIRED", 401, true},
				{"non-object-before-shape", "null", "AUTH_REQUIRED", 401, false},
				{"broken-json", `{"requestId":`, "VALIDATION_FAILED", 400, false},
				{"invalid-utf8-ff", prefix + "\xff" + suffix, "VALIDATION_FAILED", 400, false},
				{"invalid-utf8-c328", prefix + "\xc3\x28" + suffix, "VALIDATION_FAILED", 400, false},
			} {
				t.Run(tc.name, func(t *testing.T) {
					r, err := http.NewRequest(http.MethodPost, server.URL+route.path, strings.NewReader(tc.body))
					if err != nil {
						t.Fatal(err)
					}
					r.Header.Set("Content-Type", "application/json")
					response, err := server.Client().Do(r)
					if err != nil {
						t.Fatal(err)
					}
					body, readErr := io.ReadAll(response.Body)
					closeErr := response.Body.Close()
					if readErr != nil || closeErr != nil {
						t.Fatal(errors.Join(readErr, closeErr))
					}
					var result struct {
						RequestID string `json:"requestId"`
						Error     struct {
							Code string `json:"code"`
						} `json:"error"`
					}
					if response.StatusCode != tc.status || json.Unmarshal(body, &result) != nil || result.Error.Code != tc.code ||
						!groupID.MatchString(result.RequestID) || response.Header.Get("Cache-Control") != "no-store" {
						t.Fatalf("HTTP %d %s, want %d/%s with UUID and no-store", response.StatusCode, body, tc.status, tc.code)
					}
					if (result.RequestID == id) != tc.correlated {
						t.Fatalf("requestId correlation = %q, correlated = %t", result.RequestID, tc.correlated)
					}
				})
			}
		})
	}
}

func TestGroupHTTPBoundariesAndAuthorization(t *testing.T) {
	f := newGroupFixture(t, 4)
	f.friend(0, 1)
	f.friend(0, 2)
	id := groupUUID(t)
	good := groupBody(t, groupRequest{id, []string{f.users[1]}})
	for _, tc := range []struct {
		name, body, path, token, media string
		status                         int
		code                           string
	}{
		{"malformed", "{", "/v1/groups", "", "application/json", 400, "VALIDATION_FAILED"},
		{"media", good, "/v1/groups", "", "text/plain", 400, "VALIDATION_FAILED"},
		{"query", good, "/v1/groups?x=1", "", "application/json", 400, "VALIDATION_FAILED"},
		{"forcequery", good, "/v1/groups?", "", "application/json", 400, "VALIDATION_FAILED"},
		{"duplicate", `{"requestId":"` + id + `","requestId":"` + id + `","memberUserIds":[]}`, "/v1/groups", "", "application/json", 400, "VALIDATION_FAILED"},
		{"oversize", strings.Repeat(" ", 16385), "/v1/groups", "", "application/json", 400, "VALIDATION_FAILED"},
		{"auth-before-shape", "null", "/v1/groups", "", "application/json", 401, "AUTH_REQUIRED"},
		{"missing", `{"requestId":"` + id + `"}`, "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"extra", strings.TrimSuffix(good, "}") + `,"extra":1}`, "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"empty", groupBody(t, groupRequest{id, []string{}}), "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"self", groupBody(t, groupRequest{id, []string{f.users[0]}}), "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"uppercase", groupBody(t, groupRequest{strings.ToUpper(id), []string{f.users[1]}}), "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"wrong-array", `{"requestId":"` + id + `","memberUserIds":null}`, "/v1/groups", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
		{"nonfriend", groupBody(t, groupRequest{id, []string{f.users[3]}}), "/v1/groups", f.tokens[0], "application/json", 403, "AUTHORIZATION_DENIED"},
		{"nonexistent", groupBody(t, groupRequest{id, []string{groupUUID(t)}}), "/v1/groups", f.tokens[0], "application/json", 403, "AUTHORIZATION_DENIED"},
		{"bad-path", good, "/v1/groups/not-an-id/members", f.tokens[0], "application/json", 400, "VALIDATION_FAILED"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			before := f.effects()
			w := f.request("POST", tc.path, tc.body, tc.token, tc.media)
			groupCode(t, w, tc.status, tc.code)
			if !reflect.DeepEqual(before, f.effects()) {
				t.Fatal("rejection persisted effects")
			}
		})
	}
	tooMany := make([]string, 101)
	for i := range tooMany {
		tooMany[i] = f.users[1]
	}
	groupCode(t, f.request("POST", "/v1/groups", groupBody(t, groupRequest{id, tooMany}), f.tokens[0], "application/json"), 400, "VALIDATION_FAILED")
	w := f.request("POST", "/v1/groups", groupBody(t, groupRequest{id, []string{f.users[2], f.users[1], f.users[1]}}), f.tokens[0], "application/json; charset=utf-8")
	if w.Code != 201 || w.Header().Get("Cache-Control") != "no-store" {
		t.Fatalf("create: %d %s", w.Code, w.Body.String())
	}
	var first groupResult
	if err := json.Unmarshal(w.Body.Bytes(), &first); err != nil {
		t.Fatal(err)
	}
	if len(first.Added) != 3 || !sort.StringsAreSorted(first.Added) {
		t.Fatal("create result is not canonical")
	}
	retry := f.request("POST", "/v1/groups", groupBody(t, groupRequest{id, []string{f.users[1], f.users[2]}}), f.tokens[0], "application/json")
	if retry.Code != 201 || retry.Body.String() != w.Body.String() {
		t.Fatal("HTTP original result/status changed")
	}
	addBody := groupBody(t, groupRequest{groupUUID(t), []string{f.users[1]}})
	addPath := "/v1/groups/" + first.ConversationID + "/members"
	added := f.request("POST", addPath, addBody, f.tokens[0], "application/json")
	var noOp groupResult
	if added.Code != 200 || json.Unmarshal(added.Body.Bytes(), &noOp) != nil || noOp.Added == nil || len(noOp.Added) != 0 || noOp.ConversationID != first.ConversationID {
		t.Fatalf("HTTP ADD no-op result/status: %d %s", added.Code, added.Body.String())
	}
	addReplay := f.request("POST", addPath, addBody, f.tokens[0], "application/json")
	if addReplay.Code != 200 || addReplay.Body.String() != added.Body.String() {
		t.Fatal("HTTP ADD original result/status changed")
	}
	groupCode(t, f.request("POST", "/v1/groups", good, f.tokens[0], "application/json"), 409, "GROUP_REQUEST_CONFLICT")
	for _, path := range []string{"/v1/conversations?requestId=" + id + "&bad=1", "/v1/conversations?requestId=" + id + "&limit=01", "/v1/conversations?requestId=" + id + "&limit=101", "/v1/conversations?requestId=" + id + "&limit=0", "/v1/conversations?requestId=" + id + "&afterMemberUserId=" + f.users[0], "/v1/conversations?requestId=" + id + "&requestId=" + id} {
		groupCode(t, f.request("GET", path, "", f.tokens[0], ""), 400, "VALIDATION_FAILED")
	}
	groupCode(t, f.request("GET", "/v1/conversations?requestId="+id, "{}", f.tokens[0], ""), 400, "VALIDATION_FAILED")
}

func TestGroupOriginalResultsCurrentAuthorizationAndEvents(t *testing.T) {
	f := newGroupFixture(t, 5)
	for _, p := range [][2]int{{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}} {
		f.friend(p[0], p[1])
	}
	create := groupRequest{groupUUID(t), []string{f.users[1]}}
	first, err := f.change(0, create, "")
	if err != nil {
		t.Fatal(err)
	}
	add := groupRequest{groupUUID(t), []string{f.users[2]}}
	second, err := f.change(1, add, first.ConversationID)
	if err != nil || !slices.Equal(second.Added, []string{f.users[2]}) {
		t.Fatalf("member add: %v %v", second, err)
	}
	before := f.effects()
	retry, err := f.change(0, create, "")
	if err != nil || !reflect.DeepEqual(first, retry) || !reflect.DeepEqual(before, f.effects()) {
		t.Fatal("create replay derived mutable membership")
	}
	nop := groupRequest{groupUUID(t), []string{f.users[1]}}
	empty, err := f.change(0, nop, first.ConversationID)
	if err != nil || empty.Added == nil || len(empty.Added) != 0 {
		t.Fatalf("no-op: %v %v", empty, err)
	}
	before = f.effects()
	again, err := f.change(0, nop, first.ConversationID)
	if err != nil || !reflect.DeepEqual(empty, again) || !reflect.DeepEqual(before, f.effects()) {
		t.Fatal("no-op replay changed result/effects")
	}
	// The operation namespaces and per-conversation ADD identity are independent.
	if _, err = f.change(0, groupRequest{create.RequestID, []string{f.users[3]}}, first.ConversationID); err != nil {
		t.Fatal(err)
	}
	before = f.effects()
	replayedAdd, err := f.change(1, add, first.ConversationID)
	if err != nil || !reflect.DeepEqual(second, replayedAdd) || !reflect.DeepEqual(before, f.effects()) {
		t.Fatal("ADD replay derived mutable membership or added event effects")
	}
	other := f.create(0, 1)
	if _, err = f.change(1, add, other.ConversationID); err != nil {
		t.Fatal(err)
	}
	_, err = f.change(4, add, first.ConversationID)
	groupKnown(t, err, 403, "AUTHORIZATION_DENIED")
	low, high := pair(f.users[0], f.users[1])
	f.exec(`DELETE FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high)
	_, err = f.change(0, create, "")
	groupKnown(t, err, 403, "AUTHORIZATION_DENIED")
	_, err = f.change(0, groupRequest{create.RequestID, []string{f.users[4]}}, "")
	groupKnown(t, err, 403, "AUTHORIZATION_DENIED")
	f.exec(`UPDATE conversation_members SET left_at=now() WHERE conversation_id=$1 AND user_id=$2`, first.ConversationID, f.users[1])
	_, err = f.change(1, add, first.ConversationID)
	groupKnown(t, err, 403, "AUTHORIZATION_DENIED")
	// Public identity for a nonfriend remains available to an authorized member.
	page, err := f.s.conversationPage(context.Background(), f.tokens[2], f.claims[2], groupUUID(t), 100, groupContinuation{})
	if err != nil {
		t.Fatal(err)
	}
	found := false
	for _, row := range page.Items {
		if row.ConversationID == first.ConversationID && row.Member.User.UserID == f.users[3] {
			found = row.Member.User.Username == "g"+f.users[3] && row.Member.User.DisplayName == "Same display name"
		}
	}
	if !found {
		t.Fatal("authorized nonfriend identity missing")
	}
	rows, err := f.db.Query(context.Background(), `SELECT s.cursor_id,s.event_type,s.payload,o.payload FROM user_sync_events s JOIN outbox_events o ON o.event_id=(s.payload->>'eventId')::uuid WHERE s.user_id=ANY($1::uuid[]) AND s.payload->>'subjectId' IN($2,$3) ORDER BY s.cursor_id`, f.users, first.ConversationID, other.ConversationID)
	if err != nil {
		t.Fatal(err)
	}
	defer rows.Close()
	n := 0
	var previous int64
	for rows.Next() {
		var cursor int64
		var kind string
		var a, b []byte
		if err = rows.Scan(&cursor, &kind, &a, &b); err != nil {
			t.Fatal(err)
		}
		var event struct {
			Cursor   string `json:"cursor"`
			Revision int64  `json:"revision"`
			Kind     string `json:"kind"`
		}
		var out struct {
			Event json.RawMessage `json:"event"`
		}
		if json.Unmarshal(a, &event) != nil || json.Unmarshal(b, &out) != nil {
			t.Fatal("invalid event")
		}
		var aa, bb any
		if json.Unmarshal(a, &aa) != nil || json.Unmarshal(out.Event, &bb) != nil {
			t.Fatal("invalid outbox event")
		}
		if event.Revision != cursor || event.Cursor != fmt.Sprint(cursor) || event.Kind != kind || cursor <= previous || !reflect.DeepEqual(aa, bb) {
			t.Fatal("revision/cursor/Sync-Outbox identity differs")
		}
		previous = cursor
		n++
	}
	if err = rows.Err(); err != nil {
		t.Fatal(err)
	}
	if n != 28 {
		t.Fatalf("group event pairs %d want 28", n)
	}
}

func TestGroupConcurrentIdentitiesAndMembership(t *testing.T) {
	f := newGroupFixture(t, 6)
	for i := 1; i < 6; i++ {
		f.friend(0, i)
	}
	f.friend(1, 2)
	f.friend(1, 3)
	input := groupRequest{groupUUID(t), []string{f.users[1], f.users[2]}}
	sort.Strings(input.Members)
	concurrent := func(actor int, in groupRequest, conversation string, n int) []groupResult {
		t.Helper()
		start := make(chan struct{})
		type outcome struct {
			v groupResult
			e error
		}
		ch := make(chan outcome, n)
		for i := 0; i < n; i++ {
			go func() { <-start; v, e := f.change(actor, in, conversation); ch <- outcome{v, e} }()
		}
		close(start)
		out := make([]groupResult, 0, n)
		for i := 0; i < n; i++ {
			select {
			case r := <-ch:
				if r.e != nil {
					t.Fatal(r.e)
				}
				out = append(out, r.v)
			case <-time.After(15 * time.Second):
				t.Fatal("concurrent group operation stuck")
			}
		}
		for _, v := range out {
			if !reflect.DeepEqual(v, out[0]) {
				t.Fatal("concurrent retry produced different original results")
			}
		}
		return out
	}
	first := concurrent(0, input, "", 8)[0]
	if n := f.count(`SELECT count(*) FROM conversations WHERE created_by=$1 AND group_create_request_id=$2`, f.users[0], input.RequestID); n != 1 {
		t.Fatal("duplicate create")
	}
	add := groupRequest{groupUUID(t), []string{f.users[3], f.users[4]}}
	sort.Strings(add.Members)
	concurrent(0, add, first.ConversationID, 8)
	if n := f.count(`SELECT count(*) FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, first.ConversationID); n != 5 {
		t.Fatalf("membership count %d", n)
	}
	// Different requests/actors overlapping current members must serialize without
	// duplicate membership or omitted recipient event pairs.
	other := f.create(1, 0)
	type result struct {
		v groupResult
		e error
	}
	ch := make(chan result, 2)
	for _, job := range []struct {
		actor        int
		conversation string
	}{{0, first.ConversationID}, {1, other.ConversationID}} {
		request := groupUUID(t)
		go func(actor int, conversation, request string) {
			v, e := f.change(actor, groupRequest{request, []string{f.users[2]}}, conversation)
			ch <- result{v, e}
		}(job.actor, job.conversation, request)
	}
	for i := 0; i < 2; i++ {
		select {
		case r := <-ch:
			if r.e != nil {
				t.Fatal(r.e)
			}
		case <-time.After(15 * time.Second):
			t.Fatal("cross-conversation operation deadlocked")
		}
	}
	// Same CREATE identity with different verified friend targets has one winner.
	key := groupUUID(t)
	for _, target := range []string{f.users[4], f.users[5]} {
		go func(target string) { v, e := f.change(0, groupRequest{key, []string{target}}, ""); ch <- result{v, e} }(target)
	}
	wins, conflicts := 0, 0
	for i := 0; i < 2; i++ {
		r := <-ch
		if r.e == nil {
			wins++
		} else {
			groupKnown(t, r.e, 409, "GROUP_REQUEST_CONFLICT")
			conflicts++
		}
	}
	if wins != 1 || conflicts != 1 {
		t.Fatal("different-target identity race did not select one original")
	}
}

func (f *groupFixture) trigger(table, event, condition, statement string, deferred bool) func() {
	f.t.Helper()
	name := "gp" + strings.ReplaceAll(groupUUID(f.t), "-", "")
	f.exec(fmt.Sprintf(`CREATE FUNCTION %s() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF %s THEN %s; END IF; RETURN NEW; END $$`, name, condition, statement))
	prefix := "CREATE TRIGGER " + name + " BEFORE " + event + " ON " + table
	if deferred {
		prefix = "CREATE CONSTRAINT TRIGGER " + name + " AFTER " + event + " ON " + table + " DEFERRABLE INITIALLY DEFERRED"
	}
	f.exec(prefix + " FOR EACH ROW EXECUTE FUNCTION " + name + "()")
	var once sync.Once
	cleanup := func() {
		once.Do(func() { f.exec("DROP TRIGGER " + name + " ON " + table); f.exec("DROP FUNCTION " + name + "()") })
	}
	f.t.Cleanup(cleanup)
	return cleanup
}

func TestGroupEveryWriteAndDeferredCommitRollback(t *testing.T) {
	for _, operation := range []string{"CREATE", "ADD"} {
		for _, point := range []string{"conversation", "member-first", "member-later", "receipt", "sync-insert", "sync-update", "outbox", "commit"} {
			if operation == "ADD" && point == "conversation" {
				continue
			}
			t.Run(operation+"/"+point, func(t *testing.T) {
				f := newGroupFixture(t, 4)
				for i := 1; i < 4; i++ {
					f.friend(0, i)
				}
				conversation := ""
				if operation == "ADD" {
					conversation = f.create(0, 1).ConversationID
				}
				targets := []string{f.users[2], f.users[3]}
				sort.Strings(targets)
				in := groupRequest{groupUUID(t), targets}
				actor := f.users[0]
				table, event, condition := "group_operation_receipts", "INSERT", fmt.Sprintf("NEW.actor_id='%s'::uuid", actor)
				switch point {
				case "conversation":
					table = "conversations"
					condition = fmt.Sprintf("NEW.created_by='%s'::uuid AND NEW.kind='GROUP'", actor)
				case "member-first", "member-later":
					table = "conversation_members"
					target := actor
					if operation == "ADD" {
						target = targets[0]
					}
					if point == "member-later" {
						target = targets[1]
					}
					condition = fmt.Sprintf("NEW.user_id='%s'::uuid AND EXISTS(SELECT 1 FROM conversations WHERE conversation_id=NEW.conversation_id AND kind='GROUP')", target)
				case "sync-insert", "sync-update":
					table = "user_sync_events"
					if point == "sync-update" {
						event = "UPDATE"
					}
					condition = fmt.Sprintf("NEW.user_id='%s'::uuid AND NEW.event_type IN('conversation.changed','membership.changed')", actor)
				case "outbox":
					table = "outbox_events"
					condition = fmt.Sprintf("NEW.aggregate_id='%s'::uuid AND NEW.event_type IN('conversation.changed','membership.changed')", actor)
				}
				remove := f.trigger(table, event, condition, "RAISE EXCEPTION 'group-write-fault-"+point+"'", point == "commit")
				before := f.effects()
				_, err := f.change(0, in, conversation)
				var pgErr *pgconn.PgError
				if !errors.As(err, &pgErr) || pgErr.Code != "P0001" || !strings.Contains(pgErr.Message, "group-write-fault-"+point) {
					t.Fatalf("actual PG fault cause lost: %v", err)
				}
				if !reflect.DeepEqual(before, f.effects()) {
					t.Fatalf("%s rollback left effects: %v -> %v", point, before, f.effects())
				}
				remove()
				if _, err = f.change(0, in, conversation); err != nil {
					t.Fatalf("original request could not retry after rollback: %v", err)
				}
			})
		}
	}
}

func (f *groupFixture) waitBlocked(blocker uint32) uint32 {
	f.t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 8*time.Second)
	defer cancel()
	for {
		var pid uint32
		err := f.db.QueryRow(ctx, `SELECT pid FROM pg_stat_activity WHERE datname=current_database() AND application_name=$1 AND $2=ANY(pg_blocking_pids(pid)) LIMIT 1`, f.db.Config().ConnConfig.RuntimeParams["application_name"], blocker).Scan(&pid)
		if err == nil {
			return pid
		}
		if !errors.Is(err, pgx.ErrNoRows) {
			f.t.Fatal(err)
		}
		select {
		case <-ctx.Done():
			f.t.Fatal("owned PostgreSQL barrier was not observed")
		case <-time.After(10 * time.Millisecond):
		}
	}
}

func TestGroupCommitBarrierAndSessionRevalidation(t *testing.T) {
	t.Run("commit-is-not-response", func(t *testing.T) {
		f := newGroupFixture(t, 2)
		f.friend(0, 1)
		guard, err := f.db.Acquire(context.Background())
		if err != nil {
			t.Fatal(err)
		}
		defer guard.Release()
		key := time.Now().UnixNano()
		if _, err = guard.Exec(context.Background(), `SELECT pg_advisory_lock($1)`, key); err != nil {
			t.Fatal(err)
		}
		locked := true
		defer func() {
			if locked {
				if _, e := guard.Exec(context.Background(), `SELECT pg_advisory_unlock($1)`, key); e != nil {
					t.Error(e)
				}
			}
		}()
		f.trigger("group_operation_receipts", "INSERT", fmt.Sprintf("NEW.actor_id='%s'::uuid", f.users[0]), fmt.Sprintf("PERFORM pg_advisory_xact_lock(%d)", key), true)
		type result struct {
			v groupResult
			e error
		}
		ch := make(chan result, 1)
		in := groupRequest{groupUUID(t), []string{f.users[1]}}
		before := f.effects()
		go func() { v, e := f.change(0, in, ""); ch <- result{v, e} }()
		f.waitBlocked(guard.Conn().PgConn().PID())
		select {
		case <-ch:
			t.Fatal("success before COMMIT completed")
		default:
		}
		if !reflect.DeepEqual(before, f.effects()) {
			t.Fatal("uncommitted group became visible")
		}
		if _, err = guard.Exec(context.Background(), `SELECT pg_advisory_unlock($1)`, key); err != nil {
			t.Fatal(err)
		}
		locked = false
		select {
		case r := <-ch:
			if r.e != nil || r.v.ConversationID == "" {
				t.Fatalf("commit failed: %v", r.e)
			}
		case <-time.After(8 * time.Second):
			t.Fatal("deferred commit did not complete")
		}
	})
	for _, state := range []string{"REVOKED", "EPOCH", "EXPIRED"} {
		t.Run("session-"+state, func(t *testing.T) {
			f := newGroupFixture(t, 2)
			f.friend(0, 1)
			tx, err := f.db.Begin(context.Background())
			if err != nil {
				t.Fatal(err)
			}
			defer func() {
				var e error
				groupRollback(context.Background(), tx, &e)
				if e != nil {
					t.Error(e)
				}
			}()
			if _, err = tx.Exec(context.Background(), `SELECT user_id FROM users WHERE user_id=$1 FOR NO KEY UPDATE`, f.users[0]); err != nil {
				t.Fatal(err)
			}
			var guardPID uint32
			if err = tx.QueryRow(context.Background(), `SELECT pg_backend_pid()`).Scan(&guardPID); err != nil {
				t.Fatal(err)
			}
			before := f.effects()
			ch := make(chan error, 1)
			request := groupUUID(t)
			go func() { _, e := f.change(0, groupRequest{request, []string{f.users[1]}}, ""); ch <- e }()
			f.waitBlocked(guardPID)
			q := `UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL WHERE user_id=$1`
			want := "AUTH_SESSION_REVOKED"
			if state == "EPOCH" {
				q = `UPDATE sessions SET session_epoch=session_epoch+1 WHERE user_id=$1`
				want = "AUTH_SESSION_EPOCH_STALE"
			}
			if state == "EXPIRED" {
				q = `UPDATE sessions SET expires_at=now()-interval '1 second' WHERE user_id=$1`
			}
			f.exec(q, f.users[0])
			if err = tx.Commit(context.Background()); err != nil {
				t.Fatal(err)
			}
			select {
			case e := <-ch:
				groupKnown(t, e, 401, want)
			case <-time.After(8 * time.Second):
				t.Fatal("session recheck stuck")
			}
			if !reflect.DeepEqual(before, f.effects()) {
				t.Fatal("stale Session persisted group effects")
			}
		})
	}
}

// This device wraps the existing pgx frontend IO after pgx's TLS negotiation.
// It never fabricates a backend reply: only the real server COMMIT completion
// frame arms the cutoff. The observer verifies durability before releasing EOF.
type groupCommitCut struct {
	mu             sync.Mutex
	armed, pending bool
	frontend       []byte
	committed      chan struct{}
	release        chan struct{}
	once           sync.Once
}

func newGroupCommitCut() *groupCommitCut {
	return &groupCommitCut{committed: make(chan struct{}), release: make(chan struct{})}
}
func (c *groupCommitCut) arm()     { c.mu.Lock(); defer c.mu.Unlock(); c.armed = true; c.frontend = nil }
func (c *groupCommitCut) unblock() { c.once.Do(func() { close(c.release) }) }

type groupCutWriter struct {
	io.Writer
	c *groupCommitCut
}

func (w *groupCutWriter) Write(p []byte) (int, error) {
	w.c.mu.Lock()
	if w.c.armed {
		w.c.frontend = append(w.c.frontend, p...)
		for len(w.c.frontend) >= 5 {
			n := int(binary.BigEndian.Uint32(w.c.frontend[1:5]))
			if n < 4 || n > 1<<24 {
				w.c.mu.Unlock()
				return 0, errors.New("invalid observed frontend frame length")
			}
			if len(w.c.frontend) < n+1 {
				break
			}
			frame := w.c.frontend[:n+1]
			if frame[0] == 'Q' && string(frame[5:]) == "commit\x00" {
				w.c.pending = true
			}
			w.c.frontend = w.c.frontend[n+1:]
		}
	}
	w.c.mu.Unlock()
	return w.Writer.Write(p)
}

type groupCutReader struct {
	io.Reader
	c      *groupCommitCut
	buffer []byte
	cut    bool
}

func (r *groupCutReader) Read(p []byte) (int, error) {
	if r.cut {
		return 0, io.ErrUnexpectedEOF
	}
	if len(r.buffer) == 0 {
		header := make([]byte, 5)
		if _, err := io.ReadFull(r.Reader, header); err != nil {
			return 0, err
		}
		n := int(binary.BigEndian.Uint32(header[1:]))
		if n < 4 || n > 1<<24 {
			return 0, errors.New("invalid observed backend frame length")
		}
		frame := make([]byte, n+1)
		copy(frame, header)
		if _, err := io.ReadFull(r.Reader, frame[5:]); err != nil {
			return 0, err
		}
		r.c.mu.Lock()
		cut := r.c.armed && r.c.pending && frame[0] == 'C' && string(frame[5:]) == "COMMIT\x00"
		r.c.mu.Unlock()
		if cut {
			r.cut = true
			close(r.c.committed)
			<-r.c.release
			return 0, io.ErrUnexpectedEOF
		}
		r.buffer = frame
	}
	n := copy(p, r.buffer)
	r.buffer = r.buffer[n:]
	return n, nil
}

func TestGroupServerCommittedButReplyLost(t *testing.T) {
	f := newGroupFixture(t, 2)
	f.friend(0, 1)
	cfg, err := pgxpool.ParseConfig("")
	if err != nil {
		t.Fatal(err)
	}
	cfg.MaxConns = 1
	cut := newGroupCommitCut()
	defer cut.unblock()
	factory := cfg.ConnConfig.BuildFrontend
	cfg.ConnConfig.BuildFrontend = func(r io.Reader, w io.Writer) *pgproto3.Frontend {
		return factory(&groupCutReader{Reader: r, c: cut}, &groupCutWriter{Writer: w, c: cut})
	}
	db := groupPool(t, cfg)
	s := *f.s
	s.db = db
	cut.arm()
	in := groupRequest{groupUUID(t), []string{f.users[1]}}
	type result struct {
		v groupResult
		e error
	}
	ch := make(chan result, 1)
	go func() {
		v, e := s.changeGroup(context.Background(), f.tokens[0], f.claims[0], in, "")
		ch <- result{v, e}
	}()
	select {
	case <-cut.committed:
	case <-time.After(10 * time.Second):
		t.Fatal("no actual PostgreSQL COMMIT completion observed")
	}
	var original groupResult
	original.RequestID = in.RequestID
	if err = f.db.QueryRow(context.Background(), `SELECT conversation_id,added_member_user_ids::text[],created_at FROM group_operation_receipts WHERE actor_id=$1 AND operation='CREATE' AND request_id=$2`, f.users[0], in.RequestID).Scan(&original.ConversationID, &original.Added, &original.CreatedAt); err != nil {
		t.Fatalf("server completion without durable receipt: %v", err)
	}
	if f.count(`SELECT count(*) FROM conversation_members WHERE conversation_id=$1`, original.ConversationID) != 2 || f.count(`SELECT count(*) FROM user_sync_events WHERE payload->>'subjectId'=$1`, original.ConversationID) != 4 || f.count(`SELECT count(*) FROM outbox_events WHERE payload->'event'->>'subjectId'=$1`, original.ConversationID) != 4 {
		t.Fatal("actual COMMIT omitted atomic effects")
	}
	t.Log("observed real backend CommandComplete COMMIT; independent connection verified receipt, 2 members, 4 Sync and 4 Outbox before EOF release")
	before := f.effects()
	select {
	case <-ch:
		t.Fatal("caller completed before test released response loss")
	default:
	}
	cut.unblock()
	select {
	case r := <-ch:
		if r.e == nil || !errors.Is(r.e, io.ErrUnexpectedEOF) {
			t.Fatalf("unknown commit lost IO root cause: %v", r.e)
		}
	case <-time.After(10 * time.Second):
		t.Fatal("lost reply did not fail caller")
	}
	retry, err := f.change(0, in, "")
	if err != nil || !reflect.DeepEqual(original, retry) || !reflect.DeepEqual(before, f.effects()) {
		t.Fatalf("unknown-commit retry changed original result/effects: %v", err)
	}
	t.Log("client failed with retained unexpected EOF; original request replayed the durable original result without new effects")
}

func TestGroupHTTPResponseLostBeforeAndAfterCommit(t *testing.T) {
	for _, after := range []bool{false, true} {
		t.Run(fmt.Sprint("after=", after), func(t *testing.T) {
			f := newGroupFixture(t, 2)
			f.friend(0, 1)
			in := groupRequest{groupUUID(t), []string{f.users[1]}}
			handler := NewHandler(f.db, f.s.codec.Key)
			var mu sync.Mutex
			first := true
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				mu.Lock()
				drop := first
				first = false
				mu.Unlock()
				if drop {
					if after {
						record := httptest.NewRecorder()
						handler.ServeHTTP(record, r)
						if record.Code != 201 {
							t.Errorf("pre-cut handler status %d: %s", record.Code, record.Body.String())
						}
					}
					conn, _, err := w.(http.Hijacker).Hijack()
					if err != nil {
						t.Error(err)
						return
					}
					if err = conn.Close(); err != nil {
						t.Error(err)
					}
					return
				}
				handler.ServeHTTP(w, r)
			}))
			defer server.Close()
			post := func() (*http.Response, error) {
				r, e := http.NewRequest("POST", server.URL+"/v1/groups", strings.NewReader(groupBody(t, in)))
				if e != nil {
					return nil, e
				}
				r.Header.Set("Content-Type", "application/json")
				r.Header.Set("Authorization", "Bearer "+f.tokens[0])
				return server.Client().Do(r)
			}
			if response, err := post(); err == nil {
				response.Body.Close()
				t.Fatal("truncated HTTP response accepted")
			}
			n := f.count(`SELECT count(*) FROM group_operation_receipts WHERE actor_id=$1 AND request_id=$2`, f.users[0], in.RequestID)
			if n != map[bool]int{false: 0, true: 1}[after] {
				t.Fatal("HTTP loss position does not match durable state")
			}
			response, err := post()
			if err != nil {
				t.Fatal(err)
			}
			defer response.Body.Close()
			if response.StatusCode != 201 {
				t.Fatal("original HTTP request retry failed")
			}
			var result groupResult
			if err = json.NewDecoder(response.Body).Decode(&result); err != nil {
				t.Fatal(err)
			}
			if f.count(`SELECT count(*) FROM group_operation_receipts WHERE actor_id=$1 AND request_id=$2`, f.users[0], in.RequestID) != 1 {
				t.Fatal("HTTP retry duplicated receipt")
			}
		})
	}
}

func TestGroupSnapshotBeyondOneHundredAndFromStartRecovery(t *testing.T) {
	f := newGroupFixture(t, 207)
	for i := 1; i < len(f.users); i++ {
		f.friend(0, i)
	}
	targets := func(a, b int) []string { v := append([]string(nil), f.users[a:b]...); sort.Strings(v); return v }
	first, err := f.change(0, groupRequest{groupUUID(t), targets(1, 101)}, "")
	if err != nil {
		t.Fatal(err)
	}
	for _, bounds := range [][2]int{{101, 201}, {201, 207}} {
		if _, err = f.change(0, groupRequest{groupUUID(t), targets(bounds[0], bounds[1])}, first.ConversationID); err != nil {
			t.Fatal(err)
		}
	}
	scan := func(limit int) []groupRow {
		t.Helper()
		var all []groupRow
		after := groupContinuation{}
		for pages := 0; pages < 1000; pages++ {
			p, e := f.s.conversationPage(context.Background(), f.tokens[1], f.claims[1], groupUUID(t), limit, after)
			if e != nil {
				t.Fatal(e)
			}
			if p.Items == nil || len(p.Items) > limit {
				t.Fatal("invalid page size")
			}
			for _, row := range p.Items {
				if row.Kind != "DIRECT" && row.ConversationID != first.ConversationID {
					t.Fatal("snapshot leaked unrelated conversation")
				}
				if row.Member.User.Username != "g"+row.Member.User.UserID {
					t.Fatal("member identity differs")
				}
				if len(all) > 0 {
					last := all[len(all)-1]
					if last.ConversationID > row.ConversationID || last.ConversationID == row.ConversationID && last.Member.User.UserID >= row.Member.User.UserID {
						t.Fatal("tuple cursor was not exclusive and sorted")
					}
				}
				all = append(all, row)
			}
			if !p.HasMore {
				if p.Next != (groupContinuation{}) {
					t.Fatal("terminal continuation not empty")
				}
				return all
			}
			last := p.Items[len(p.Items)-1]
			if p.Next != (groupContinuation{last.ConversationID, last.Member.User.UserID}) {
				t.Fatal("continuation not last emitted tuple")
			}
			after = p.Next
		}
		t.Fatal("pagination did not terminate")
		return nil
	}
	all := scan(100)
	if len(all) != 209 {
		t.Fatalf("total GROUP+DIRECT rows %d want 209", len(all))
	}
	if len(scan(1)) != 209 {
		t.Fatal("limit=1 dropped rows")
	}
	// Insert a formerly inactive low tuple after the reader passed it. A saved
	// continuation cannot recover it; the required independent from-start scan can.
	low := slices.Min(f.users[2:])
	f.exec(`UPDATE conversation_members SET left_at=now() WHERE conversation_id=$1 AND user_id=$2`, first.ConversationID, low)
	if len(scan(73)) != 208 {
		t.Fatal("active membership filter failed")
	}
	page, err := f.s.conversationPage(context.Background(), f.tokens[1], f.claims[1], groupUUID(t), 100, groupContinuation{})
	if err != nil || !page.HasMore {
		t.Fatalf("initial page: %v", err)
	}
	if _, err = f.change(0, groupRequest{groupUUID(t), []string{low}}, first.ConversationID); err != nil {
		t.Fatal(err)
	}
	after := page.Next
	for {
		p, e := f.s.conversationPage(context.Background(), f.tokens[1], f.claims[1], groupUUID(t), 100, after)
		if e != nil {
			t.Fatal(e)
		}
		for _, row := range p.Items {
			if row.ConversationID == first.ConversationID && row.Member.User.UserID == low {
				t.Fatal("low tuple was unexpectedly after the saved cursor")
			}
		}
		if !p.HasMore {
			break
		}
		after = p.Next
	}
	f.exec(`UPDATE users SET display_name='Updated same display' WHERE user_id=$1`, low)
	recovered := scan(99)
	found := false
	for _, row := range recovered {
		if row.ConversationID == first.ConversationID && row.Member.User.UserID == low {
			found = row.Member.User.DisplayName == "Updated same display"
		}
	}
	if !found || len(recovered) != 209 {
		t.Fatal("from-start scan missed lower tuple insertion/update")
	}
}

type groupRollbackFault struct {
	pgx.Tx
	err error
}

func (tx groupRollbackFault) Rollback(context.Context) error { return tx.err }
func TestGroupUnknownAndCleanupErrorsPropagate(t *testing.T) {
	cleanup := errors.New("actual cleanup boundary failure")
	known := groupDenied()
	err := known
	groupRollback(context.Background(), groupRollbackFault{err: cleanup}, &err)
	if !errors.Is(err, cleanup) || !errors.Is(err, known) {
		t.Fatal("rollback discarded one cause")
	}
	for _, cause := range []error{err, fmt.Errorf("wrapped unknown: %w", known), errors.New("unclassified database failure")} {
		func() {
			defer func() {
				if got := recover(); got != cause {
					t.Fatalf("unknown cause projected or replaced: %v", got)
				}
			}()
			groupFailure(httptest.NewRecorder(), "", cause)
		}()
	}
	w := httptest.NewRecorder()
	groupFailure(w, groupUUID(t), known)
	groupCode(t, w, 403, "AUTHORIZATION_DENIED")
	// A valid legacy GROUP remains readable/addable, but CREATE cannot invent its
	// original targets from later mutable membership or misclassify it as 409.
	f := newGroupFixture(t, 3)
	f.friend(0, 1)
	f.friend(0, 2)
	id, request := groupUUID(t), groupUUID(t)
	f.exec(`INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES($1,'GROUP',$2,$3)`, id, f.users[0], request)
	f.exec(`INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'OWNER'),($1,$3,'MEMBER')`, id, f.users[0], f.users[1])
	_, cause := f.change(0, groupRequest{request, []string{f.users[1]}}, "")
	if cause == nil || !strings.Contains(cause.Error(), "persisted-original-group-result-missing") {
		t.Fatalf("legacy receipt loss fabricated result: %v", cause)
	}
	if _, cause = f.change(0, groupRequest{groupUUID(t), []string{f.users[2]}}, id); cause != nil {
		t.Fatal(cause)
	}
}

func (f *groupFixture) advisory() (*pgxpool.Conn, int64, func()) {
	f.t.Helper()
	guard, err := f.db.Acquire(context.Background())
	if err != nil {
		f.t.Fatal(err)
	}
	key := time.Now().UnixNano()
	if _, err = guard.Exec(context.Background(), `SELECT pg_advisory_lock($1)`, key); err != nil {
		guard.Release()
		f.t.Fatal(err)
	}
	var once sync.Once
	release := func() {
		once.Do(func() {
			if _, err := guard.Exec(context.Background(), `SELECT pg_advisory_unlock($1)`, key); err != nil {
				f.t.Error(err)
			}
			guard.Release()
		})
	}
	f.t.Cleanup(release)
	return guard, key, release
}

func TestGroupUserLockCompatibilityWithLogoutAndSend(t *testing.T) {
	t.Run("logout-Session-before-user-FK", func(t *testing.T) {
		f := newGroupFixture(t, 2)
		f.friend(0, 1)
		guard, key, release := f.advisory()
		defer release()
		f.trigger("user_sync_events", "INSERT", fmt.Sprintf("NEW.user_id='%s'::uuid AND NEW.event_type='session.revoked'", f.users[0]), fmt.Sprintf("PERFORM pg_advisory_xact_lock(%d)", key), false)
		logout := make(chan *httptest.ResponseRecorder, 1)
		go func() {
			r := httptest.NewRequest("POST", "/v1/auth/logout", nil)
			r.Header.Set("Authorization", "Bearer "+f.tokens[0])
			w := httptest.NewRecorder()
			f.s.logout(w, r)
			logout <- w
		}()
		logoutPID := f.waitBlocked(guard.Conn().PgConn().PID())
		group := make(chan error, 1)
		request := groupUUID(t)
		go func() { _, err := f.change(0, groupRequest{request, []string{f.users[1]}}, ""); group <- err }()
		f.waitBlocked(logoutPID) // Group owns users and waits on this real Session.
		release()
		select {
		case w := <-logout:
			if w.Code != 204 {
				t.Fatalf("logout failed/deadlocked: %d %s", w.Code, w.Body.String())
			}
		case <-time.After(8 * time.Second):
			t.Fatal("logout FK/user lock cycle")
		}
		select {
		case err := <-group:
			groupKnown(t, err, 401, "AUTH_SESSION_REVOKED")
		case <-time.After(8 * time.Second):
			t.Fatal("group stayed blocked after logout")
		}
		if f.count(`SELECT count(*) FROM group_operation_receipts WHERE actor_id=$1`, f.users[0]) != 0 || f.count(`SELECT count(*) FROM conversations WHERE kind='GROUP' AND created_by=$1`, f.users[0]) != 0 {
			t.Fatal("logout race persisted unauthorized group")
		}
	})
	t.Run("send-conversation-before-sender-FK", func(t *testing.T) {
		f := newGroupFixture(t, 3)
		f.friend(0, 1)
		f.friend(0, 2)
		original := f.create(0, 1)
		guard, key, release := f.advisory()
		defer release()
		f.trigger("messages", "INSERT", fmt.Sprintf("NEW.conversation_id='%s'::uuid", original.ConversationID), fmt.Sprintf("PERFORM pg_advisory_xact_lock(%d)", key), false)
		frame := sendFrame{ProtocolVersion: "1.0", Type: "message.send", RequestID: groupUUID(t)}
		frame.Payload.ConversationID = original.ConversationID
		frame.Payload.Content = textContent{Kind: "TEXT", Text: "send holds conversation"}
		send := make(chan error, 1)
		go func() { _, err := f.s.commitMessage(context.Background(), f.claims[0], frame); send <- err }()
		sendPID := f.waitBlocked(guard.Conn().PgConn().PID())
		group := make(chan error, 1)
		input := groupRequest{groupUUID(t), []string{f.users[2]}}
		go func() { _, err := f.change(0, input, original.ConversationID); group <- err }()
		f.waitBlocked(sendPID) // Group owns users and waits on real send's row lock.
		release()
		for _, ch := range []chan error{send, group} {
			select {
			case err := <-ch:
				if err != nil {
					t.Fatalf("send/ADD lock compatibility failed: %v", err)
				}
			case <-time.After(8 * time.Second):
				t.Fatal("send sender FK/user lock cycle")
			}
		}
		if f.count(`SELECT count(*) FROM messages WHERE conversation_id=$1`, original.ConversationID) != 1 || f.count(`SELECT count(*) FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, original.ConversationID) != 3 {
			t.Fatal("send/ADD lost atomic effects")
		}
	})
}

func TestGroupRescansMembersBeforeLockingAndUserSyncCommittedPrefix(t *testing.T) {
	t.Run("new-member-requires-earlier-lock-retry", func(t *testing.T) {
		f := newGroupFixture(t, 5)
		indices := []int{0, 1, 2, 3, 4}
		sort.Slice(indices, func(a, b int) bool { return f.users[indices[a]] < f.users[indices[b]] })
		low, added, old, actor := indices[0], indices[2], indices[3], indices[4]
		for _, target := range []int{low, added, old} {
			f.friend(actor, target)
		}
		original := f.create(actor, old)
		guard, err := f.db.Begin(context.Background())
		if err != nil {
			t.Fatal(err)
		}
		defer func() {
			var cause error
			groupRollback(context.Background(), guard, &cause)
			if cause != nil {
				t.Error(cause)
			}
		}()
		if _, err = guard.Exec(context.Background(), `SELECT user_id FROM users WHERE user_id=$1 FOR NO KEY UPDATE`, f.users[low]); err != nil {
			t.Fatal(err)
		}
		var pid uint32
		if err = guard.QueryRow(context.Background(), `SELECT pg_backend_pid()`).Scan(&pid); err != nil {
			t.Fatal(err)
		}
		result := make(chan error, 1)
		input := groupRequest{groupUUID(t), []string{f.users[low]}}
		go func() { _, err := f.change(actor, input, original.ConversationID); result <- err }()
		f.waitBlocked(pid)
		// This legitimate operation commits while the first attempt still has the
		// old membership set and cannot yet acquire its first sorted user lock.
		if _, err = f.change(actor, groupRequest{groupUUID(t), []string{f.users[added]}}, original.ConversationID); err != nil {
			t.Fatal(err)
		}
		reader, err := f.db.Begin(context.Background())
		if err != nil {
			t.Fatal(err)
		}
		defer func() {
			var cause error
			groupRollback(context.Background(), reader, &cause)
			if cause != nil {
				t.Error(cause)
			}
		}()
		if _, err = reader.Exec(context.Background(), `SELECT user_id FROM users WHERE user_id=$1 FOR SHARE`, f.users[added]); err != nil {
			t.Fatal(err)
		}
		var readerPID uint32
		if err = reader.QueryRow(context.Background(), `SELECT pg_backend_pid()`).Scan(&readerPID); err != nil {
			t.Fatal(err)
		}
		if err = guard.Commit(context.Background()); err != nil {
			t.Fatal(err)
		}
		f.waitBlocked(readerPID) // Proves reattempt locked the newly observed member.
		select {
		case <-result:
			t.Fatal("new recipient user lock was omitted")
		default:
		}
		if err = reader.Commit(context.Background()); err != nil {
			t.Fatal(err)
		}
		select {
		case err = <-result:
			if err != nil {
				t.Fatal(err)
			}
		case <-time.After(8 * time.Second):
			t.Fatal("sorted-set retry stuck")
		}
		if f.count(`SELECT count(*) FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, original.ConversationID) != 4 {
			t.Fatal("membership recheck lost a concurrent addition")
		}
	})
	t.Run("UserSync-waits-for-whole-group-event-pair", func(t *testing.T) {
		f := newGroupFixture(t, 2)
		f.friend(0, 1)
		var previous int64
		if err := f.db.QueryRow(context.Background(), `SELECT max(cursor_id) FROM user_sync_events WHERE user_id=$1`, f.users[0]).Scan(&previous); err != nil {
			t.Fatal(err)
		}
		guard, key, release := f.advisory()
		defer release()
		f.trigger("group_operation_receipts", "INSERT", fmt.Sprintf("NEW.actor_id='%s'::uuid", f.users[0]), fmt.Sprintf("PERFORM pg_advisory_xact_lock(%d)", key), true)
		input := groupRequest{groupUUID(t), []string{f.users[1]}}
		change := make(chan error, 1)
		go func() { _, err := f.change(0, input, ""); change <- err }()
		producerPID := f.waitBlocked(guard.Conn().PgConn().PID())
		request := map[string]any{"syncVersion": "1.0", "type": "sync.user.request", "requestId": groupUUID(t), "cursor": f.s.syncCursor(f.users[0], previous), "limit": 100}
		body := groupBody(t, request)
		page := make(chan *httptest.ResponseRecorder, 1)
		go func() {
			r := httptest.NewRequest("POST", "/v1/sync/user", strings.NewReader(body))
			r.Header.Set("Authorization", "Bearer "+f.tokens[0])
			w := httptest.NewRecorder()
			f.s.syncUser(w, r)
			page <- w
		}()
		f.waitBlocked(producerPID)
		select {
		case <-page:
			t.Fatal("UserSync passed uncommitted producer")
		default:
		}
		release()
		select {
		case err := <-change:
			if err != nil {
				t.Fatal(err)
			}
		case <-time.After(8 * time.Second):
			t.Fatal("producer did not finish")
		}
		select {
		case w := <-page:
			var got struct {
				Events  []syncUserEvent `json:"events"`
				HasMore bool            `json:"hasMore"`
				Next    string          `json:"nextCursor"`
			}
			if w.Code != 200 || json.Unmarshal(w.Body.Bytes(), &got) != nil || len(got.Events) != 2 || got.HasMore || got.Events[0].Kind != "conversation.changed" || got.Events[1].Kind != "membership.changed" || got.Next != got.Events[1].Cursor {
				t.Fatalf("group committed prefix incomplete: %d %s", w.Code, w.Body.String())
			}
		case <-time.After(8 * time.Second):
			t.Fatal("UserSync did not finish")
		}
	})
}

type groupWriteFault struct {
	header http.Header
	err    error
}

func (w *groupWriteFault) Header() http.Header       { return w.header }
func (w *groupWriteFault) WriteHeader(int)           {}
func (w *groupWriteFault) Write([]byte) (int, error) { return 0, w.err }

func TestGroupResponseIOAndRealRollbackFailureKeepCauses(t *testing.T) {
	writeFailure := errors.New("response transport failed")
	for _, tc := range []struct{ cause, want error }{{writeFailure, writeFailure}, {nil, io.ErrShortWrite}} {
		func() {
			defer func() {
				if got := recover(); got != tc.want {
					t.Fatalf("response IO cause lost: %v", got)
				}
			}()
			groupJSON(&groupWriteFault{header: make(http.Header), err: tc.cause}, 201, groupResult{})
		}()
	}
	f := newGroupFixture(t, 2)
	f.friend(0, 1)
	before := f.effects()
	tx, err := f.db.Begin(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	id := groupUUID(t)
	if _, err = tx.Exec(context.Background(), `INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES($1,'GROUP',$2,$3)`, id, f.users[0], groupUUID(t)); err != nil {
		var cause error = err
		groupRollback(context.Background(), tx, &cause)
		t.Fatal(cause)
	}
	// Close only this owned test connection while its real transaction is open.
	// PostgreSQL rolls it back; the attempted explicit rollback must still retain
	// its actual conn-closed cause alongside the original canonical rejection.
	if err = tx.Conn().PgConn().Close(context.Background()); err != nil {
		t.Fatal(err)
	}
	known := groupDenied()
	err = known
	groupRollback(context.Background(), tx, &err)
	if err == known || !errors.Is(err, known) {
		t.Fatalf("real rollback did not preserve both causes: %v", err)
	}
	var knownPart apiError
	if !errors.As(err, &knownPart) {
		t.Fatal("canonical original cause disappeared")
	}
	func() {
		defer func() {
			if got := recover(); got != err {
				t.Fatalf("cleanup failure was projected as 4xx: %v", got)
			}
		}()
		groupFailure(httptest.NewRecorder(), groupUUID(t), err)
	}()
	if !reflect.DeepEqual(before, f.effects()) {
		t.Fatal("closed owned transaction left persisted effects")
	}
	t.Logf("real pgx rollback failure retained with primary rejection and propagated: %v", err)
}

func TestGroupHTTPCurrentAuthAndSnapshot(t *testing.T) {
	f := newGroupFixture(t, 3)
	direct := f.friend(0, 1)
	original := f.create(0, 1)
	request := groupUUID(t)
	w := f.request("GET", "/v1/conversations?requestId="+request, "", f.tokens[1], "")
	var page groupPage
	if w.Code != 200 || w.Header().Get("Cache-Control") != "no-store" || json.Unmarshal(w.Body.Bytes(), &page) != nil || page.RequestID != request || len(page.Items) != 4 || page.HasMore || page.Next != (groupContinuation{}) {
		t.Fatalf("HTTP snapshot: %d %s", w.Code, w.Body.String())
	}
	seen := map[string]bool{}
	for _, row := range page.Items {
		seen[row.ConversationID] = true
	}
	if !seen[direct] || !seen[original.ConversationID] {
		t.Fatal("HTTP snapshot omitted DIRECT/GROUP")
	}
	other := f.request("GET", "/v1/conversations?requestId="+request, "", f.tokens[2], "")
	if other.Code != 200 || json.Unmarshal(other.Body.Bytes(), &page) != nil || page.Items == nil || len(page.Items) != 0 {
		t.Fatal("outsider snapshot leaked or returned null rows")
	}
	groupCode(t, f.request("GET", "/v1/conversations?requestId="+request, "", "", ""), 401, "AUTH_REQUIRED")
	groupCode(t, f.request("GET", "/v1/conversations?requestId="+request, "", "invalid-token", ""), 401, "AUTH_TOKEN_INVALID")
	expired := f.claims[1]
	expired.IssuedAt = time.Now().Add(-2 * time.Hour).Unix()
	expired.ExpiresAt = time.Now().Add(-time.Hour).Unix()
	token, err := f.s.codec.Sign(expired)
	if err != nil {
		t.Fatal(err)
	}
	groupCode(t, f.request("GET", "/v1/conversations?requestId="+request, "", token, ""), 401, "AUTH_TOKEN_EXPIRED")
	if _, _, _, _, err = f.s.newSession(context.Background(), f.users[1], clientInput{ClientType: "WEB", DeviceID: "replacement"}); err != nil {
		t.Fatal(err)
	}
	groupCode(t, f.request("POST", "/v1/groups/"+original.ConversationID+"/members", groupBody(t, groupRequest{request, []string{f.users[0]}}), f.tokens[1], "application/json"), 401, "AUTH_SESSION_EPOCH_STALE")
}
