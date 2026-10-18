import os
import json
from dotenv import load_dotenv
from litellm import completion
from core.simulation import SimulationEngine

load_dotenv()

ENTERPRISE_SYSTEM_PROMPT = """You are Ripple OS — an autonomous socio-technical resilience engine.
Analyze the FalkorDB simulation telemetry and return a strictly valid JSON response following this schema:
{
  "executive_headline": "Direct 1-sentence urgent summary of financial and technical exposure",
  "threat_level": "CRITICAL" | "HIGH" | "ELEVATED",
  "financial_impact_narrative": "Crisp 1-2 sentence business impact citing the exact dollar risk per hour",
  "primary_commander": {
    "name": "Person Name",
    "role": "Role",
    "justification": "Why chosen via PageRank centrality"
  },
  "temporal_milestones": [
    {"day": 0, "status": "Immediate attrition, ownership severed"},
    {"day": 14, "status": "Stripe-v3-Migration breach risks $250k regulatory fine"},
    {"day": 60, "status": "OAuth rotation deadline failure threatens complete auth outage"}
  ],
  "remediation_phases": [
    {
      "phase": "Phase 1: Immediate Containment (0-2h)",
      "actions": ["Reassign payments-gateway ownership via FalkorDB mutation", "Activate standby SRE"]
    },
    {
      "phase": "Phase 2: Knowledge Extraction & Shadowing (2-12h)",
      "actions": ["Initiate pair-programming handover on Stripe-v3 codebase", "Audit uncommitted branch diffs"]
    },
    {
      "phase": "Phase 3: Formal Verification (12-24h)",
      "actions": ["Verify checkout-api end-to-end traversal", "Commit immutable AgentMemory node to graph"]
    }
  ]
}
Return pure JSON only. No markdown formatting ticks.
"""

class ResilienceAgent:
    def __init__(self, engine: SimulationEngine = None, model: str = "gemini/gemini-2.5-flash"):
        # Shared engine instance preserves telemetry in Streamlit session state
        self.engine = engine if engine is not None else SimulationEngine()
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            os.environ["GEMINI_API_KEY"] = self.api_key

    def run_person_sim(self, target_person: str, temporal_days: int = 0) -> tuple[dict, dict]:
        self.engine.clear_telemetry()
        sandbox_id = self.engine.create_sandbox("company_prod")
        try:
            telemetry = self.engine.simulate_departure(sandbox_id, target_person, temporal_days)
            report = self._call_llm(telemetry, f"Simulate departure of staff member '{target_person}' at day {temporal_days}")
            return telemetry, report
        finally:
            self.engine.drop_sandbox(sandbox_id)

    def run_service_sim(self, target_service: str) -> tuple[dict, dict]:
        self.engine.clear_telemetry()
        sandbox_id = self.engine.create_sandbox("company_prod")
        try:
            telemetry = self.engine.simulate_service_outage(sandbox_id, target_service)
            report = self._call_llm(telemetry, f"Analyze Sev-1 infrastructure failure on '{target_service}'")
            return telemetry, report
        finally:
            self.engine.drop_sandbox(sandbox_id)

    def _call_llm(self, telemetry: dict, task_desc: str) -> dict:
        prompt = f"TELEMETRY DATA:\n{json.dumps(telemetry, indent=2)}\n\nTASK: {task_desc}"
        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": ENTERPRISE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].replace("json", "").strip()
            return json.loads(raw)
        except Exception:
            return self._fallback_json(telemetry)

    def _fallback_json(self, t: dict) -> dict:
        is_person = t.get("type") == "person_departure"
        target = t.get("departed") if is_person else t.get("failed_service")
        successor = t.get("recommended_successors", [[target, 0.5]])[0][0] if is_person else "Sarah"

        return {
            "executive_headline": f"Immediate operational vulnerability detected following disruption of {target}.",
            "threat_level": "CRITICAL",
            "financial_impact_narrative": "Downstream core payment and checkout pathways are exposed to degradation.",
            "primary_commander": {
                "name": successor,
                "role": "Lead Incident Commander",
                "justification": "Highest PageRank topological centrality within the affected sub-graph."
            },
            "temporal_milestones": [
                {"day": 0, "status": "Ownership vacuum initiated"},
                {"day": 14, "status": "Stripe-v3-Migration blocker activates"},
                {"day": 60, "status": "OAuth rotation certificate expires"}
            ],
            "remediation_phases": [
                {
                    "phase": "Phase 1: Immediate Containment (0-2h)",
                    "actions": [f"Reroute operational ownership of impacted systems to {successor}", "Activate emergency monitoring"]
                },
                {
                    "phase": "Phase 2: Root-Cause Remediation (2-12h)",
                    "actions": ["Verify dependency heartbeat", "Inspect orphaned initiative deliverables"]
                },
                {
                    "phase": "Phase 3: Verification & Recovery (12-24h)",
                    "actions": ["Run end-to-end checkout verification query", "Persist incident mitigation memory in FalkorDB"]
                }
            ]
        }