-- Only with writers stopped and the release backup/retry-window assessment.
-- Business/group/member/event rows from 0001 are deliberately preserved.
DROP TABLE group_operation_receipts;
DROP FUNCTION group_operation_ids_canonical(uuid[]);
