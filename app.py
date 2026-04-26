"""
app.py — Zariya B2B Marketplace
Main entry point: Google OAuth gate → KYC → Role-based dashboard.
"""

import os
import streamlit as st

from data_store import get_user, is_registered
from auth import show_registration_form
from wholesaler import show_wholesaler_dashboard
from shopkeeper import show_shopkeeper_dashboard

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Zariya — B2B Marketplace",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Green & White Pakistani Vibe
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Nastaliq+Urdu&display=swap');

/* ── Root tokens ──────────────────────────────────────────────────────────── */
:root {
    --green-dark:   #1B5E20;
    --green-main:   #2E7D32;
    --green-mid:    #388E3C;
    --green-light:  #4CAF50;
    --green-pale:   #E8F5E9;
    --green-soft:   #C8E6C9;
    --white:        #FFFFFF;
    --off-white:    #F9FBF9;
    --text-primary: #1A1A1A;
    --text-muted:   #5C6B5D;
    --border:       #C8E6C9;
    --shadow:       0 4px 24px rgba(27,94,32,0.10);
    --shadow-sm:    0 2px 8px rgba(27,94,32,0.07);
    --radius:       14px;
    --radius-sm:    8px;
}

/* ── Global resets ────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--off-white); }
h1,h2,h3,h4,h5,h6 { color: var(--green-dark); font-weight: 700; }

/* ── Hide Streamlit chrome ────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Primary button override ──────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--green-main), var(--green-light));
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.55rem 1.2rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(46,125,50,0.3);
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(46,125,50,0.35);
}
.stButton > button[kind="secondary"] {
    border: 1.5px solid var(--green-mid);
    color: var(--green-main);
    border-radius: var(--radius-sm);
    font-weight: 500;
    background: white;
    transition: all 0.2s ease;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--green-pale);
}

/* ── Text inputs ──────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border) !important;
    background: white !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--green-light) !important;
    box-shadow: 0 0 0 3px rgba(76,175,80,0.12) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--green-pale);
    border-radius: var(--radius);
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm);
    font-weight: 500;
    color: var(--green-main);
    padding: 0.5rem 1.1rem;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--green-dark) !important;
    font-weight: 700;
    box-shadow: var(--shadow-sm);
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--green-dark) 0%, var(--green-main) 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: white !important;
    border-radius: var(--radius-sm);
    width: 100%;
    margin-top: 0.5rem;
    font-weight: 500;
    transition: background 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
}

/* ── Zariya navbar logo ───────────────────────────────────────────────────── */
.zariya-nav {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1rem 0 1.5rem 0;
}
.zariya-nav-logo {
    font-size: 2.4rem;
}
.zariya-nav-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: white;
    line-height: 1.1;
}
.zariya-nav-urdu {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.75);
    font-family: 'Noto Nastaliq Urdu', serif;
}

/* ── Sidebar profile card ─────────────────────────────────────────────────── */
.sidebar-profile {
    background: rgba(255,255,255,0.12);
    border-radius: var(--radius);
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.2);
}
.sidebar-role-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
}
.sidebar-biz { font-size: 1rem; font-weight: 700; margin: 4px 0; }
.sidebar-loc { font-size: 0.8rem; opacity: 0.8; }
.sidebar-stat { font-size: 0.78rem; opacity: 0.7; margin-top: 6px; }

/* ── KYC header ───────────────────────────────────────────────────────────── */
.kyc-header { text-align: center; padding: 2rem 0 1rem 0; }
.zariya-logo-small { font-size: 2.8rem; font-weight: 800; color: var(--green-dark); letter-spacing: -1px; }
.kyc-sub { color: var(--text-muted); font-size: 1.05rem; }
.kyc-email { color: var(--green-main); font-size: 0.9rem; margin-top: 0.5rem; }

