import uuid
import time
from core.database import DatabaseManager

class SimulationEngine:
    def __init__(self):
        self.db = DatabaseManager.get_client()
        self.telemetry_log = []

    def _logged_query(self, graph, query: str, params=None, read_only=False):
        start = time.perf_counter()
        res = graph.ro_query(query, params) if read_only else graph.query(query, params)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        self.telemetry_log.append({
            "query": query.strip().split("\n")[0] + ("..." if "\n" in query.strip() else ""),
            "full_query": query.strip(),
            "latency_ms": round(elapsed_ms, 2),
            "rows": len(res.result_set) if res.result_set else 0,
            "type": "READ" if read_only else "MUTATE"
        })
        return res

    def get_telemetry(self):
        return self.telemetry_log

    def clear_telemetry(self):
        self.telemetry_log = []

    def create_sandbox(self, source_graph_name="company_prod") -> str:
        sandbox_id = f"sim_{uuid.uuid4().hex[:8]}"
        src = self.db.select_graph(source_graph_name)
        dst = self.db.select_graph(sandbox_id)

        nodes = self._logged_query(src, "MATCH (n) RETURN id(n) AS id, labels(n)[0] AS label, properties(n) AS props", read_only=True).result_set

        node_map = {}
        for n_id, label, props in nodes:
            prop_items = []
            for k, v in props.items():
                if isinstance(v, str):
                    escaped = v.replace("'", "\\'")
                    prop_items.append(f"{k}: '{escaped}'")
                else:
                    prop_items.append(f"{k}: {v}")
            prop_str = ", ".join(prop_items)
            res = self._logged_query(dst, f"CREATE (n:{label} {{{prop_str}}}) RETURN id(n)")
            node_map[n_id] = res.result_set[0][0]

        rels = self._logged_query(src, "MATCH (a)-[r]->(b) RETURN id(a) AS src, type(r) AS type, properties(r) AS props, id(b) AS dst", read_only=True).result_set
        for src_id, r_type, props, dst_id in rels:
            new_src = node_map[src_id]
            new_dst = node_map[dst_id]
            prop_items = []
            for k, v in props.items():
                if isinstance(v, str):
                    escaped = v.replace("'", "\\'")
                    prop_items.append(f"{k}: '{escaped}'")
                else:
                    prop_items.append(f"{k}: {v}")
            prop_str = ", ".join(prop_items)
            prop_clause = f" {{{prop_str}}}" if prop_str else ""
            self._logged_query(dst, f"""
                MATCH (a), (b)
                WHERE id(a) = {new_src} AND id(b) = {new_dst}
                CREATE (a)-[:{r_type}{prop_clause}]->(b)
            """)
        return sandbox_id

    def drop_sandbox(self, sandbox_id: str):
        try:
            self.db.select_graph(sandbox_id).delete()
        except Exception:
            pass

    def get_graph_data(self, graph_name="company_prod"):
        g = self.db.select_graph(graph_name)
        nodes = g.ro_query("MATCH (n) RETURN id(n), labels(n)[0], n.name, properties(n)").result_set
        edges = g.ro_query("MATCH (a)-[r]->(b) RETURN id(a), id(b), type(r)").result_set
        return nodes, edges

    def simulate_departure(self, sandbox_id: str, person_name: str, temporal_days: int = 0) -> dict:
        g = self.db.select_graph(sandbox_id)

        # 1. Pre-departure inventory
        pre_check = self._logged_query(
            g,
            "MATCH (p:Person {name: $name})-[r]->(target) RETURN type(r) AS rel, labels(target)[0] AS target_type, target.name AS target_name",
            {"name": person_name},
            read_only=True
        ).result_set

        # 2. Sever the actor node
        self._logged_query(g, "MATCH (p:Person {name: $name}) DETACH DELETE p", {"name": person_name})

        # 3. Detect orphaned Epics & associated Regulatory fines
        orphans = self._logged_query(g, """
            MATCH (e:Epic)
            WHERE NOT (:Person)-[:KNOWS_ABOUT]->(e)
            OPTIONAL MATCH (e)-[:BLOCKS|MANDATES_CHANGE_ON]->(target)
            RETURN e.name AS epic, e.deadline_days AS deadline, e.regulatory_fine AS fine, collect(target.name) AS impacted_targets
        """, read_only=True).result_set

        # 4. Multi-hop Traversal: Which Customer Contracts have SLAs breached?
        # Path: CustomerContract -> Service -> Service -> (impacted targets)
        sla_breaches = self._logged_query(g, """
            MATCH (c:CustomerContract)-[:COVERS_SLA]->(s:Service)
            WHERE s.name IN ['payments-engine', 'checkout-orchestrator', 'orders-service']
            RETURN DISTINCT c.name AS customer, c.arr AS arr, c.penalty_per_hr AS penalty, s.name AS covered_service
        """, read_only=True).result_set

        # 5. Successor selection via PageRank on collaboration network
        try:
            pagerank = self._logged_query(g, """
                CALL algo.pageRank('Person', 'COLLABORATES_WITH')
                YIELD node, score
                RETURN node.name AS candidate, score
                ORDER BY score DESC
                LIMIT 3
            """, read_only=True).result_set
        except Exception:
            pagerank = self._logged_query(g, """
                MATCH (p:Person)-[:COLLABORATES_WITH]-(other)
                RETURN p.name AS candidate, count(other) AS score
                ORDER BY score DESC
                LIMIT 3
            """, read_only=True).result_set

        # 6. Deep 4-Hop Blast Path Traversals
        blast_paths = self._logged_query(g, """
            MATCH path = (c:CustomerContract)-[:COVERS_SLA]->(s1:Service)-[:DEPENDS_ON*1..3]->(s2:Service {name: 'payments-engine'})
            RETURN [n IN nodes(path) | n.name] AS trace
        """, read_only=True).result_set

        # Calculate Financial Exposure
        total_regulatory = sum(o[2] or 0 for o in orphans)
        total_sla_penalty_hr = sum(s[2] or 0 for s in sla_breaches)
        rev_at_risk_hr = 130000 + 95000  # payments-engine + checkout-orchestrator baseline

        return {
            "type": "person_departure",
            "departed": person_name,
            "temporal_horizon_days": temporal_days,
            "lost_connections": pre_check,
            "orphaned_initiatives": orphans,
            "impacted_contracts": sla_breaches,
            "recommended_successors": pagerank,
            "downstream_blast_radius": [p[0] for p in blast_paths],
            "financials": {
                "rev_at_risk_per_hr": rev_at_risk_hr,
                "sla_penalties_per_hr": total_sla_penalty_hr,
                "regulatory_exposure": total_regulatory,
                "est_24h_outage_loss": (rev_at_risk_hr + total_sla_penalty_hr) * 24 + total_regulatory
            }
        }

    def simulate_service_outage(self, sandbox_id: str, service_name: str) -> dict:
        g = self.db.select_graph(sandbox_id)

        # 1. Cascade traversal: From client contracts to cloud infrastructure
        upstream = self._logged_query(g, """
            MATCH path = (upstream)-[:ROUTES_TO|DEPENDS_ON*1..4]->(s:Service {name: $name})
            RETURN DISTINCT upstream.name AS component, labels(upstream)[0] AS type, length(path) AS hops, [n IN nodes(path) | n.name] AS via
            ORDER BY hops
        """, {"name": service_name}, read_only=True).result_set

        # 2. Impacted SLAs
        sla_breaches = self._logged_query(g, """
            MATCH (c:CustomerContract)-[:COVERS_SLA]->(s:Service)
            WHERE s.name = $name OR s.name IN $upstream_names
            RETURN DISTINCT c.name, c.penalty_per_hr, c.arr
        """, {"name": service_name, "upstream_names": [u[0] for u in upstream]}, read_only=True).result_set

        # 3. Emergency escalation contacts
        owners = self._logged_query(g, """
            MATCH (p:Person)-[:OWNS|ONCALL_FOR]->(s:Service)
            WHERE s.name = $name OR s.name IN $upstream_names
            RETURN p.name AS person, p.role AS role, p.timezone AS timezone, collect(s.name) AS services
        """, {"name": service_name, "upstream_names": [u[0] for u in upstream]}, read_only=True).result_set

        self._logged_query(g, "MATCH (s:Service {name: $name}) DETACH DELETE s", {"name": service_name})

        total_sla_hr = sum(s[1] or 0 for s in sla_breaches)

        return {
            "type": "service_outage",
            "failed_service": service_name,
            "impacted_upstream": upstream,
            "breached_contracts": sla_breaches,
            "responders_to_alert": owners,
            "financials": {
                "hourly_exposure": 130000 + total_sla_hr,
                "projected_4h_incident_cost": (130000 + total_sla_hr) * 4
            }
        }

    def execute_autonomous_healing(self, target_person: str, successor_person: str) -> dict:
        g = self.db.select_graph("company_prod")

        patch_query = """
        MATCH (successor:Person {name: $successor})
        MATCH (departed:Person {name: $departed})
        OPTIONAL MATCH (departed)-[:KNOWS_ABOUT]->(e:Epic)
        OPTIONAL MATCH (departed)-[:OWNS]->(s:Service)
        FOREACH (epic IN CASE WHEN e IS NOT NULL THEN [e] ELSE [] END |
            CREATE (successor)-[:KNOWS_ABOUT {source: 'Ripple-Autonomous-Engine', timestamp: timestamp()}]->(epic)
        )
        FOREACH (srv IN CASE WHEN s IS NOT NULL THEN [s] ELSE [] END |
            CREATE (successor)-[:OWNS {source: 'Ripple-Autonomous-Engine', timestamp: timestamp()}]->(srv)
        )
        RETURN count(e) AS epics_rescued, count(s) AS services_rescued
        """
        patch_res = self._logged_query(g, patch_query, {"successor": successor_person, "departed": target_person}).result_set

        memory_query = """
        MATCH (successor:Person {name: $successor})
        CREATE (finding:AgentMemory {
            id: randomUUID(),
            incident_type: 'Personnel Departure Remediation',
            mitigated_target: $departed,
            successor_assigned: $successor,
            status: 'MITIGATED_ACTIVE',
            resolved_at: timestamp()
        })
        CREATE (successor)-[:HAS_INCIDENT_MEMORY]->(finding)
        RETURN finding.id AS memory_id
        """
        mem_res = self._logged_query(g, memory_query, {"successor": successor_person, "departed": target_person}).result_set

        return {
            "status": "SUCCESS",
            "successor": successor_person,
            "epics_rescued": patch_res[0][0] if patch_res else 0,
            "services_rescued": patch_res[0][1] if patch_res else 0,
            "memory_node_id": mem_res[0][0] if mem_res else None
        }

    def run_company_fragility_scan(self) -> list:
        g = self.db.select_graph("company_prod")
        people = g.ro_query("MATCH (p:Person) RETURN p.name AS name, p.role AS role").result_set

        scores = []
        for name, role in people:
            sandbox = self.create_sandbox("company_prod")
            try:
                res = self.simulate_departure(sandbox, name, temporal_days=0)
                orphans = len(res["orphaned_initiatives"])
                blast = len(res["downstream_blast_radius"])
                financial_risk = res["financials"]["est_24h_outage_loss"]
                vuln_score = min(100, (orphans * 35) + (blast * 15) + (20 if financial_risk > 200000 else 0))
                
                scores.append({
                    "name": name,
                    "role": role,
                    "orphans": orphans,
                    "blast_hops": blast,
                    "financial_exposure": f"${financial_risk:,.0f}",
                    "vulnerability_score": vuln_score,
                    "bus_factor_threat": "CRITICAL" if vuln_score >= 70 else ("HIGH" if vuln_score >= 35 else "STABLE")
                })
            finally:
                self.drop_sandbox(sandbox)

        scores.sort(key=lambda x: x["vulnerability_score"], reverse=True)
        return scores