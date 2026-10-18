import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import pandas as pd
from core.simulation import SimulationEngine
from agents.resilience_agent import ResilienceAgent
from ui.styles import APP_CSS

st.set_page_config(
    page_title="Ripple OS | Socio-Technical Resilience",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

st.markdown(APP_CSS, unsafe_allow_html=True)

# Shared Session Engine Connection
if "engine" not in st.session_state:
    st.session_state.engine = SimulationEngine()
if "agent" not in st.session_state:
    st.session_state.agent = ResilienceAgent(engine=st.session_state.engine)
if "last_sim" not in st.session_state:
    st.session_state.last_sim = None
if "healing_done" not in st.session_state:
    st.session_state.healing_done = None

engine = st.session_state.engine
agent = st.session_state.agent

# Executive Topbar Navigation
st.markdown("""
<div class='exec-topbar'>
    <div>
        <div class='brand-title'>RIPPLE <span>OS</span></div>
        <div class='brand-subtitle'>Autonomous Socio-Technical Resilience Engine</div>
    </div>
    <div style='display: flex; gap: 12px; align-items: center;'>
        <div class='stat-pill'>
            <span class='stat-pill-label'>Monitored ARR</span>
            <span class='stat-pill-val' style='color:#38bdf8;'>$27,700,000</span>
        </div>
        <div class='stat-pill'>
            <span class='stat-pill-label'>Topology Mesh</span>
            <span class='stat-pill-val' style='color:#a855f7;'>38 Nodes / 72 Edges</span>
        </div>
        <div class='stat-pill'>
            <span class='stat-pill-label'>Engine Status</span>
            <span class='stat-pill-val' style='color:#10b981;'>● ONLINE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown("<div style='font-size:12px; font-weight:800; color:#64748b; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px;'>SIMULATION SETUP</div>", unsafe_allow_html=True)

    mode = st.segmented_control(
        "Simulation Mode",
        ["Staff Attrition", "Service Outage"],
        default="Staff Attrition"
    )

    if mode == "Staff Attrition":
        target = st.selectbox(
            "Select Staff Target (SPOF)",
            ["Alex", "Sarah", "Elena", "Marcus", "Chen", "David", "Priya", "Zoe"],
            index=0
        )
        temporal_days = st.slider("Temporal Horizon (Days Out)", min_value=0, max_value=60, value=14, step=7)
        trigger_btn = st.button("⚡ EXECUTE CHAOS SIMULATION", type="primary", use_container_width=True)
    else:
        target = st.selectbox(
            "Select Core Service",
            [
                "payments-engine",
                "checkout-orchestrator",
                "identity-mesh",
                "orders-service",
                "fraud-detection-engine",
                "notification-dispatcher",
                "ledger-reconciler",
                "edge-api-gateway"
            ],
            index=0
        )
        temporal_days = 0
        trigger_btn = st.button("🔥 SIMULATE SEV-1 OUTAGE", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#64748b; line-height:1.6;'>
        <b>FALKORDB ENGINE STRENGTHS:</b><br>
        • <b>Multigraph Sandboxing:</b> Zero production data pollution.<br>
        • <b>Linear Algebra Kernels:</b> <code>CALL algo.pageRank()</code> & <code>algo.WCC()</code>.<br>
        • <b>Multi-Hop Cypher:</b> Real causality over vector guessing.
    </div>
    """, unsafe_allow_html=True)

# Interactive Topology Visualizer
def render_graph_view(highlights=None):
    highlights = highlights or {}
    nodes, edges = engine.get_graph_data("company_prod")
    net = Network(height="520px", width="100%", bgcolor="#0a0f1d", font_color="#cbd5e1")

    for n_id, label, name, props in nodes:
        props = props or {}

        if label == "CustomerContract":
            color = "#a855f7"
            size = 24
            tooltip = f"🏢 Customer Contract: {name}\nARR: ${props.get('arr', 0):,}\nPenalty:${props.get('penalty_per_hr', 0):,}/hr"
        elif label == "Service":
            color = "#0284c7"
            size = 20
            tooltip = f"⚙️ Service: {name}\nTier: {props.get('tier', 'N/A')}\nExposure: ${props.get('rev_exposure_per_hr', 0):,}/hr"
        elif label == "CloudResource":
            color = "#0ea5e9"
            size = 18
            tooltip = f"☁️ Cloud Infrastructure: {name}\nProvider: {props.get('provider', 'AWS')}"
        elif label == "Vendor":
            color = "#ec4899"
            size = 20
            tooltip = f"🔗 Third-Party SaaS: {name}\nSLA: {props.get('reliability_sla', 'N/A')}"
        elif label == "Epic":
            color = "#eab308"
            size = 22
            tooltip = f"🎯 Strategic Initiative: {name}\nDeadline: {props.get('deadline_days', 'N/A')} days\nFine: ${props.get('regulatory_fine', 0):,}"
        elif label == "Person":
            color = "#3b82f6"
            size = 20
            tooltip = f"👤 Personnel: {name}\nRole: {props.get('role', 'Team Member')}"
        else:
            color = "#64748b"
            size = 16
            tooltip = f"{name} ({label})"

        border = "#1a2333"

        if name in highlights.get("severed", []):
            color = "#ef4444"
            size = 32
            border = "#fca5a5"
            tooltip = f"💥 SEVERED TARGET: {name}\nSingle Point of Failure"
        elif name in highlights.get("impacted", []):
            color = "#f97316"
            size = 26
            border = "#fdba74"
            tooltip = f"⚠️ IN BLAST CASCADE: {name}\nImpacted by dependency chain"
        elif name in highlights.get("successor", []):
            color = "#10b981"
            size = 32
            border = "#6ee7b7"
            tooltip = f"🛡️ PAGERANK SUCCESSOR: {name}\nElected via GraphBLAS Centrality"

        net.add_node(
            n_id,
            label=name,
            color=color,
            size=size,
            shape="dot",
            borderWidth=2,
            borderWidthSelected=4,
            title=tooltip
        )

    for src, dst, r_type in edges:
        net.add_edge(src, dst, title=f"Relation: {r_type}", color="#1e293b", arrows="to", width=1.4)

    net.set_options("""
    {
      "physics": {
        "barnesHut": { "gravitationalConstant": -3400, "springLength": 95, "damping": 0.1 },
        "minVelocity": 0.75
      },
      "interaction": { "hover": true, "zoomView": true, "tooltipDelay": 80 }
    }
    """)
    components.html(net.generate_html(), height=530, scrolling=False)

# Trigger Simulation Execution
if trigger_btn:
    with st.spinner("Forking FalkorDB ephemeral sandbox & running GraphBLAS algorithms..."):
        if mode == "Staff Attrition":
            telemetry, report = agent.run_person_sim(target, temporal_days)
            st.session_state.last_sim = {
                "category": "person",
                "target": target,
                "days": temporal_days,
                "telemetry": telemetry,
                "report": report
            }
        else:
            telemetry, report = agent.run_service_sim(target)
            st.session_state.last_sim = {
                "category": "service",
                "target": target,
                "days": 0,
                "telemetry": telemetry,
                "report": report
            }
        st.session_state.healing_done = None

# Tabs Navigation
# In ui/app.py, update the tab layout line:
tab_sim, tab_agents, tab_heal, tab_radar, tab_board, tab_telemetry = st.tabs([
    "🎯 Real-Time Topology & Blast Diff",
    "🤖 Multi-Agent Coordination Mesh",
    "🛡️ Autonomous Remediation Engine",
    "📈 Enterprise Fragility Radar",
    "📄 Board Briefing Export",
    "⚡ FalkorDB Query Telemetry"
])

# Add this block to ui/app.py right after tab_sim:
# ---------------- TAB: MULTI-AGENT COORDINATION (TRACK 2 WEAPON) ----------------
with tab_agents:
    st.markdown("### 🤖 Multi-Agent Coordination & Shared Memory (Track 2)")
    st.write("Demonstration of asynchronous agent handoff. Two distinct agents coordinate and pass operational ownership strictly through FalkorDB `(:AgentHandoffMemory)` graph state nodes.")

    from agents.mcp_tools import GraphMCPTools
    from agents.multi_agent_mesh import TriageSentinelAgent, RemediationGovernanceAgent

    mcp = GraphMCPTools("company_prod")
    agent_1 = TriageSentinelAgent(mcp)
    agent_2 = RemediationGovernanceAgent()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style='background:#0d1527; border:1px solid #1e293b; border-radius:10px; padding:16px;'>
            <div style='font-size:11px; font-weight:800; color:#38bdf8; text-transform:uppercase;'>AGENT 1: TRIAGE SENTINEL</div>
            <div style='font-size:13px; color:#cbd5e1; margin-top:4px;'>Scans fractures, calls MCP tools (PageRank, SLA Audit), and commits unassigned handoff ticket to FalkorDB memory.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Trigger Agent 1 (Triage & Write Memory)", type="secondary", use_container_width=True):
            sandbox = engine.create_sandbox("company_prod")
            try:
                engine.simulate_departure(sandbox, "Alex", 14)
                handoff_data = agent_1.run_triage("Alex", sandbox)
                st.session_state["active_ticket"] = handoff_data["handoff_ticket_id"]
                st.success(f"✔ State persisted! Ticket ID: {handoff_data['handoff_ticket_id']}")
                st.json(handoff_data)
            finally:
                engine.drop_sandbox(sandbox)

    with c2:
        st.markdown("""
        <div style='background:#0d1527; border:1px solid #1e293b; border-radius:10px; padding:16px;'>
            <div style='font-size:11px; font-weight:800; color:#10b981; text-transform:uppercase;'>AGENT 2: REMEDIATION GOVERNOR</div>
            <div style='font-size:13px; color:#cbd5e1; margin-top:4px;'>Wakes up in a separate context, queries FalkorDB for active handoff memory nodes, and executes the remediation patch.</div>
        </div>
        """, unsafe_allow_html=True)
        active_t = st.session_state.get("active_ticket", "None")
        st.markdown(f"**Target Memory Node in Graph:** `ticket_id: {active_t}`")
        if st.button("Trigger Agent 2 (Read Memory & Resolve)", type="primary", use_container_width=True, disabled=(active_t == "None")):
            resolution = agent_2.execute_handoff_remediation(active_t)
            st.success(f"✔ Agent 2 resolved ticket {active_t} via FalkorDB memory query!")
            st.json(resolution)
            st.code(f"""
            // Verify persistent multi-agent memory state in FalkorDB:
            MATCH (m:AgentHandoffMemory {{ticket_id: '{active_t}'}})
            RETURN m.ticket_id, m.from_agent, m.to_agent, m.status, m.resolved_by;
            """, language="cypher")

# ---------------- TAB 1: TOPOLOGY & BLAST DIFF ----------------
with tab_sim:
    col_vis, col_panel = st.columns([1.15, 1], gap="medium")

    # If simulation has been run, compute diff highlights
    highlights = {"severed": [], "impacted": [], "successor": []}
    if st.session_state.last_sim:
        sim = st.session_state.last_sim
        highlights["severed"].append(sim["target"])
        t = sim["telemetry"]

        if sim["category"] == "person":
            for o in t.get("orphaned_initiatives", []):
                highlights["impacted"].append(o[0])
                if len(o) > 3 and isinstance(o[3], list):
                    highlights["impacted"].extend(o[3])
            for contract in t.get("impacted_contracts", []):
                highlights["impacted"].append(contract[0])
            for chain in t.get("downstream_blast_radius", []):
                if isinstance(chain, list):
                    highlights["impacted"].extend(chain)
                elif isinstance(chain, str):
                    highlights["impacted"].append(chain)
            if t.get("recommended_successors"):
                highlights["successor"].append(t["recommended_successors"][0][0])
        else:
            for up in t.get("impacted_upstream", []):
                highlights["impacted"].append(up[0])
            for contract in t.get("breached_contracts", []):
                highlights["impacted"].append(contract[0])

    with col_vis:
        st.markdown("<div style='font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:8px;'>TOPOLOGY CANVAS</div>", unsafe_allow_html=True)
        render_graph_view(highlights)
        st.markdown("""
        <div style='display: flex; gap: 14px; font-size: 11px; color: #94a3b8; justify-content: center; margin-top: 8px;'>
            <span><span style='color:#ef4444;'>●</span> Severed Target</span>
            <span><span style='color:#f97316;'>●</span> Blast Radius</span>
            <span><span style='color:#10b981;'>●</span> PageRank Successor</span>
            <span><span style='color:#a855f7;'>●</span> Contracts (SLAs)</span>
            <span><span style='color:#0284c7;'>●</span> Microservices</span>
            <span><span style='color:#ec4899;'>●</span> SaaS Vendors</span>
        </div>
        """, unsafe_allow_html=True)

    with col_panel:
        st.markdown("<div style='font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:8px;'>INCIDENT INTELLIGENCE</div>", unsafe_allow_html=True)

        if st.session_state.last_sim:
            sim = st.session_state.last_sim
            t = sim["telemetry"]
            rep = sim["report"]
            fin = t.get("financials", {})

            # Disruption Active View
            st.markdown(f"""
            <div class='exec-banner banner-danger'>
                <div class='banner-title'>SEV-1 SIMULATION ACTIVE (HORIZON: T+{sim['days']} DAYS)</div>
                <div class='banner-head'>{rep.get('executive_headline', 'Critical Structural Vulnerability Detected')}</div>
                <div class='banner-desc'>{rep.get('financial_impact_narrative', '')}</div>
            </div>
            """, unsafe_allow_html=True)

            if sim["category"] == "person":
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='kpi-tile'><div class='kpi-label'>Revenue Risk / Hr</div><div class='kpi-number' style='color:#ef4444;'>${fin.get('rev_at_risk_per_hr', 0):,.0f}</div><div class='kpi-sub'>Transactional loss</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-tile'><div class='kpi-label'>SLA Penalties / Hr</div><div class='kpi-number' style='color:#f97316;'>${fin.get('sla_penalties_per_hr', 0):,.0f}</div><div class='kpi-sub'>Contract default</div></div>", unsafe_allow_html=True)
                successor_name = t["recommended_successors"][0][0] if t.get("recommended_successors") else "None"
                c3.markdown(f"<div class='kpi-tile'><div class='kpi-label'>PageRank Successor</div><div class='kpi-number' style='color:#10b981;'>{successor_name}</div><div class='kpi-sub'>GraphBLAS lead</div></div>", unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                c1.markdown(f"<div class='kpi-tile'><div class='kpi-label'>Revenue Loss / Hr</div><div class='kpi-number' style='color:#ef4444;'>${fin.get('hourly_exposure', 0):,.0f}</div><div class='kpi-sub'>Direct downtime</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-tile'><div class='kpi-label'>Est. 4h Incident Cost</div><div class='kpi-number' style='color:#f97316;'>${fin.get('projected_4h_incident_cost', 0):,.0f}</div><div class='kpi-sub'>Exposure across mesh</div></div>", unsafe_allow_html=True)

            st.markdown("<div style='font-size:11px; font-weight:700; color:#64748b; margin: 16px 0 6px 0; text-transform:uppercase;'>CAUSAL GRAPH TRAVERSAL CHAINS:</div>", unsafe_allow_html=True)
            if sim["category"] == "person" and t.get("downstream_blast_radius"):
                for path in t["downstream_blast_radius"]:
                    st.markdown(f"<div class='flow-pill'>⚠️ {' ➔ '.join(path)}</div>", unsafe_allow_html=True)
            elif sim["category"] == "service" and t.get("impacted_upstream"):
                for up in t["impacted_upstream"]:
                    st.markdown(f"<div class='flow-pill'>🔥 {' ➔ '.join(up[3])}</div>", unsafe_allow_html=True)

            p_comm = rep.get("primary_commander", {})
            st.markdown("<div style='font-size:11px; font-weight:700; color:#64748b; margin: 16px 0 6px 0; text-transform:uppercase;'>ALGORITHMIC INCIDENT COMMANDER:</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='officer-box'>
                <div class='officer-avatar'>{p_comm.get('name', 'S')[0]}</div>
                <div>
                    <div style='font-weight:700; color:#f8fafc; font-size:14px;'>{p_comm.get('name', 'Sarah')} <span style='font-size:12px; color:#38bdf8; font-weight:500;'>({p_comm.get('role', 'Staff Architect')})</span></div>
                    <div style='font-size:12px; color:#94a3b8; margin-top:2px;'>{p_comm.get('justification', 'Elected via PageRank centrality on GraphBLAS matrix kernel.')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📋 View 24-Hour Automated Remediation Protocol", expanded=False):
                for phase in rep.get("remediation_phases", []):
                    st.markdown(f"**{phase.get('phase')}**")
                    for act in phase.get("actions", []):
                        st.markdown(f"- {act}")

        else:
            # Clean Baseline State (Before Clicking Anything)
            st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 4px solid #10b981; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px;'>
                <div style='font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #10b981;'>NOMINAL OPERATION // ALL SYSTEMS HEALTHY</div>
                <div style='font-size: 15px; font-weight: 700; color: #f8fafc; margin-top: 3px;'>Enterprise Socio-Technical Mesh is Fully Balanced</div>
                <div style='font-size: 13px; color: #cbd5e1; margin-top: 4px;'>No unassigned ownership, severed dependencies, or regulatory bottlenecks detected in production.</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.markdown("<div class='kpi-tile'><div class='kpi-label'>SLA Compliance</div><div class='kpi-number' style='color:#10b981;'>100%</div><div class='kpi-sub'>Contracts Secure</div></div>", unsafe_allow_html=True)
            c2.markdown("<div class='kpi-tile'><div class='kpi-label'>Active Services</div><div class='kpi-number' style='color:#38bdf8;'>8</div><div class='kpi-sub'>Tier-0/1 Services</div></div>", unsafe_allow_html=True)
            c3.markdown("<div class='kpi-tile'><div class='kpi-label'>Active Roadmaps</div><div class='kpi-number' style='color:#eab308;'>4</div><div class='kpi-sub'>Staffed Mandates</div></div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background:#0d1527; border: 1px solid #1a2333; border-radius:10px; padding:18px; margin-top:20px;'>
                <div style='font-size:13px; font-weight:700; color:#f8fafc;'>⚡ How to Test Ripple OS:</div>
                <div style='font-size:12px; color:#94a3b8; margin-top:6px; line-height:1.7;'>
                    1. In the sidebar, select a critical engineer like <b>Alex</b> or service like <b>payments-engine</b>.<br>
                    2. Adjust the <b>Temporal Horizon</b> slider (e.g., 14 days out).<br>
                    3. Click <b>Execute Chaos Simulation</b> to fork an ephemeral FalkorDB graph sandbox and view causal blast radius diffs in real-time.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------------- TAB 2: AUTONOMOUS REMEDIATION ----------------
with tab_heal:
    st.markdown("### 🛡️ Autonomous State Remediation & Agent Memory (Track 2)")
    st.write("FalkorDB doesn't just observe; it actively remediates. One click mutates the topology, patches dead ownership, and commits an immutable `(:AgentMemory)` node for persistent cross-session coordination.")

    if st.session_state.last_sim and st.session_state.last_sim["category"] == "person":
        sim = st.session_state.last_sim
        target_name = sim["target"]
        successor = sim["telemetry"]["recommended_successors"][0][0]

        st.markdown(f"""
        **Automated Remediation Action Package:**
        * Detach dead ownership and knowledge edges from **@{target_name}**.
        * Synthetically bind orphaned Epics and Services directly to **@{successor}** via `[:KNOWS_ABOUT]` and `[:OWNS]`.
        * Commit an immutable cryptographic memory node `(:AgentMemory)` into FalkorDB.
        """)

        if st.button(f"⚡ EXECUTE AUTONOMOUS PATCH ➔ TRANSFER TO @{successor}", type="primary"):
            heal_result = engine.execute_autonomous_healing(target_name, successor)
            st.session_state.healing_done = heal_result

        if st.session_state.healing_done:
            h = st.session_state.healing_done
            st.success(f"✔ Remediation complete! Rescued {h['epics_rescued']} Epics and {h['services_rescued']} Services. Reassigned to @{h['successor']}.")
            st.markdown(f"**FalkorDB Persistent Memory ID:** `{h['memory_node_id']}`")
            st.code(f"""
            // Verify persistent memory across sessions in FalkorDB:
            MATCH (p:Person {{name: '{h['successor']}'}})-[:HAS_INCIDENT_MEMORY]->(m:AgentMemory)
            RETURN m.id AS memory_id, m.incident_type AS type, m.mitigated_target AS target, m.status AS status;
            """, language="cypher")
    else:
        st.info("Run a Staff Attrition simulation in Tab 1 to generate an autonomous remediation protocol.")

# ---------------- TAB 3: FRAGILITY RADAR ----------------
with tab_radar:
    st.markdown("### 📈 Enterprise Fragility Radar (Continuous Bus-Factor Stress Test)")
    st.write("Monte Carlo analysis running across independent FalkorDB sandboxes to rank every staff member by structural and financial fragility.")

    if st.button("🔍 SCAN FULL ENTERPRISE ESTATE", type="secondary"):
        with st.spinner("Spawning parallel FalkorDB sandboxes and running stress simulations..."):
            scores = engine.run_company_fragility_scan()
            df = pd.DataFrame(scores)

            st.dataframe(
                df[["name", "role", "orphans", "blast_hops", "financial_exposure", "vulnerability_score", "bus_factor_threat"]],
                use_container_width=True,
                column_config={
                    "vulnerability_score": st.column_config.ProgressColumn("Fragility Index", min_value=0, max_value=100, format="%d%%"),
                    "bus_factor_threat": st.column_config.TextColumn("Threat Tier")
                }
            )

# ---------------- TAB 4: BOARD BRIEFING EXPORT ----------------
with tab_board:
    st.markdown("### 📄 Board-Level Briefing Export")
    st.write("Generate a formal, C-level executive incident memorandum with audit signatures for regulatory and board compliance.")

    if st.session_state.last_sim:
        sim = st.session_state.last_sim
        rep = sim["report"]
        fin = sim["telemetry"].get("financials", {})

        board_memo = f"""# EXECUTIVE INCIDENT MEMORANDUM
**CLASSIFICATION:** STRICTLY CONFIDENTIAL // C-SUITE ONLY  
**SOURCE ENGINE:** RIPPLE OS // FALKORDB ENTERPRISE GRAPH  
**INCIDENT DOMAIN:** {sim['category'].upper()} - {sim['target']}  
**TEMPORAL HORIZON:** T+{sim['days']} DAYS  

---

### 1. EXECUTIVE RISK ABSTRACT
{rep.get('executive_headline')}

### 2. QUANTIFIED FINANCIAL EXPOSURE
* **Hourly Revenue at Risk:** ${fin.get('rev_at_risk_per_hr', fin.get('hourly_exposure', 0)):,.2f} / hr
* **Regulatory Compliance Exposure:** ${fin.get('regulatory_exposure', 0):,.2f}
* **Projected Incident Cost:** ${fin.get('est_24h_outage_loss', fin.get('projected_4h_incident_cost', 0)):,.2f}

### 3. APPOINTED INCIDENT COMMANDER
* **Officer:** {rep.get('primary_commander', {}).get('name')} ({rep.get('primary_commander', {}).get('role')})
* **Algorithmic Selection:** {rep.get('primary_commander', {}).get('justification')}

### 4. MITIGATION AUDIT TRAIL
* Graph Memory ID: {st.session_state.healing_done.get('memory_node_id') if st.session_state.healing_done else 'PENDING_COMMIT'}
* System Status: ACTIVE MITIGATION IN PROGRESS
"""
        st.text_area("Memorandum Markdown", board_memo, height=280)
        st.download_button(
            "📥 Download Executive Briefing (.md)",
            board_memo,
            file_name=f"Ripple_Board_Briefing_{sim['target']}.md",
            mime="text/markdown"
        )
    else:
        st.info("Execute a simulation to generate an executive board memorandum.")

# ---------------- TAB 5: FALKORDB TELEMETRY TRACES ----------------
with tab_telemetry:
    st.markdown("### ⚡ FalkorDB Native Engine Traces")
    st.write("Real-time inspection trace of exact OpenCypher statements and linear algebra latencies executed in this session.")
    telem = engine.get_telemetry()
    if telem:
        st.dataframe(pd.DataFrame(telem)[["latency_ms", "type", "rows", "query"]], use_container_width=True)
    else:
        st.caption("Telemetry stream active. Execute any simulation to inspect execution kernels.")