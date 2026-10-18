# ⚡ Ripple OS: Autonomous Socio-Technical Resilience Engine

> **Predictive chaos engineering, multi-agent coordination, and blast radius simulation powered by FalkorDB multigraph sandboxing and GraphBLAS linear algebra.**

Built for **Graph Hacks: Give Your AI Agents Real Context**, hosted by WeMakeDevs and FalkorDB.

---

## 🎯 Target Tracks

* 🧠 **Track 3: Company Brain (Primary):** Models a 6-layer enterprise knowledge topology connecting $27.7M in Customer SLAs, Microservice meshes, Cloud infrastructure, Third-party vendors, Architecture Decision Records (ADRs), and Staff ownership.
* 🤖 **Track 2: Agent Memory & Coordination:** Implements asynchronous multi-agent coordination and cross-session state handoffs strictly through persistent FalkorDB `(:AgentHandoffMemory)` and `(:AgentMemory)` graph nodes.
* 🕵️ **Track 1: Agents That Act on Connected Data:** Replaces speculative LLM generation with deterministic GraphBLAS linear algebra procedures (`CALL algo.pageRank`, `CALL algo.WCC`) and multi-hop Cypher traversals.

---

## 📌 Problem: The Blind Spot of Vector RAG

When a senior staff architect resigns or a microservice experiences transient packet loss, traditional Vector RAG systems fail:
* **Vector similarity cannot compute topological causality:** Embedding the phrase *"Alex leaves the company"* returns Alex's resume, HR files, or recent pull requests. It has near-zero cosine similarity with *"Acme Retail $50,000/hr SLA default"*.
* **The Reality:** Alex is the sole knowledge owner for the `PCI-DSS-4.0-Audit` and `Stripe-v3-Migration` epics. These initiatives directly govern `payments-engine`, which is a synchronous dependency for `checkout-orchestrator`, which is bound by a **$14,000,000 ARR contract** with Acme Global Retail.
* **The Solution:** What takes recursive SQL joins or document embeddings minutes of guessing is resolved in **1.4 milliseconds as a 5-hop Cypher traversal in FalkorDB**.

---

## 🏗️ Enterprise Graph Data Model (38 Nodes / 72 Edges)

Ripple OS models the organization across six interconnected layers:

```text
[Tier-1 Customer Contracts (SLAs)]
│
│ [:COVERS_SLA]
▼
[Edge API Gateways]
│
│ [:ROUTES_TO]
▼
[Core Microservices] ────────[:DEPENDS_ON*1..4]────────▶ [Cloud Infrastructure]
│          │                                                  │
│          │ [:INTEGRATES_WITH]                               │ [:HOSTED_ON]
▼          ▼                                                  ▼
[Personnel] [Third-Party SaaS]                              [Kafka / Aurora / Redis]
│          │
│          │ [:BLOCKS]
▼          ▼
[Strategic Epics & Compliance] ──[:DOCUMENTED_IN]──▶ [Architecture Decision Records (ADRs)]
```

### Node Types & Properties
- `(:CustomerContract)`: `name`, `arr`, `penalty_per_hr`, `tier`
- `(:Service)`: `name`, `tier`, `lang`, `rev_exposure_per_hr`
- `(:CloudResource)`: `name`, `provider`, `region`, `tier`
- `(:Vendor)`: `name`, `vendor`, `reliability_sla`
- `(:Epic)`: `name`, `deadline_days`, `regulatory_fine`, `risk`
- `(:Person)`: `name`, `role`, `timezone`, `cost_per_hr`
- `(:Document)`: `id`, `title`, `url`, `sha`, `sign_off_date`
- `(:AgentHandoffMemory)`: `ticket_id`, `from_agent`, `to_agent`, `status`, `target_departed`, `created_at`
- `(:AgentMemory)`: `id`, `incident_type`, `mitigated_target`, `successor_assigned`, `status`, `resolved_at`

---

## ⚡ Core FalkorDB Capabilities Leveraged

### 1. Zero-Pollution Multigraph Sandboxing
Live-fire chaos testing on production graphs is dangerous. Rather than provisioning separate database instances, Ripple OS uses FalkorDB's native multigraph topology:
```python
# Creates an in-memory clone sandbox in <4ms
sandbox_id = f"sim_{uuid.uuid4().hex[:8]}"
dst = db.select_graph(sandbox_id)
# Executes destructive failure simulations, then reaps cleanly:
dst.delete()
```