/* ── Portal headers ───────────────────────────────────────────────────────── */
.portal-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 1.2rem 1.6rem;
    border-radius: var(--radius);
    margin-bottom: 1.4rem;
}
.wholesaler-header { background: linear-gradient(135deg, #E8F5E9, #DCEDC8); border-left: 5px solid var(--green-main); }
.shopkeeper-header  { background: linear-gradient(135deg, #E3F2FD, #E8EAF6); border-left: 5px solid #1565C0; }
.portal-icon { font-size: 2.5rem; }
.portal-header h2 { margin: 0; color: var(--text-primary); font-size: 1.4rem; }
.portal-header p  { margin: 0; color: var(--text-muted); font-size: 0.9rem; }

/* ── Product cards ────────────────────────────────────────────────────────── */
.product-card {
    background: white;
    border-radius: var(--radius);
    padding: 1.2rem;
    border: 1.5px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: all 0.25s ease;
    min-height: 220px;
    margin-bottom: 0.3rem;
}
.product-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
    border-color: var(--green-light);
}
.product-emoji { font-size: 2.2rem; margin-bottom: 6px; }
.product-company { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.product-name { font-size: 0.92rem; font-weight: 600; color: var(--text-primary); margin: 4px 0 6px 0; line-height: 1.3; }
.product-price { font-size: 1.25rem; font-weight: 800; color: var(--green-dark); }
.product-unit  { font-size: 0.75rem; color: var(--text-muted); }
.product-stock { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }
.cat-badge {
    background: var(--green-pale);
    color: var(--green-dark);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
}
.in-cart-badge {
    background: #FFF3E0;
    color: #E65100;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 5px;
}

/* ── AI Guru ──────────────────────────────────────────────────────────────── */
.ai-guru-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1rem 1.4rem;
    background: linear-gradient(135deg, #E8EAF6, #EDE7F6);
    border-radius: var(--radius);
    border-left: 5px solid #5C6BC0;
    margin-bottom: 1rem;
}
.guru-avatar { font-size: 2.4rem; }
.guru-info h3 { margin: 0; font-size: 1.15rem; color: #283593; }
.guru-info p  { margin: 0; color: #5C6B9C; font-size: 0.85rem; }
.guru-badge   { margin-left: auto; font-size: 0.82rem; font-weight: 600; }
.chat-empty   { text-align: center; padding: 3rem; color: var(--text-muted); }

/* ── Checkout & Payment ───────────────────────────────────────────────────── */
.checkout-card {
    background: white;
    border-radius: var(--radius);
    padding: 1.4rem;
    border: 1.5px solid var(--border);
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.total-box {
    background: var(--green-pale);
    border-radius: var(--radius-sm);
    padding: 0.8rem 1rem;
    text-align: right;
    border: 1.5px solid var(--green-soft);
}
.total-label  { display: block; font-size: 0.78rem; color: var(--text-muted); font-weight: 600; }
.total-amount { display: block; font-size: 1.5rem; font-weight: 800; color: var(--green-dark); }

/* ── Gateway cards ────────────────────────────────────────────────────────── */
.gateway-card {
    text-align: center;
    padding: 1.2rem 0.8rem;
    border-radius: var(--radius);
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 0.5rem;
}
.raast   { background: #E3F2FD; border-color: #1565C0; }
.jazzcash{ background: #FFF3E0; border-color: #E65100; }
.nayapay { background: #EDE7F6; border-color: #6A1B9A; }
.gateway-logo { font-size: 2rem; margin-bottom: 6px; }
.gateway-name { font-weight: 700; font-size: 1rem; }
.gateway-desc { font-size: 0.77rem; color: var(--text-muted); }

/* ── Processing animation ─────────────────────────────────────────────────── */
.processing-card {
    text-align: center;
    padding: 2.5rem;
    background: white;
    border-radius: var(--radius);
    border: 2px solid var(--green-soft);
    box-shadow: var(--shadow);
}
.processing-icon { font-size: 3rem; margin-bottom: 0.8rem; }
.processing-text { font-size: 1.1rem; font-weight: 600; color: var(--green-main); margin-bottom: 1rem; }
.processing-bar  { background: var(--green-pale); border-radius: 10px; height: 6px; overflow: hidden; }
.processing-fill {
    height: 100%;
    width: 60%;
    background: linear-gradient(90deg, var(--green-main), var(--green-light));
    border-radius: 10px;
    animation: slide 1s infinite alternate;
}
@keyframes slide { from { transform: translateX(-30%); } to { transform: translateX(80%); } }

/* ── Receipt card ─────────────────────────────────────────────────────────── */
.receipt-card {
    max-width: 520px;
    margin: 1rem auto;
    background: white;
    border-radius: var(--radius);
    border: 2px solid var(--green-soft);
    box-shadow: var(--shadow);
    overflow: hidden;
}
.receipt-header {
    background: linear-gradient(135deg, var(--green-main), var(--green-light));
    color: white;
    text-align: center;
    padding: 1.8rem 1rem 1.4rem;
}
.receipt-check { font-size: 2.8rem; }
.receipt-header h3 { color: white !important; margin: 0.5rem 0 0.2rem; font-size: 1.4rem; }
.receipt-header p  { color: rgba(255,255,255,0.85); margin: 0; font-size: 0.9rem; }
.receipt-body  { padding: 1.2rem 1.6rem; }
.receipt-row   { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--border); }
.receipt-row:last-child { border-bottom: none; }
.r-label { font-size: 0.82rem; color: var(--text-muted); font-weight: 500; }
.r-value { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.tx-id   { font-family: monospace; background: var(--green-pale); padding: 2px 8px; border-radius: 4px; color: var(--green-dark); }
.amount  { font-size: 1.15rem; font-weight: 800; color: var(--green-dark); }
.status-badge {
    background: #E8F5E9;
    color: #2E7D32;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.receipt-footer {
    text-align: center;
    padding: 0.8rem;
    background: var(--green-pale);
    font-size: 0.82rem;
    color: var(--text-muted);
}

/* ── Inventory badges ─────────────────────────────────────────────────────── */
.badge-seeded { background:#FFF9C4; color:#F57F17; border-radius:20px; padding:3px 10px; font-size:0.75rem; font-weight:600; }
.badge-mine   { background:#E8F5E9; color:#2E7D32; border-radius:20px; padding:3px 10px; font-size:0.75rem; font-weight:600; }

/* ── Login screen ─────────────────────────────────────────────────────────── */
.login-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    text-align: center;
    gap: 1rem;
}
.login-logo-big { font-size: 4rem; }
.login-title { font-size: 3rem; font-weight: 900; color: var(--green-dark); letter-spacing: -2px; margin: 0; }
.login-urdu  { font-size: 1.4rem; color: var(--text-muted); font-family: 'Noto Nastaliq Urdu', serif; }
.login-desc  { font-size: 1rem; color: var(--text-muted); max-width: 440px; line-height: 1.6; }
.login-features {
    display: flex;
    gap: 2rem;
    margin: 1rem 0;
    flex-wrap: wrap;
    justify-content: center;
}
.login-feature {
    background: white;
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.4rem;
    text-align: center;
    min-width: 130px;
    box-shadow: var(--shadow-sm);
}
.login-feature .lf-icon { font-size: 1.8rem; }
.login-feature .lf-text { font-size: 0.82rem; color: var(--text-muted); margin-top: 4px; font-weight: 500; }
</style>
""",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE OAUTH GATE
# ══════════════════════════════════════════════════════════════════════════════

def _oauth_configured() -> bool:
    """Return True if Google OAuth secrets are present in secrets.toml."""
    try:
        return bool(st.secrets.get("auth", {}).get("google", {}).get("client_id"))
    except Exception:
        return False


def _show_login_page() -> None:
    """Landing page — Google OAuth in production, Demo Mode locally."""
    st.markdown(
        """
        <div class="login-hero">
            <div class="login-logo-big">🌿</div>
            <h1 class="login-title">Zariya</h1>
            <p class="login-urdu">آپ کا کاروباری ساتھی</p>
            <p class="login-desc">
                Pakistan's premier B2B marketplace connecting Wholesalers and Shopkeepers
                — powered by AI, built for the FMCG ecosystem.
            </p>
            <div class="login-features">
                <div class="login-feature"><div class="lf-icon">🏭</div><div class="lf-text">Wholesale Listings</div></div>
                <div class="login-feature"><div class="lf-icon">🤖</div><div class="lf-text">AI Guru</div></div>
                <div class="login-feature"><div class="lf-icon">💳</div><div class="lf-text">Raast · JazzCash</div></div>
                <div class="login-feature"><div class="lf-icon">📍</div><div class="lf-text">Pakistan-wide</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if _oauth_configured():
        # ── Production: real Google OAuth ─────────────────────────────────────
        st.login("google")
    else:
        # ── Demo Mode: instant access without credentials ──────────────────────
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align:center; margin-bottom:1rem;'>
                <span style='background:#FFF9C4; color:#F57F17; border-radius:20px;
                             padding:6px 18px; font-size:0.85rem; font-weight:700;'>
                    🔑 Demo Mode — Google OAuth not configured
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.markdown("**Enter as a Demo User:**")
            demo_role = st.radio(
                "Select role",
                ["🏪  Shopkeeper (Demo)", "🏭  Wholesaler (Demo)"],
                label_visibility="collapsed",
                horizontal=True,
            )
            if st.button("🚀  Enter Zariya Marketplace", use_container_width=True, type="primary"):
                role_key = "Wholesaler" if "Wholesaler" in demo_role else "Shopkeeper"
                email = f"demo_{role_key.lower()}@zariya.demo"
                st.session_state["demo_email"] = email
                st.session_state["demo_name"] = f"Demo {role_key}"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def _render_sidebar(email: str, profile: dict) -> None:
    with st.sidebar:
        # Zariya brand
        st.markdown(
            """
            <div class="zariya-nav">
                <div class="zariya-nav-logo">🌿</div>
                <div>
                    <div class="zariya-nav-title">Zariya</div>
                    <div class="zariya-nav-urdu">آپ کا کاروباری ساتھی</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        role = profile.get("role", "User")
        role_icon = "🏭" if role == "Wholesaler" else "🏪"
        biz = profile.get("business_name", "—")
        city = profile.get("city", "")
        area = profile.get("area_name", "")
        province = profile.get("province", "")
        loc_parts = [x for x in [area, city, province] if x]
        loc_str = ", ".join(loc_parts[:2]) if loc_parts else "—"

        st.markdown(
            f"""
            <div class="sidebar-profile">
                <div class="sidebar-role-badge">{role_icon} {role}</div>
                <div class="sidebar-biz">{biz}</div>
                <div class="sidebar-loc">📍 {loc_str}</div>
                <div class="sidebar-stat">
                    {profile.get('business_type', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"**👤** {profile.get('display_name', email)}")
        st.markdown(f"**✉️** `{email}`")
        st.markdown(f"**🪪** CNIC: `{profile.get('cnic', '—')}`")

        st.markdown("---")

        # Cart summary for shopkeepers
        if role == "Shopkeeper":
            cart = st.session_state.get("cart", {})
            cart_count = sum(cart.values())
            if cart_count:
                st.markdown(f"🛒 **Cart:** {cart_count} item(s)")
                if st.button("🗑️ Clear Cart"):
                    st.session_state["cart"] = {}
                    st.rerun()

        if st.button("🚪 Sign Out"):
            # Clear demo session
            st.session_state.pop("demo_email", None)
            st.session_state.pop("demo_name", None)
            # Clear app state
            for key in ["cart", "chat_history", "kyc_complete", "user_profile"]:
                st.session_state.pop(key, None)
            # Google OAuth logout (no-op if not configured)
            try:
                st.logout()
            except Exception:
                pass
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── 1. Resolve identity (OAuth or Demo Mode) ──────────────────────────────
    email = ""
    display_name = ""

    # Check real Google OAuth first
    try:
        if st.user.is_logged_in:
            email = str(st.user.get("email", ""))
            display_name = str(st.user.get("name", email.split("@")[0]))
    except AttributeError:
        pass

    # Fall back to Demo Mode session
    if not email:
        email = st.session_state.get("demo_email", "")
        display_name = st.session_state.get("demo_name", "Demo User")

    if not email:
        _show_login_page()
        st.stop()

    # ── 2. KYC gate ───────────────────────────────────────────────────────────
    if not is_registered(email):
        show_registration_form(email, display_name)
        st.stop()

    # ── 3. Load profile ───────────────────────────────────────────────────────
    profile = get_user(email)
    if not profile:
        st.error("Profile not found. Please contact support.")
        st.stop()

    # ── 4. Sidebar ────────────────────────────────────────────────────────────
    _render_sidebar(email, profile)

    # ── 5. Route to role-based dashboard ──────────────────────────────────────
    role = profile.get("role", "Shopkeeper")
    if role == "Wholesaler":
        show_wholesaler_dashboard(email, profile)
    else:
        show_shopkeeper_dashboard(email, profile)


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
