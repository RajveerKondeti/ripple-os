APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography & Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e2e8f0;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Core Canvas Background */
    .stApp {
        background-color: #070a12;
    }

    /* Remove Streamlit Default Header and Spacing */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: #0a0f1d !important;
        border-right: 1px solid #1a2333;
    }

    /* Seamless PyVis Iframe Container (No White Borders) */
    iframe {
        border: 1px solid #1a2333 !important;
        border-radius: 12px !important;
        background-color: #0a0f1d !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6) !important;
    }

    /* Executive Topbar */
    .exec-topbar {
        background: linear-gradient(180deg, #0f172a 0%, #0a0f1d 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
    }
    .brand-title span {
        color: #38bdf8;
    }
    .brand-subtitle {
        font-size: 12px;
        color: #64748b;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Stat Badges */
    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #0d1527;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 12px;
    }
    .stat-pill-label {
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 10px;
        letter-spacing: 0.05em;
    }
    .stat-pill-val {
        color: #f8fafc;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Executive Metric Card */
    /* Executive Metric Card */
    .kpi-tile {
        background: #0d1527;
        border: 1px solid #1a2333;
        border-radius: 10px;
        padding: 12px 14px;
        transition: border-color 0.2s ease;
        min-width: 0;
    }
    .kpi-tile:hover {
        border-color: #2563eb;
    }
    .kpi-label {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 800;
        margin-top: 4px;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Alert Banners */
    .exec-banner {
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border-left: 4px solid;
    }
    .banner-danger {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-left-color: #ef4444;
    }
    .banner-title {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #ef4444;
    }
    .banner-head {
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 3px;
    }
    .banner-desc {
        font-size: 13px;
        color: #cbd5e1;
        margin-top: 4px;
        line-height: 1.5;
    }

    /* Propagation Breadcrumb Pills */
    .flow-pill {
        display: inline-flex;
        align-items: center;
        background: #0a0f1d;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 3px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        color: #e2e8f0;
    }

    /* Commander Box */
    .officer-box {
        background: #0d1527;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .officer-avatar {
        width: 42px;
        height: 42px;
        border-radius: 8px;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 18px;
        color: white;
    }

    /* Tab Bar Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #0a0f1d;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #1a2333;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        color: #64748b;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }
</style>
"""