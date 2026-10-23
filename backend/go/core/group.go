package core

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"mime"
	"net/http"
	"net/url"
	"regexp"
	"slices"
	"sort"
	"strconv"
	"time"
	"unicode/utf8"

	"github.com/jackc/pgx/v5"
)

var groupID = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

type groupRequest struct {
	RequestID string   `json:"requestId"`
	Members   []string `json:"memberUserIds"`
}
type groupResult struct {
	RequestID      string    `json:"requestId"`
	ConversationID string    `json:"conversationId"`
	Added          []string  `json:"addedMemberUserIds"`
	CreatedAt      time.Time `json:"createdAt"`
}
type groupUser struct {
	UserID      string `json:"userId"`
	Username    string `json:"username"`
	DisplayName string `json:"displayName"`
}
type groupMember struct {
	User     groupUser `json:"user"`
	Role     string    `json:"role"`
	JoinedAt time.Time `json:"joinedAt"`
}
type groupRow struct {
	ConversationID string      `json:"conversationId"`
	Kind           string      `json:"kind"`
	CreatedBy      string      `json:"createdBy"`
	CreatedAt      time.Time   `json:"createdAt"`
	Member         groupMember `json:"member"`
}
type groupContinuation struct {
	Conversation string `json:"afterConversationId"`
	Member       string `json:"afterMemberUserId"`
}
type groupPage struct {
	RequestID string            `json:"requestId"`
	Items     []groupRow        `json:"items"`
	HasMore   bool              `json:"hasMore"`
	Next      groupContinuation `json:"next"`
}

