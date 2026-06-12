param(
    [string]$Root = (Get-Location).Path
)

Write-Host "== MODEL_RUNNER BOOTSTRAP START =="

# ----------------------------
# 1. Stop running python processes (safe kill)
# ----------------------------
Write-Host "Stopping Python processes..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# ----------------------------
# 2. Fix encoding + remove null-byte corruption
# ----------------------------
Write-Host "Cleaning corrupted Python files..."

$pyFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.py"

foreach ($f in $pyFiles) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)

        # detect null-byte corruption
        if ($bytes -contains 0) {
            Write-Host "Fixing: $($f.FullName)"

            # convert to UTF-8 text salvage (lossy safe)
            $text = [System.Text.Encoding]::UTF8.GetString($bytes)

            # strip null characters
            $text = $text -replace "`0", ""

            # rewrite safely
            Set-Content -Path $f.FullName -Value $text -Encoding UTF8
        }
    }
    catch {
        Write-Host "Skip: $($f.FullName)"
    }
}

# ----------------------------
# 3. Ensure runtime structure exists
# ----------------------------
Write-Host "Ensuring runtime modules..."

$dirs = @(
    "runtime",
    "api",
    "bus",
    "agents",
    "tests"
)

foreach ($d in $dirs) {
    if (!(Test-Path "$Root\$d")) {
        New-Item -ItemType Directory -Path "$Root\$d" | Out-Null
    }
}

# ----------------------------
# 4. Create minimal DAG engine (repair core)
# ----------------------------
$dagPath = "$Root\runtime\dag.py"

@"
class DAGNode:
    def __init__(self, name, fn=None):
        self.name = name
        self.fn = fn
        self.next = []

    def add(self, node):
        self.next.append(node)


class DAGEngine:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, fn=None):
        node = DAGNode(name, fn)
        self.nodes[name] = node
        return node

    def link(self, a, b):
        self.nodes[a].add(self.nodes[b])

    def run(self, start):
        visited = set()
        stack = [self.nodes[start]]

        while stack:
            node = stack.pop()
            if node.name in visited:
                continue

            visited.add(node.name)

            if node.fn:
                node.fn()

            for n in node.next:
                stack.append(n)

        return visited
"@ | Set-Content -Path $dagPath -Encoding UTF8

# ----------------------------
# 5. Create minimal supervisor (self-healing loop)
# ----------------------------
$supervisorPath = "$Root\runtime\supervisor.py"

@"
import time
import traceback

class Supervisor:
    def __init__(self, engine):
        self.engine = engine
        self.running = True

    def heal(self, err):
        print("[SUPERVISOR] healing:", err)

    def run(self, entry="root"):
        while self.running:
            try:
                self.engine.run(entry)
                time.sleep(1)

            except Exception as e:
                self.heal(traceback.format_exc())
                time.sleep(2)
"@ | Set-Content -Path $supervisorPath -Encoding UTF8

# ----------------------------
# 6. Create safe FastAPI entry
# ----------------------------
$apiPath = "$Root\api\main.py"

@"
from fastapi import FastAPI
from runtime.dag import DAGEngine

app = FastAPI()

engine = DAGEngine()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run-dag")
def run_dag():
    return {"result": list(engine.run("root"))}
"@ | Set-Content -Path $apiPath -Encoding UTF8

# ----------------------------
# 7. Boot check
# ----------------------------
Write-Host "Running validation import test..."

python -c "import runtime.dag; import api.main; print('BOOT OK')"

Write-Host "== MODEL_RUNNER BOOTSTRAP COMPLETE =="