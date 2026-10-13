from pathlib import Path
import re,json
r=Path('H:/.codex/worktrees/err/IM-platform')
p=(r/'spec/architecture/frozen-architecture.md').read_text(encoding='utf8')
lines=p.splitlines(); show=False
for line in lines:
 if re.match(r'^## ',line):show=any(line.startswith('## '+str(n)+'.') for n in [3,10,11,12])
 if re.match(r'^### ',line) and line.startswith(('### 2.3','### 6.1')):show=True
 if re.match(r'^### ',line) and line.startswith(('### 2.4','### 6.2')):show=False
 if show:print(line)
print((r/'spec/governance/error-handling.md').read_text(encoding='utf8'))