func groupJSON(w http.ResponseWriter, status int, value any) {
	body, err := json.Marshal(value)
	if err != nil {
		panic(err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	body = append(body, '\n')
	n, err := w.Write(body)
	if err != nil {
		panic(err)
	}
	if n != len(body) {
		panic(io.ErrShortWrite)
	}
}

func groupFailure(w http.ResponseWriter, id string, err error) {
	// Only a direct canonical rejection is classified. In particular a joined
	// rejection + rollback failure must propagate both causes as server failure.
	e, ok := err.(apiError)
	if ok {
		valid := e.Status == 400 && e.Code == "VALIDATION_FAILED" ||
			e.Status == 403 && e.Code == "AUTHORIZATION_DENIED" ||
			e.Status == 409 && e.Code == "GROUP_REQUEST_CONFLICT"
		if e.Status == 401 {
			switch e.Code {
			case "AUTH_REQUIRED", "AUTH_TOKEN_INVALID", "AUTH_TOKEN_EXPIRED", "AUTH_SESSION_REVOKED", "AUTH_SESSION_EPOCH_STALE", "AUTH_CLIENT_TYPE_MISMATCH":
				valid = true
			}
		}
		if valid {
			groupJSON(w, e.Status, map[string]any{"requestId": id, "error": map[string]string{"code": e.Code, "message": e.Message}})
			return
		}
	}
	panic(err)
}

func groupInvalid() error { return fail(400, "VALIDATION_FAILED", "Group request is invalid.") }
func groupDenied() error  { return fail(403, "AUTHORIZATION_DENIED", "Group access is denied.") }

// Decode one bounded JSON object without accepting duplicate keys. Non-object
// JSON remains a shape error checked after authentication.
func groupObject(body []byte) (map[string]json.RawMessage, error) {
	if !utf8.Valid(body) || !json.Valid(body) {
		return nil, groupInvalid()
	}
	d := json.NewDecoder(bytes.NewReader(body))
	d.UseNumber()
	first, err := d.Token()
	if err != nil {
		return nil, err
	}
	if first != json.Delim('{') {
		return nil, nil
	}
	fields := make(map[string]json.RawMessage)
	for d.More() {
		key, err := d.Token()
		if err != nil {
			return nil, err
		}
		name := key.(string)
		if _, exists := fields[name]; exists {
			return nil, groupInvalid()
		}
		var value json.RawMessage
		if err = d.Decode(&value); err != nil {
			return nil, err
		}
		fields[name] = value
	}
	if _, err = d.Token(); err != nil {
		return nil, err
	}
	return fields, nil
}

func (s *authService) mutateGroup(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Cache-Control", "no-store")
	id, err := uuid()
	if err != nil {
		panic(err)
	}
	reject := func(err error) { groupFailure(w, id, err) }
	media, _, mediaErr := mime.ParseMediaType(r.Header.Get("Content-Type"))
	body, err := io.ReadAll(io.LimitReader(r.Body, 16385))
	if err != nil {
		reject(err)
		return
	}
	fields, err := groupObject(body)
	if fields != nil {
		var candidate string
		if json.Unmarshal(fields["requestId"], &candidate) == nil && groupID.MatchString(candidate) {
			id = candidate
		}
	}
	if r.URL.RawQuery != "" || r.URL.ForceQuery || mediaErr != nil || media != "application/json" || len(body) > 16384 {
		reject(groupInvalid())
		return
	}
	if err != nil {
		reject(err)
		return
	}
	token, err := bearer(r)
	if err != nil {
		reject(err)
		return
	}
	c, err := s.authenticate(r.Context(), token)
	if err != nil {
		reject(err)
		return
	}
	var input groupRequest
	if len(fields) != 2 || fields["requestId"] == nil || fields["memberUserIds"] == nil ||
		json.Unmarshal(fields["requestId"], &input.RequestID) != nil || !groupID.MatchString(input.RequestID) ||
		json.Unmarshal(fields["memberUserIds"], &input.Members) != nil || len(input.Members) < 1 || len(input.Members) > 100 {
		reject(groupInvalid())
		return
	}
	for _, member := range input.Members {
		if !groupID.MatchString(member) || member == c.UserID {
			reject(groupInvalid())
			return
		}
	}
	sort.Strings(input.Members)
	input.Members = slices.Compact(input.Members)
	conversation := r.PathValue("conversationId")
	if r.Pattern == "POST /v1/groups/{conversationId}/members" && !groupID.MatchString(conversation) {
		reject(groupInvalid())
		return
	}
	result, err := s.changeGroup(r.Context(), token, c, input, conversation)
	if err != nil {
		reject(err)
		return
	}
	status := 200
	if conversation == "" {
		status = 201
	}
	groupJSON(w, status, result)
}

func groupRollback(ctx context.Context, tx pgx.Tx, result *error) {
	cleanup, cancel := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
	defer cancel()
	if err := tx.Rollback(cleanup); err != nil && !errors.Is(err, pgx.ErrTxClosed) {
		*result = errors.Join(*result, err)
	}
}

func groupMembers(ctx context.Context, tx pgx.Tx, conversation string) ([]string, error) {
	rows, err := tx.Query(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL ORDER BY user_id`, conversation)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	ids := make([]string, 0)
	for rows.Next() {
		var id string
		if err = rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	return ids, rows.Err()
}

func (s *authService) groupSession(ctx context.Context, tx pgx.Tx, token string, c claims) error {
	var locked string
	err := tx.QueryRow(ctx, `SELECT session_id FROM sessions WHERE user_id=$1 AND client_type=$2 FOR SHARE`, c.UserID, c.ClientType).Scan(&locked)
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		return err
	}
	_, err = s.syncAuthenticate(ctx, tx, token)
	return err
}

func (s *authService) changeGroup(ctx context.Context, token string, c claims, input groupRequest, conversation string) (groupResult, error) {
	for {
		result, again, err := s.groupAttempt(ctx, token, c, input, conversation)
		if err != nil || !again {
			return result, err
		}
		// A newly committed member requires another earlier user lock. No writes
		// happened in this attempt; rollback before acquiring the new sorted set.
	}
}

func (s *authService) groupAttempt(ctx context.Context, token string, c claims, input groupRequest, conversation string) (result groupResult, again bool, err error) {
	tx, err := s.db.Begin(ctx)
	if err != nil {
		return result, false, err
	}
	defer groupRollback(ctx, tx, &err)
	users := append([]string{c.UserID}, input.Members...)
	if conversation != "" {
		var members []string
		members, err = groupMembers(ctx, tx, conversation)
		if err != nil {
			return
		}
		users = append(users, members...)
	}
	sort.Strings(users)
	users = slices.Compact(users)
	for _, user := range users {
		var locked string
		// NO KEY UPDATE serializes producers and blocks UserSync SHARE, while
		// permitting the FK KEY SHARE needed by an existing send/logout holder.
		err = tx.QueryRow(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR NO KEY UPDATE`, user).Scan(&locked)
		if errors.Is(err, pgx.ErrNoRows) {
			err = groupDenied()
			return
		}
		if err != nil {
			return
		}
	}
	if err = s.groupSession(ctx, tx, token, c); err != nil {
		return
	}
	operation := "CREATE"
	if conversation != "" {
		operation = "ADD"
		var member, kind string
		err = tx.QueryRow(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND user_id=$2 AND left_at IS NULL FOR SHARE`, conversation, c.UserID).Scan(&member)
		if errors.Is(err, pgx.ErrNoRows) {
			err = groupDenied()
			return
		}
		if err != nil {
			return
		}
		err = tx.QueryRow(ctx, `SELECT kind FROM conversations WHERE conversation_id=$1 FOR UPDATE`, conversation).Scan(&kind)
		if errors.Is(err, pgx.ErrNoRows) {
			err = groupDenied()
			return
		}
		if err != nil {
			return
		}
		if kind != "GROUP" {
			err = groupDenied()
			return
		}
		var current []string
		current, err = groupMembers(ctx, tx, conversation)
		if err != nil {
			return
		}
		for _, user := range current {
			if !slices.Contains(users, user) {
				again = true
				return
			}
		}
	}
	for _, target := range input.Members {
		low, high := pair(c.UserID, target)
		var friend bool
		err = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM friendships WHERE user_low_id=$1 AND user_high_id=$2)`, low, high).Scan(&friend)
		if err != nil {
			return
		}
		if !friend {
			err = groupDenied()
			return
		}
	}
	var targets []string
	result.RequestID = input.RequestID
	query := `SELECT conversation_id,target_user_ids::text[],added_member_user_ids::text[],created_at FROM group_operation_receipts WHERE actor_id=$1 AND operation=$2 AND request_id=$3`
	args := []any{c.UserID, operation, input.RequestID}
	if operation == "ADD" {
		query += ` AND conversation_id=$4`
		args = append(args, conversation)
	}
	err = tx.QueryRow(ctx, query, args...).Scan(&result.ConversationID, &targets, &result.Added, &result.CreatedAt)
	hasReceipt := err == nil
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		return
	}
	err = nil
	if operation == "CREATE" {
		var existing string
		lookup := tx.QueryRow(ctx, `SELECT conversation_id FROM conversations WHERE created_by=$1 AND group_create_request_id=$2`, c.UserID, input.RequestID).Scan(&existing)
		if lookup != nil && !errors.Is(lookup, pgx.ErrNoRows) {
			err = lookup
			return
		}
		if lookup == nil && !hasReceipt {
			err = errors.New("persisted-original-group-result-missing")
			return
		}
		if hasReceipt && (lookup != nil || existing != result.ConversationID) {
			err = errors.New("inconsistent persisted group create identity")
			return
		}
	}
	if hasReceipt {
		if !slices.Equal(targets, input.Members) {
			err = fail(409, "GROUP_REQUEST_CONFLICT", "Group request identity has different targets.")
			return
		}
		if err = s.groupSession(ctx, tx, token, c); err != nil {
			return
		}
		err = tx.Commit(ctx)
		return
	}
	result.ConversationID = conversation
	result.Added = make([]string, 0)
	if operation == "CREATE" {
		result.ConversationID, err = uuid()
		if err != nil {
			return
		}
		_, err = tx.Exec(ctx, `INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES($1,'GROUP',$2,$3)`, result.ConversationID, c.UserID, input.RequestID)
		if err != nil {
			return
		}
		_, err = tx.Exec(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'OWNER')`, result.ConversationID, c.UserID)
		if err != nil {
			return
		}
		result.Added = append(result.Added, c.UserID)
	}
	for _, user := range input.Members {
		var added string
		err = tx.QueryRow(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'MEMBER') ON CONFLICT(conversation_id,user_id) DO UPDATE SET left_at=NULL WHERE conversation_members.left_at IS NOT NULL RETURNING user_id`, result.ConversationID, user).Scan(&added)
		if errors.Is(err, pgx.ErrNoRows) {
			err = nil
			continue
		}
		if err != nil {
			return
		}
		result.Added = append(result.Added, added)
	}
	sort.Strings(result.Added)
	err = tx.QueryRow(ctx, `INSERT INTO group_operation_receipts(actor_id,operation,request_id,conversation_id,target_user_ids,added_member_user_ids) VALUES($1,$2,$3,$4,$5::uuid[],$6::uuid[]) RETURNING created_at`, c.UserID, operation, input.RequestID, result.ConversationID, input.Members, result.Added).Scan(&result.CreatedAt)
	if err != nil {
		return
	}
	if len(result.Added) > 0 {
		var recipients []string
		recipients, err = groupMembers(ctx, tx, result.ConversationID)
		if err != nil {
			return
		}
		for _, user := range recipients {
			for _, kind := range []string{"conversation.changed", "membership.changed"} {
				if err = writeUserStateEvent(ctx, tx, user, kind, result.ConversationID, true); err != nil {
					return
				}
			}
		}
	}
	if err = s.groupSession(ctx, tx, token, c); err != nil {
		return
	}
	err = tx.Commit(ctx)
	return
}

