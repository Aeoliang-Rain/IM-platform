-- Original targets/results cannot be reconstructed from changing membership.
CREATE FUNCTION group_operation_ids_canonical(ids uuid[]) RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT AS $$
    SELECT array_position(ids, NULL) IS NULL
       AND ids = ARRAY(SELECT DISTINCT id FROM unnest(ids) AS id ORDER BY id)
$$;

CREATE TABLE group_operation_receipts (
    actor_id uuid NOT NULL REFERENCES users(user_id),
    operation text NOT NULL CHECK (operation IN ('CREATE', 'ADD')),
    request_id uuid NOT NULL,
    conversation_id uuid NOT NULL REFERENCES conversations(conversation_id),
    target_user_ids uuid[] NOT NULL,
    added_member_user_ids uuid[] NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (actor_id, operation, conversation_id, request_id),
    CHECK (cardinality(target_user_ids) BETWEEN 1 AND 100),
    CHECK (group_operation_ids_canonical(target_user_ids)),
    CHECK (NOT actor_id = ANY(target_user_ids)),
    CHECK (cardinality(added_member_user_ids) <= 101),
    CHECK (group_operation_ids_canonical(added_member_user_ids)),
    CHECK ((operation = 'ADD' AND added_member_user_ids <@ target_user_ids)
        OR (operation = 'CREATE'
            AND added_member_user_ids @> target_user_ids
            AND added_member_user_ids @> ARRAY[actor_id]
            AND cardinality(added_member_user_ids) = cardinality(target_user_ids) + 1))
);
CREATE UNIQUE INDEX group_create_receipt_identity
    ON group_operation_receipts(actor_id, request_id) WHERE operation = 'CREATE';
-- conversations(created_by,group_create_request_id) and membership PK remain.
-- Core verifies GROUP/current Session/member/friends and CREATE conversation
-- identity, and commits receipt, business rows, all user events and Outbox once.
