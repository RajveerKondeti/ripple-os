"""
Multi-Agent Coordination & Memory Mesh (Track 2 Compliance)
Demonstrates Agent-to-Agent Handoff via FalkorDB Persistent State Nodes.
"""
import uuid
import json
from agents.mcp_tools import GraphMCPTools
from core.database import DatabaseManager

class TriageSentinelAgent:
    """Agent 1: Detects fractures, queries MCP tools, and writes episodic memory to FalkorDB."""
    def __init__(self, tools: GraphMCPTools):
        self.tools = tools
        self.db = DatabaseManager.get_client()

    def run_triage(self, departed_person: str, sandbox_id: str) -> dict:
        g = self.db.select_graph(sandbox_id)
        
        # 1. Discover orphaned initiatives
        orphans = g.ro_query("""
            MATCH (e:Epic)
            WHERE NOT (:Person)-[:KNOWS_ABOUT]->(e)
            RETURN e.name AS epic, e.deadline_days AS deadline, e.regulatory_fine AS fine
        """).result_set

        # 2. Use MCP tools to find provenance and customer blast
        impacted_docs = []
        for o in orphans:
            docs = self.tools.resolve_source_provenance(o[0])
            impacted_docs.extend(docs)

        sla_risks = self.tools.audit_contract_exposure(['payments-engine', 'checkout-orchestrator'])
        top_candidates = self.tools.compute_pagerank_successors()

        # 3. Write Handoff State into FalkorDB Persistent Memory
        handoff_ticket_id = f"HND-{uuid.uuid4().hex[:6].upper()}"
        handoff_query = """
        CREATE (m:AgentHandoffMemory {
            ticket_id: $ticket_id,
            from_agent: 'TriageSentinelAgent',
            to_agent: 'RemediationGovernanceAgent',
            target_departed: $departed,
            status: 'TRIAGED_PENDING_RECOVERY',
            recommended_successor: $successor,
            created_at: timestamp()
        })
        RETURN m.ticket_id
        """
        top_pick = top_candidates[0]["candidate"] if top_candidates else "Sarah"
        self.db.select_graph("company_prod").query(handoff_query, {
            "ticket_id": handoff_ticket_id,
            "departed": departed_person,
            "successor": top_pick
        })

        return {
            "handoff_ticket_id": handoff_ticket_id,
            "orphaned_epics": orphans,
            "provenance_documents": impacted_docs,
            "sla_penalties": sla_risks,
            "elected_successor": top_pick,
            "status": "PASSED_TO_REMEDIATION_AGENT"
        }

class RemediationGovernanceAgent:
    """Agent 2: Wakes up, reads Agent 1's memory node from FalkorDB, and executes the state patch."""
    def __init__(self):
        self.db = DatabaseManager.get_client()

    def execute_handoff_remediation(self, handoff_ticket_id: str) -> dict:
        g = self.db.select_graph("company_prod")

        # 1. Read Agent 1's state from FalkorDB memory
        state_rows = g.ro_query("""
            MATCH (m:AgentHandoffMemory {ticket_id: $ticket_id})
            RETURN m.target_departed, m.recommended_successor, m.status
        """, {"ticket_id": handoff_ticket_id}).result_set

        if not state_rows:
            return {"error": "Handoff ticket not found in FalkorDB memory."}

        departed, successor, old_status = state_rows[0]

        # 2. Execute the autonomous patch
        patch_query = """
        MATCH (s:Person {name: $successor})
        MATCH (d:Person {name: $departed})
        OPTIONAL MATCH (d)-[:KNOWS_ABOUT]->(e:Epic)
        OPTIONAL MATCH (d)-[:OWNS]->(srv:Service)
        FOREACH (epic IN CASE WHEN e IS NOT NULL THEN [e] ELSE [] END |
            CREATE (s)-[:KNOWS_ABOUT {source: 'MultiAgentHandoff', timestamp: timestamp()}]->(epic)
        )
        FOREACH (svc IN CASE WHEN srv IS NOT NULL THEN [srv] ELSE [] END |
            CREATE (s)-[:OWNS {source: 'MultiAgentHandoff', timestamp: timestamp()}]->(svc)
        )
        """
        g.query(patch_query, {"successor": successor, "departed": departed})

        # 3. Transition memory state to RESOLVED
        g.query("""
            MATCH (m:AgentHandoffMemory {ticket_id: $ticket_id})
            SET m.status = 'REMEDIATION_COMMITTED',
                m.resolved_by = 'RemediationGovernanceAgent',
                m.resolved_at = timestamp()
        """, {"ticket_id": handoff_ticket_id})

        return {
            "ticket_id": handoff_ticket_id,
            "previous_status": old_status,
            "final_status": "REMEDIATION_COMMITTED",
            "active_officer": successor,
            "recovered_for": departed
        }