func (s *authService) listConversations(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Cache-Control", "no-store")
	id, err := uuid()
	if err != nil {
		panic(err)
	}
	query, parseErr := url.ParseQuery(r.URL.RawQuery)
	if values := query["requestId"]; len(values) == 1 && groupID.MatchString(values[0]) {
		id = values[0]
	}
	reject := func(err error) { groupFailure(w, id, err) }
	if parseErr != nil {
		reject(groupInvalid())
		return
	}
	for key, values := range query {
		if len(values) != 1 || key != "requestId" && key != "limit" && key != "afterConversationId" && key != "afterMemberUserId" {
			reject(groupInvalid())
			return
		}
	}
	body, err := io.ReadAll(io.LimitReader(r.Body, 1))
	if err != nil {
		reject(err)
		return
	}
	if len(body) != 0 {
		reject(groupInvalid())
		return
	}
	token, err := bearer(r)
	if err != nil {
		reject(err)
		return
	}
	c, err := s.authenticate(r.Context(), token)
	if err != nil {
		reject(err)
		return
	}
	limit := 100
	if raw, exists := query["limit"]; exists {
		limit, err = strconv.Atoi(raw[0])
		if err != nil || limit < 1 || limit > 100 || strconv.Itoa(limit) != raw[0] {
			reject(groupInvalid())
			return
		}
	}
	after := groupContinuation{Conversation: query.Get("afterConversationId"), Member: query.Get("afterMemberUserId")}
	_, first := query["afterConversationId"]
	_, second := query["afterMemberUserId"]
	if !groupID.MatchString(query.Get("requestId")) || first != second || first && (!groupID.MatchString(after.Conversation) || !groupID.MatchString(after.Member)) {
		reject(groupInvalid())
		return
	}
	page, err := s.conversationPage(r.Context(), token, c, id, limit, after)
	if err != nil {
		reject(err)
		return
	}
	groupJSON(w, 200, page)
}

