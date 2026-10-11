# Exact temporary CA Machine rollback proposal

Pending explicit Human permission. Read-only evidence proves the approved week2 CA is physically in LocalMachine Root: exact thumb `727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C`, DER SHA256 `a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5`, expires2026-10-17T08:58:07Z. Its exact HKLM key exists; HKCU key is absent. The same-target CurrentUser logical view is preserved74 plus this inherited CA=75. Original permission named CurrentUser only, so Machine removal requires this specific additional decision. Microsoft documents that CurrentUser logical Root inherits Machine Root: https://learn.microsoft.com/en-us/windows-hardware/drivers/install/local-machine-and-current-user-certificate-stores.

The private complete Machine snapshot immediately before proposed removal is hashed/count-bound in the adjacent JSON. The Machine snapshot before manual import is unavailable. The expected Machine after set is this actual current set minus only the exact approved thumb; CurrentUser after must equal its preserved original74 full set.

Minimal standard command, executed in a normal administrator-authorized Windows context only after permission:

`certutil.exe -f -delstore Root 727E5D6BB4D072F9A76BFBC8FA81A6159A047D5C`

Record actual command/exit and precisely owned confirmation if emitted. Verify exact full-set differences, ownCA absent and HKCU untouched. Then capture fresh default native TLS rejection with live explicitCA200 positive control and independently complete owned resource/AVD restoration. Do not delete other same-name certificates, add trust, modify registry/ACL/security policy/global preferences or operate unrelated processes. No mutation has been performed under this proposal.
