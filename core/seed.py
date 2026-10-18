from core.database import DatabaseManager

def seed_enterprise_graph():
    db = DatabaseManager.get_client()
    g = db.select_graph("company_prod")

    try:
        g.delete()
    except Exception:
        pass

    cypher = """
    // ==========================================
    // 1. TIER-1 ENTERPRISE CUSTOMER CONTRACTS (SLAs)
    // ==========================================
    CREATE (acme:CustomerContract {name: 'Acme-Global-Retail', arr: 14000000, penalty_per_hr: 50000, tier: 'Mission-Critical'})
    CREATE (vertex:CustomerContract {name: 'Vertex-Fintech-Corp', arr: 9500000, penalty_per_hr: 35000, tier: 'Mission-Critical'})
    CREATE (omni:CustomerContract {name: 'Omni-Logistics-LLC', arr: 4200000, penalty_per_hr: 15000, tier: 'Enterprise'})

    // ==========================================
    // 2. EDGE INGRESS & FRONTEND ROUTERS
    // ==========================================
    CREATE (edge_proxy:Service {name: 'edge-api-gateway', tier: 'tier-0', lang: 'Rust', rev_exposure_per_hr: 110000})
    CREATE (checkout_web:Service {name: 'checkout-orchestrator', tier: 'tier-0', lang: 'Go', rev_exposure_per_hr: 95000})
    CREATE (portal_ui:Service {name: 'customer-portal-ui', tier: 'tier-2', lang: 'TypeScript', rev_exposure_per_hr: 20000})

    // ==========================================
    // 3. CORE TRANSACTIONAL & DOMAIN MICROSERVICES
    // ==========================================
    CREATE (payments_engine:Service {name: 'payments-engine', tier: 'tier-0', lang: 'Java', rev_exposure_per_hr: 130000})
    CREATE (orders_service:Service {name: 'orders-service', tier: 'tier-1', lang: 'Go', rev_exposure_per_hr: 75000})
    CREATE (auth_mesh:Service {name: 'identity-mesh', tier: 'tier-0', lang: 'Go', rev_exposure_per_hr: 85000})
    CREATE (fraud_pipeline:Service {name: 'fraud-detection-engine', tier: 'tier-1', lang: 'Python', rev_exposure_per_hr: 40000})
    CREATE (notification_broker:Service {name: 'notification-dispatcher', tier: 'tier-2', lang: 'Python', rev_exposure_per_hr: 12000})
    CREATE (ledger_sink:Service {name: 'ledger-reconciler', tier: 'tier-1', lang: 'Scala', rev_exposure_per_hr: 60000})

    // ==========================================
    // 4. CLOUD INFRASTRUCTURE & EVENT BUSES
    // ==========================================
    CREATE (kafka_cluster:CloudResource {name: 'kafka-event-backbone', provider: 'AWS', region: 'us-east-1', tier: 'foundational'})
    CREATE (aurora_db:CloudResource {name: 'aurora-primary-cluster', provider: 'AWS', region: 'us-east-1', tier: 'foundational'})
    CREATE (redis_cache:CloudResource {name: 'redis-session-mesh', provider: 'AWS', region: 'us-east-1', tier: 'tier-1'})
    CREATE (k8s_prod:CloudResource {name: 'k8s-prod-us-east', provider: 'AWS', region: 'us-east-1', tier: 'foundational'})

    // ==========================================
    // 5. THIRD-PARTY DEPENDENCIES & VENDORS
    // ==========================================
    CREATE (stripe_api:Vendor {name: 'Stripe-Custom-Billing-API', vendor: 'Stripe', reliability_sla: '99.99%'})
    CREATE (twilio_api:Vendor {name: 'Twilio-SMS-Gateway', vendor: 'Twilio', reliability_sla: '99.9%'})
    CREATE (auth0_idp:Vendor {name: 'Auth0-Enterprise-Federation', vendor: 'Okta', reliability_sla: '99.99%'})

    // ==========================================
    // 6. STRATEGIC ROADMAPS & COMPLIANCE MANDATES
    // ==========================================
    CREATE (pci_audit:Epic {name: 'PCI-DSS-4.0-Audit', deadline_days: 14, regulatory_fine: 500000, risk: 'catastrophic'})
    CREATE (stripe_v3:Epic {name: 'Stripe-v3-Migration', deadline_days: 21, regulatory_fine: 250000, risk: 'critical'})
    CREATE (kms_rotation:Epic {name: 'Zero-Trust-KMS-Rotation', deadline_days: 45, regulatory_fine: 750000, risk: 'critical'})
    CREATE (kafka_rebalance:Epic {name: 'Kafka-Lag-Optimization', deadline_days: 60, regulatory_fine: 0, risk: 'medium'})

    // ==========================================
    // 7. PERSONNEL (SOCIO-TECHNICAL ACTORS)
    // ==========================================
    CREATE (alex:Person {name: 'Alex', role: 'Principal Infrastructure Architect', timezone: 'UTC-5', cost_per_hr: 160})
    CREATE (sarah:Person {name: 'Sarah', role: 'Staff Backend Architect', timezone: 'UTC-5', cost_per_hr: 145})
    CREATE (elena:Person {name: 'Elena', role: 'Lead AppSec Specialist', timezone: 'UTC-8', cost_per_hr: 155})
    CREATE (marcus:Person {name: 'Marcus', role: 'Principal SRE Lead', timezone: 'UTC+1', cost_per_hr: 150})
    CREATE (chen:Person {name: 'Chen', role: 'Senior Staff Data Eng', timezone: 'UTC-8', cost_per_hr: 140})
    CREATE (priya:Person {name: 'Priya', role: 'VP of Platform Engineering', timezone: 'UTC-5', cost_per_hr: 185})
    CREATE (david:Person {name: 'David', role: 'Senior Payments Engineer', timezone: 'UTC+0', cost_per_hr: 130})
    CREATE (zoe:Person {name: 'Zoe', role: 'Frontend Systems Lead', timezone: 'UTC-5', cost_per_hr: 125})

    // ==========================================
    // RELATIONSHIPS: CUSTOMER SLA BOUNDARIES
    // ==========================================
    CREATE (acme)-[:COVERS_SLA]->(checkout_web)
    CREATE (acme)-[:COVERS_SLA]->(payments_engine)
    CREATE (vertex)-[:COVERS_SLA]->(payments_engine)
    CREATE (vertex)-[:COVERS_SLA]->(auth_mesh)
    CREATE (omni)-[:COVERS_SLA]->(orders_service)

    // RELATIONSHIPS: SERVICE MESH TRAVERSALS (Deep 5-Hop Cascades)
    CREATE (edge_proxy)-[:ROUTES_TO]->(checkout_web)
    CREATE (edge_proxy)-[:ROUTES_TO]->(portal_ui)
    CREATE (checkout_web)-[:DEPENDS_ON {sync: true, weight: 3}]->(orders_service)
    CREATE (checkout_web)-[:DEPENDS_ON {sync: true, weight: 3}]->(auth_mesh)
    CREATE (orders_service)-[:DEPENDS_ON {sync: true, weight: 3}]->(payments_engine)
    CREATE (payments_engine)-[:DEPENDS_ON {sync: false, weight: 1}]->(fraud_pipeline)
    CREATE (payments_engine)-[:DEPENDS_ON {sync: false, weight: 1}]->(notification_broker)
    CREATE (payments_engine)-[:DEPENDS_ON {sync: false, weight: 2}]->(ledger_sink)

    // RELATIONSHIPS: INFRASTRUCTURE BACKBONES
    CREATE (payments_engine)-[:HOSTED_ON]->(k8s_prod)
    CREATE (orders_service)-[:READS_WRITES]->(aurora_db)
    CREATE (payments_engine)-[:READS_WRITES]->(aurora_db)
    CREATE (auth_mesh)-[:CACHES_IN]->(redis_cache)
    CREATE (fraud_pipeline)-[:CONSUMES_FROM]->(kafka_cluster)
    CREATE (ledger_sink)-[:CONSUMES_FROM]->(kafka_cluster)

    // RELATIONSHIPS: VENDOR INTEGRATIONS
    CREATE (payments_engine)-[:INTEGRATES_WITH]->(stripe_api)
    CREATE (auth_mesh)-[:INTEGRATES_WITH]->(auth0_idp)
    CREATE (notification_broker)-[:INTEGRATES_WITH]->(twilio_api)

    // RELATIONSHIPS: EPIC BLOCKERS
    CREATE (stripe_v3)-[:BLOCKS]->(stripe_api)
    CREATE (pci_audit)-[:MANDATES_CHANGE_ON]->(payments_engine)
    CREATE (kms_rotation)-[:BLOCKS]->(aurora_db)
    CREATE (kafka_rebalance)-[:OPTIMIZES]->(kafka_cluster)

    // ==========================================
    // SOCIO-TECHNICAL EDGES: KNOWLEDGE & OWNERSHIP
    // (Notice: Alex is the sole bridge for the Stripe & PCI epics!)
    // ==========================================
    CREATE (alex)-[:KNOWS_ABOUT {depth: 'author', criticality: 5}]->(stripe_v3)
    CREATE (alex)-[:KNOWS_ABOUT {depth: 'sign-off-officer', criticality: 5}]->(pci_audit)
    CREATE (alex)-[:OWNS]->(payments_engine)
    CREATE (alex)-[:ADMINISTERS]->(k8s_prod)

    CREATE (sarah)-[:OWNS]->(checkout_web)
    CREATE (sarah)-[:OWNS]->(orders_service)
    CREATE (elena)-[:OWNS]->(auth_mesh)
    CREATE (elena)-[:KNOWS_ABOUT {depth: 'author', criticality: 5}]->(kms_rotation)

    CREATE (marcus)-[:ONCALL_FOR]->(payments_engine)
    CREATE (marcus)-[:ONCALL_FOR]->(edge_proxy)
    CREATE (chen)-[:OWNS]->(kafka_cluster)
    CREATE (chen)-[:OWNS]->(fraud_pipeline)
    CREATE (david)-[:MAINTAINS]->(ledger_sink)
    CREATE (zoe)-[:OWNS]->(portal_ui)
    CREATE (priya)-[:MANAGES]->(pci_audit)
    CREATE (priya)-[:MANAGES]->(stripe_v3)

    // COLLABORATION NETWORK (For PageRank Successor Computation)
    CREATE (sarah)-[:COLLABORATES_WITH {weight: 8}]->(alex)
    CREATE (marcus)-[:COLLABORATES_WITH {weight: 7}]->(alex)
    CREATE (david)-[:COLLABORATES_WITH {weight: 6}]->(alex)
    CREATE (elena)-[:COLLABORATES_WITH {weight: 5}]->(sarah)
    CREATE (chen)-[:COLLABORATES_WITH {weight: 6}]->(marcus)
    CREATE (zoe)-[:COLLABORATES_WITH {weight: 4}]->(sarah)
    
    // ==========================================
    // 8. ARCHITECTURE DECISION RECORDS (ADRs) & INCIDENT TICKETS
    // ==========================================
    CREATE (adr_pci:Document {
        id: 'ADR-2024-09', 
        title: 'PCI-DSS v4 Hardening Architecture', 
        url: 'https://wiki.internal/adr/2024-09-pci-dss', 
        sha: 'e4b81c2',
        sign_off_date: '2024-09-15'
    })
    CREATE (adr_stripe:Document {
        id: 'ADR-2026-03', 
        title: 'Stripe v3 API Upgrade & Webhook Deadlines', 
        url: 'https://wiki.internal/adr/2026-03-stripe-v3', 
        sha: '8f921a4',
        sign_off_date: '2026-03-01'
    })
    CREATE (ticket_incident:Document {
        id: 'INC-8821', 
        title: 'Post-Mortem: 2025 Payments Gateway Cascade', 
        url: 'https://jira.internal/browse/INC-8821',
        sha: '99d01f1'
    })

    // PROVENANCE EDGES (Track 3 Compliance)
    CREATE (pci_audit)-[:DOCUMENTED_IN]->(adr_pci)
    CREATE (stripe_v3)-[:DOCUMENTED_IN]->(adr_stripe)
    CREATE (payments_engine)-[:REFERENCED_IN]->(ticket_incident)
    CREATE (alex)-[:AUTHORED]->(adr_pci)
    CREATE (alex)-[:AUTHORED]->(adr_stripe)
    """
    g.query(cypher)
    print("✔ Realistic Enterprise Graph seeded: 35+ nodes, 70+ edges.")

if __name__ == "__main__":
    seed_enterprise_graph()