### 2. GraphBLAS Matrix Algorithms as MCP Tools
Instead of asking an LLM to guess incident leadership, Ripple OS executes FalkorDB's native linear algebra procedures:

```cypher
// Algorithmic Succession via GraphBLAS PageRank
CALL algo.pageRank('Person', 'COLLABORATES_WITH')
YIELD node, score
RETURN node.name AS candidate, score
ORDER BY score DESC
LIMIT 3;
```

```cypher
// Organizational Partition Detection via Weakly Connected Components
CALL algo.WCC(null)
YIELD node, componentId
RETURN componentId, collect(node.name) AS isolated_cluster;
```

### 3. Causal Multi-Hop Blast Radius Traversals
```cypher
// Tracing SLA default exposures up to 4 hops deep
MATCH path = (c:CustomerContract)-[:COVERS_SLA]->(s1:Service)-[:DEPENDS_ON*1..3]->(s2:Service {name: $failed_service})
RETURN DISTINCT c.name AS customer, c.penalty_per_hr AS penalty, [n IN nodes(path) | n.name] AS causal_chain;
```

### 4. Persistent Multi-Agent State Handoff (Track 2)
Two autonomous agents coordinate without a centralized queue by writing state directly into FalkorDB:
- **Agent 1 (TriageSentinel):** Detects fractures, queries MCP graph tools, and commits an `(:AgentHandoffMemory)` node with status `TRIAGED_PENDING_RECOVERY`.
- **Agent 2 (RemediationGovernor):** Operates in an isolated thread, queries FalkorDB for active tickets, mutates ownership edges, and updates status to `REMEDIATION_COMMITTED`.

---

## 🚀 Quickstart & Reproduction

**Prerequisites**
- Docker installed and running
- Python 3.10+
- A Gemini API key (or OpenAI API key)

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/ripple-os.git
cd ripple-os
```

### 2. Start FalkorDB Container
Start FalkorDB with the visual browser enabled on port 3000:
```bash
docker run -d -p 6379:6379 -p 3000:3000 --name falkordb-mesh falkordb/falkordb:latest
```

### 3. Set Up Environment
```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `.env` file in the project root (you can use `.env.example` as a template):
```env
# Gemini API Key (Required for AI Synthesis)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# FalkorDB Connection Settings
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
```

### 5. Seed the Enterprise Graph Topology
Populate the 38-node / 72-edge baseline graph into FalkorDB:
```bash
python -m core.seed
```
*(Verify by visiting `http://localhost:3000` to inspect the live FalkorDB browser UI).*

### 6. Launch Ripple OS
```bash
python run.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Adversarial Stress Testing
Ripple OS includes an automated test suite designed to evaluate cycles, edge dropouts, and multi-node attrition in isolated scratch sandboxes without altering production state:
```bash
python -m tests.break_tests
```

**Test Coverage:**
1. **Cyclic Dependency Resolution:** Proves variable-length Cypher traversals bounded to `*1..4` terminate cleanly in deadlock loops without stack overflow.
2. **Entity Injection Resilience:** Tests handling of non-existent entity targets without agent crashes.
3. **Multi-Node Decapitation:** Simulates simultaneous attrition of primary and secondary leads; verifies GraphBLAS PageRank stability on degraded subgraphs.
4. **Network Partition Detection:** Validates `CALL algo.WCC()` component isolation flags under edge severance.
5. **Sandbox Churn & Key Isolation:** Concurrently creates and reaps 5 ephemeral tenant sandboxes with zero key leaks.

---

## 📂 Repository Layout
```plaintext
ripple/
├── .env.example               # Environment template
├── .gitignore                 # Strict ignore rules
├── requirements.txt           # Verified dependencies
├── README.md                  # System documentation
├── run.py                     # Application runner
├── core/
│   ├── database.py            # FalkorDB client manager & connection pool
│   ├── seed.py                # 38-node / 72-edge multi-layer enterprise graph
│   └── simulation.py          # Multigraph sandboxing & GraphBLAS algorithms
├── agents/
│   ├── mcp_tools.py           # Model Context Protocol (MCP) graph tool catalogue
│   ├── multi_agent_mesh.py    # Track 2 asynchronous agent handoff engine
│   └── resilience_agent.py    # Reasoning engine & executive incident synthesizer
├── tests/
│   └── break_tests.py         # Zero-leakage adversarial stress suite
└── ui/
    ├── app.py                 # Streamlit executive control center
    └── styles.py              # Dark theme styling & typography
```

---

## ⚖️ License
Apache License 2.0. Distributed as open source for the WeMakeDevs & FalkorDB Hackathon.