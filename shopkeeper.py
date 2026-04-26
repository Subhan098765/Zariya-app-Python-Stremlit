"""
shopkeeper.py — Zariya B2B Shopkeeper Portal
AI Guru (Gemini 1.5 Flash) + searchable Marketplace + Cart & Checkout.
"""

import os
import streamlit as st

from data_store import load_inventory
from payments import show_checkout

# ── Gemini setup ──────────────────────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types

    # Try st.secrets first, then os.getenv
    _GEMINI_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    
    if _GEMINI_KEY:
        _genai_client = genai.Client(api_key=_GEMINI_KEY)
        _GEMINI_AVAILABLE = True
    else:
        _genai_client = None
        _GEMINI_AVAILABLE = False
except Exception:
    _genai_client = None
    _GEMINI_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# SHOPKEEPER DASHBOARD ENTRY
# ══════════════════════════════════════════════════════════════════════════════

def show_shopkeeper_dashboard(user_email: str, user_profile: dict) -> None:
    business = user_profile.get("business_name", "Your Shop")
    city = user_profile.get("city", "")

    st.markdown(
        f"""
        <div class="portal-header shopkeeper-header">
            <span class="portal-icon">🏪</span>
            <div>
                <h2>Shopkeeper Portal</h2>
                <p>{business}{(' — ' + city) if city else ''}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cart_count = sum(st.session_state.get("cart", {}).values())
    tab_labels = [
        "🤖  AI Guru",
        f"🛒  Marketplace{'  ·  🛍️ ' + str(cart_count) if cart_count else ''}",
        "💳  Checkout",
    ]

    tab1, tab2, tab3 = st.tabs(tab_labels)

    with tab1:
        _show_ai_guru(user_profile)

    with tab2:
        _show_marketplace()

    with tab3:
        inventory = load_inventory()
        show_checkout(st.session_state.get("cart", {}), inventory)


# ══════════════════════════════════════════════════════════════════════════════
# AI GURU
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
You are Zariya AI Guru — a smart B2B supply chain assistant for Pakistani shopkeepers and retailers.
You have deep knowledge of:
- Pakistani FMCG brands: Unilever, Nestlé, National Foods, Shan Foods, Engro, EBM, Tapal, Haleeb, Noon, Dalda
- Popular Pakistani grocery items and their typical wholesale/retail prices in PKR
- Stock recommendations based on shop type, city, and season
- Local market trends in Karachi, Lahore, Islamabad, Rawalpindi, Peshawar, Quetta, Multan, Faisalabad
- Payment systems: Raast, JazzCash, EasyPaisa, NayaPay

IMPORTANT RULES:
- Always answer in the same language as the question (Urdu or English or Roman Urdu)
- Provide specific PKR prices when asked
- When asked "who has the cheapest price for X?", mention the typical price range and which company offers it
- Keep answers concise, practical, and business-focused
- When suggesting stock for a shop, consider the city, shop type, and budget
- You help shopkeepers make smarter buying decisions
""".strip()


def _get_gemini_response(user_message: str, chat_history: list) -> str:
    """Get a response from Gemini 2.0 Flash."""
    if not _GEMINI_AVAILABLE or _genai_client is None:
        return (
            "⚠️ AI Guru is currently offline. Please set the `GEMINI_API_KEY` environment variable to enable it.\n\n"
            "**Sample answer:** For Shan Biryani Masala (60g), typical wholesale prices range from ₨ 110–130 per packet. "
            "Shan Foods is the brand; you can buy from local distributors or through Zariya marketplace."
        )

    try:
        # Build history for multi-turn conversation
        contents = []
        for msg in chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(genai_types.Content(role=role, parts=[genai_types.Part(text=msg["content"])]))

        # Add the current user message
        contents.append(genai_types.Content(role="user", parts=[genai_types.Part(text=user_message)]))

        # Try 1.5 Flash first, then fallback to 2.0
        try:
            model_id = "gemini-1.5-flash"
            response = _genai_client.models.generate_content(
                model=model_id,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0.7,
                ),
            )
        except Exception:
            model_id = "gemini-2.0-flash"
            response = _genai_client.models.generate_content(
                model=model_id,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0.7,
                ),
            )
        return response.text

    except Exception as e:
        return f"⚠️ AI Guru encountered an error: {str(e)}\n\nPlease try again or check your API key."


def _show_ai_guru(user_profile: dict) -> None:
    city = user_profile.get("city", "your city")
    business_type = user_profile.get("business_type", "shop")

    st.markdown(
        f"""
        <div class="ai-guru-header">
            <div class="guru-avatar">🤖</div>
            <div class="guru-info">
                <h3>Zariya AI Guru</h3>
                <p>Your smart B2B assistant — کاروبار کا ذہین ساتھی</p>
            </div>
            <div class="guru-badge">{'🟢 Online' if _GEMINI_AVAILABLE else '🔴 Offline'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick suggestion buttons
    st.markdown("**💡 Quick Questions:**")
    suggestions = [
        f"Who has the cheapest price for Shan Biryani Masala?",
        f"Suggest stock for a {business_type} in {city}",
        "What are the best-selling FMCG products this season?",
        "Compare Lipton vs Tapal tea wholesale prices",
        "مجھے چھوٹی دکان کے لیے stock کی فہرست بتائیں",
    ]

    sug_cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        with sug_cols[i]:
            if st.button(sug[:35] + ("…" if len(sug) > 35 else ""), key=f"sug_{i}", use_container_width=True):
                if "chat_history" not in st.session_state:
                    st.session_state["chat_history"] = []
                st.session_state["chat_history"].append({"role": "user", "content": sug})
                with st.spinner("AI Guru is thinking…"):
                    reply = _get_gemini_response(sug, st.session_state["chat_history"])
                st.session_state["chat_history"].append({"role": "model", "content": reply})
                st.rerun()

    st.divider()

    # Chat history display
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if not st.session_state["chat_history"]:
        st.markdown(
            """
            <div class="chat-empty">
                <p>👋 السلام علیکم! I'm your AI Guru.</p>
                <p>Ask me anything about prices, stock recommendations, or market trends!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🏪"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask AI Guru… (English or Urdu)")

    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.spinner("🤔 AI Guru is thinking…"):
            reply = _get_gemini_response(user_input, st.session_state["chat_history"])
        st.session_state["chat_history"].append({"role": "model", "content": reply})
        st.rerun()

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE
# ══════════════════════════════════════════════════════════════════════════════