func (s *authService) conversationPage(ctx context.Context, token string, c claims, id string, limit int, after groupContinuation) (page groupPage, err error) {
	tx, err := s.db.Begin(ctx)
	if err != nil {
		return
	}
	defer groupRollback(ctx, tx, &err)
	var locked string
	if err = tx.QueryRow(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR SHARE`, c.UserID).Scan(&locked); err != nil {
		return
	}
	if err = s.groupSession(ctx, tx, token, c); err != nil {
		return
	}
	query := `SELECT c.conversation_id,c.kind,c.created_by,c.created_at,u.user_id,u.username,u.display_name,m.role,m.joined_at FROM conversations c JOIN conversation_members own ON own.conversation_id=c.conversation_id AND own.user_id=$1 AND own.left_at IS NULL JOIN conversation_members m ON m.conversation_id=c.conversation_id AND m.left_at IS NULL JOIN users u ON u.user_id=m.user_id`
	args := []any{c.UserID, limit + 1}
	if after.Conversation != "" {
		query += ` WHERE (c.conversation_id,m.user_id)>($3::uuid,$4::uuid)`
		args = append(args, after.Conversation, after.Member)
	}
	query += ` ORDER BY c.conversation_id,m.user_id LIMIT $2`
	rows, err := tx.Query(ctx, query, args...)
	if err != nil {
		return
	}
	page = groupPage{RequestID: id, Items: make([]groupRow, 0)}
	for rows.Next() {
		var row groupRow
		if err = rows.Scan(&row.ConversationID, &row.Kind, &row.CreatedBy, &row.CreatedAt, &row.Member.User.UserID, &row.Member.User.Username, &row.Member.User.DisplayName, &row.Member.Role, &row.Member.JoinedAt); err != nil {
			break
		}
		page.Items = append(page.Items, row)
	}
	if err == nil {
		err = rows.Err()
	}
	rows.Close()
	if err != nil {
		return
	}
	if err = s.groupSession(ctx, tx, token, c); err != nil {
		return
	}
	if err = tx.Commit(ctx); err != nil {
		return
	}
	page.HasMore = len(page.Items) > limit
	if page.HasMore {
		page.Items = page.Items[:limit]
		last := page.Items[len(page.Items)-1]
		page.Next = groupContinuation{last.ConversationID, last.Member.User.UserID}
	}
	return
}
