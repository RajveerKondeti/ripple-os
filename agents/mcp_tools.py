"""
MCP (Model Context Protocol) Tool Catalogue for FalkorDB
Exposes typed graph algorithms and traversals as autonomous tools for Gemini.
"""
from core.database import DatabaseManager

class GraphMCPTools:
    def __init__(self, graph_name="company_prod"):
        self.db = DatabaseManager.get_client()
        self.graph_name = graph_name

    def get_graph(self):
        return self.db.select_graph(self.graph_name)

    # Tool 1: Blast Radius Traversal
    def compute_blast_radius(self, target_service: str, depth: int = 4) -> list:
        depth = min(max(1, depth), 5)
        g = self.get_graph()
        query = """
        MATCH path = (upstream)-[:ROUTES_TO|DEPENDS_ON*1..""" + str(depth) + """]->(target:Service {name: $name})
        RETURN DISTINCT upstream.name AS component, labels(upstream)[0] AS type, length(path) AS hops, [n IN nodes(path) | n.name] AS trace
        ORDER BY hops
        """
        rows = g.ro_query(query, {"name": target_service}).result_set
        return [{"component": r[0], "type": r[1], "hops": r[2], "trace": r[3]} for r in rows]

    # Tool 2: PageRank Centrality Tool
    def compute_pagerank_successors(self) -> list:
        g = self.get_graph()
        try:
            rows = g.ro_query("""
                CALL algo.pageRank('Person', 'COLLABORATES_WITH')
                YIELD node, score
                RETURN node.name AS candidate, score
                ORDER BY score DESC
                LIMIT 3
            """).result_set
            return [{"candidate": r[0], "pagerank_score": round(float(r[1]), 5)} for r in rows]
        except Exception:
            rows = g.ro_query("""
                MATCH (p:Person)-[:COLLABORATES_WITH]-(other)
                RETURN p.name, count(other) AS score ORDER BY score DESC LIMIT 3
            """).result_set
            return [{"candidate": r[0], "degree_score": r[1]} for r in rows]

    # Tool 3: Document Provenance Resolution
    def resolve_source_provenance(self, initiative_name: str) -> list:
        g = self.get_graph()
        query = """
        MATCH (e:Epic {name: $name})-[:DOCUMENTED_IN]->(d:Document)
        OPTIONAL MATCH (author:Person)-[:AUTHORED]->(d)
        RETURN d.id AS doc_id, d.title AS title, d.url AS url, d.sha AS commit_sha, author.name AS original_author
        """
        rows = g.ro_query(query, {"name": initiative_name}).result_set
        return [{"doc_id": r[0], "title": r[1], "url": r[2], "commit_sha": r[3], "author": r[4]} for r in rows]

    # Tool 4: Customer Contract Exposure
    def audit_contract_exposure(self, service_names: list) -> list:
        g = self.get_graph()
        query = """
        MATCH (c:CustomerContract)-[:COVERS_SLA]->(s:Service)
        WHERE s.name IN $services
        RETURN DISTINCT c.name AS customer, c.arr AS arr, c.penalty_per_hr AS penalty, s.name AS service
        """
        rows = g.ro_query(query, {"services": service_names}).result_set
        return [{"customer": r[0], "arr": r[1], "hourly_penalty": r[2], "service": r[3]} for r in rows]