CATEGORY_EMOJIS = {
    "Beverages": "☕",
    "Spices & Masala": "🌶️",
    "Condiments": "🍯",
    "Dairy": "🥛",
    "Household": "🧹",
    "Personal Care": "🧴",
    "Snacks & Confectionery": "🍪",
    "Cooking Oil & Ghee": "🫙",
    "Flour & Grain": "🌾",
    "Baby Products": "👶",
    "Other": "📦",
}

COMPANY_COLORS = {
    "Unilever": "#1565C0",
    "Nestlé": "#2E7D32",
    "National Foods": "#E65100",
    "Shan Foods": "#C62828",
    "Engro": "#4527A0",
}


def _show_marketplace() -> None:
    st.markdown("#### 🛒 Zariya Marketplace")

    inventory = load_inventory()

    if not inventory:
        st.info("📭 The marketplace is currently empty. Wholesalers will add products soon!")
        return

    # ── Search & Filter bar ───────────────────────────────────────────────────
    search_col, company_col, cat_col, sort_col = st.columns([3, 2, 2, 2])

    with search_col:
        search_q = st.text_input(
            "🔍 Search products…",
            placeholder="e.g. Shan Biryani, Surf Excel…",
            label_visibility="collapsed",
        )
    with company_col:
        companies = ["All Companies"] + sorted({p.get("company", "") for p in inventory})
        company_filter = st.selectbox("Company", companies, label_visibility="collapsed")
    with cat_col:
        categories = ["All Categories"] + sorted({p.get("category", "") for p in inventory})
        cat_filter = st.selectbox("Category", categories, label_visibility="collapsed")
    with sort_col:
        sort_by = st.selectbox(
            "Sort",
            ["Price: Low → High", "Price: High → Low", "Name A → Z", "Stock: High → Low"],
            label_visibility="collapsed",
        )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = inventory

    if search_q:
        q = search_q.lower()
        filtered = [
            p
            for p in filtered
            if q in p.get("name", "").lower()
            or q in p.get("company", "").lower()
            or q in p.get("category", "").lower()
        ]

    if company_filter != "All Companies":
        filtered = [p for p in filtered if p.get("company") == company_filter]

    if cat_filter != "All Categories":
        filtered = [p for p in filtered if p.get("category") == cat_filter]

    # Sort
    if sort_by == "Price: Low → High":
        filtered.sort(key=lambda x: x.get("bulk_price", 0))
    elif sort_by == "Price: High → Low":
        filtered.sort(key=lambda x: x.get("bulk_price", 0), reverse=True)
    elif sort_by == "Name A → Z":
        filtered.sort(key=lambda x: x.get("name", ""))
    elif sort_by == "Stock: High → Low":
        filtered.sort(key=lambda x: x.get("stock_quantity", 0), reverse=True)

    # ── Results summary ────────────────────────────────────────────────────────
    st.markdown(f"**{len(filtered)} product(s) available**")

    if not filtered:
        st.warning("No products match your search. Try different filters.")
        return

    # ── Product grid ──────────────────────────────────────────────────────────
    if "cart" not in st.session_state:
        st.session_state["cart"] = {}

    cols_per_row = 3
    for row_start in range(0, len(filtered), cols_per_row):
        row_products = filtered[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, product in zip(cols, row_products):
            pid = product.get("id", "")
            company = product.get("company", "")
            category = product.get("category", "Other")
            emoji = CATEGORY_EMOJIS.get(category, "📦")
            company_color = COMPANY_COLORS.get(company, "#388E3C")
            in_cart = st.session_state["cart"].get(pid, 0)

            with col:
                st.markdown(
                    f"""
                    <div class="product-card">
                        <div class="product-emoji">{emoji}</div>
                        <div class="product-company" style="color:{company_color};">{company}</div>
                        <div class="product-name">{product.get('name', '')}</div>
                        <div class="product-meta">
                            <span class="cat-badge">{category}</span>
                        </div>
                        <div class="product-price">₨ {product.get('bulk_price', 0):,.0f}</div>
                        <div class="product-unit">per {product.get('unit', 'unit')}</div>
                        <div class="product-stock">📦 {product.get('stock_quantity', 0):,} in stock</div>
                        {'<div class="in-cart-badge">🛒 ' + str(in_cart) + ' in cart</div>' if in_cart else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quantity + Add to cart
                qty_col, btn_col = st.columns([2, 3])
                with qty_col:
                    qty = st.number_input(
                        "Qty",
                        min_value=1,
                        max_value=int(product.get("stock_quantity", 999)),
                        value=max(1, in_cart),
                        step=1,
                        key=f"qty_{pid}",
                        label_visibility="collapsed",
                    )
                with btn_col:
                    btn_label = f"{'Update' if in_cart else 'Add to'} Cart 🛒"
                    if st.button(btn_label, key=f"cart_{pid}", use_container_width=True, type="primary"):
                        st.session_state["cart"][pid] = qty
                        st.toast(f"✅ {product.get('name', '')} added to cart!", icon="🛒")
                        st.rerun()
