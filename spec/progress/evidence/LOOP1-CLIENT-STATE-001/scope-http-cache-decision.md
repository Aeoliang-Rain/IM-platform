# Minimal scope decision: real Web/Go authentication

BLOCKED_BY_TASK_SCOPE (Web actual acceptance only). Task allowed_paths does not include `clients/web/src/application/http.ts`; no edit made.

Actual new Chromium/default TLS and actual Go project im-gui-product-20261004-35588: `/v1/auth/login` responds 200 application/json with canonical WEB ACTIVE session and HTTP_ONLY_SECURE_COOKIE token delivery, no Cache-Control header. Web Http rejects before auth parsing because its generic HTTP response condition requires no-store. Canonical auth-user-friend.openapi.json contains no no-store response requirement; sync.openapi.json requires it and SyncHttp independently enforces it. Relay forwards headers unchanged. Prior page module MIME failure was repaired in test relay; original browser-initial-failure.png is preliminary, not acceptance.

Requested additional allowed_path: `clients/web/src/application/http.ts` only.

Proposed minimal diff:
```diff
- if(r.redirected||!/^application\/json(?:\s*;|$)/i.test(r.headers.get('content-type')??'')||r.headers.get('cache-control')!=='no-store')return invalid();
+ if(r.redirected||!/^application\/json(?:\s*;|$)/i.test(r.headers.get('content-type')??''))return invalid();
```

Keep fetch cache:no-store, secure origin, same-origin credentials, redirect:error, strict canonical parser, streaming budget/UTF8 and SyncHttp's contractual response cache validation. Tests: real Go auth positive, generic HTTP valid JSON absent-cache positive; redirect/nonJSON/malformed/oversize negative; Sync user/conversation missing/no-cache response remains rejected without cursor/row advancement; existing full Web behavior/logout checks. No server/public contract/security boundary amendment.
