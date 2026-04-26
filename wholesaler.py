"""
wholesaler.py — Zariya B2B Wholesaler Portal
Add products, manage inventory with live edit/delete actions.
"""

import streamlit as st
from data_store import (
    load_inventory,
    add_product,
    remove_product,
    update_product,
    get_products_by_wholesaler,
)

PRESET_COMPANIES = [
    "Unilever",
    "Nestlé",
    "National Foods",
    "Shan Foods",
    "Engro",
    "P&G Pakistan",
    "Colgate-Palmolive",
    "Reckitt Pakistan",
    "Dalda Foods",
    "English Biscuit Manufacturers (EBM)",
    "Other (Enter Manually)",
]

CATEGORIES = [
    "Beverages",
    "Spices & Masala",
    "Condiments",
    "Dairy",
    "Household",
    "Personal Care",
    "Snacks & Confectionery",
    "Cooking Oil & Ghee",
    "Flour & Grain",
    "Baby Products",
    "Other",
]

UNITS = ["Pack", "Box", "Carton", "Bottle", "Tin", "Bag", "Jar", "Dozen", "Piece", "Kg"]


# ══════════════════════════════════════════════════════════════════════════════
# WHOLESALER DASHBOARD ENTRY
# ══════════════════════════════════════════════════════════════════════════════

def show_wholesaler_dashboard(user_email: str, user_profile: dict) -> None:
    business = user_profile.get("business_name", "Your Business")

    st.markdown(
        f"""
        <div class="portal-header wholesaler-header">
            <span class="portal-icon">🏭</span>
            <div>
                <h2>Wholesaler Portal</h2>
                <p>{business} — Manage your product catalogue</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["➕  Add New Product", "📦  Manage Inventory"])

    with tab1:
        _show_add_product(user_email, user_profile)

    with tab2:
        _show_manage_inventory(user_email)


# ══════════════════════════════════════════════════════════════════════════════
# ADD PRODUCT FORM
# ══════════════════════════════════════════════════════════════════════════════

def _show_add_product(user_email: str, user_profile: dict) -> None:
    st.markdown("#### 📋 New Product Listing")

    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            product_name = st.text_input(
                "Product Name *", placeholder="e.g. Lipton Yellow Label Tea 190g"
            )
            company_choice = st.selectbox("Company / Brand *", PRESET_COMPANIES)
            custom_company = ""
            if company_choice == "Other (Enter Manually)":
                custom_company = st.text_input("Enter Company Name *", placeholder="e.g. Haleeb Foods")

            category = st.selectbox("Category *", CATEGORIES)

        with col2:
            bulk_price = st.number_input(
                "Bulk Price (PKR) *",
                min_value=1.0,
                max_value=9_999_999.0,
                value=100.0,
                step=5.0,
                format="%.0f",
                help="Price per unit for bulk orders",
            )
            stock_quantity = st.number_input(
                "Stock Quantity *",
                min_value=1,
                max_value=999_999,
                value=100,
                step=10,
                help="Available units in stock",
            )
            unit = st.selectbox("Unit of Measure", UNITS)

        description = st.text_area(
            "Product Description (optional)",
            placeholder="Key features, pack sizes, expiry info…",
            max_chars=300,
        )

        submitted = st.form_submit_button(
            "🚀  List Product on Zariya Marketplace",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            errors = []

            if not product_name.strip():
                errors.append("Product Name is required.")

            final_company = (
                custom_company.strip()
                if company_choice == "Other (Enter Manually)"
                else company_choice
            )
            if not final_company:
                errors.append("Company / Brand name is required.")

            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                product = {
                    "name": product_name.strip(),
                    "company": final_company,
                    "category": category,
                    "bulk_price": bulk_price,
                    "stock_quantity": int(stock_quantity),
                    "unit": unit,
                    "description": description.strip(),
                    "added_by": user_email,
                    "added_by_name": user_profile.get("business_name", "Unknown"),
                }
                pid = add_product(product)
                st.success(f"✅ **{product_name}** listed successfully! (ID: `{pid}`)")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MANAGE INVENTORY
# ══════════════════════════════════════════════════════════════════════════════

def _show_manage_inventory(user_email: str) -> None:
    st.markdown("#### 📦 Your Product Listings")

    my_products = get_products_by_wholesaler(user_email)

    # Also show system-seeded products for demo
    all_inventory = load_inventory()
    seeded = [p for p in all_inventory if p.get("added_by") == "system"]
    combined = my_products + seeded

    if not combined:
        st.info("📭 You haven't listed any products yet. Use the **Add New Product** tab to get started.")
        return

    # ── Filters ──────────────────────────────────────────────────────────────
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        company_filter = st.selectbox(
            "Filter by Company",
            ["All Companies"] + sorted({p.get("company", "") for p in combined}),
        )
    with fcol2:
        cat_filter = st.selectbox(
            "Filter by Category",
            ["All Categories"] + sorted({p.get("category", "") for p in combined}),
        )

    filtered = [
        p
        for p in combined
        if (company_filter == "All Companies" or p.get("company") == company_filter)
        and (cat_filter == "All Categories" or p.get("category") == cat_filter)
    ]

    st.markdown(f"**{len(filtered)} product(s) found**")
    st.divider()

    # ── Product cards with edit/delete ────────────────────────────────────────
    for product in filtered:
        pid = product.get("id", "")
        is_seeded = product.get("added_by") == "system"
        is_mine = product.get("added_by") == user_email

        with st.expander(
            f"🏷️  {product.get('name', 'Unknown')}  ·  {product.get('company', '')}  ·  ₨ {product.get('bulk_price', 0):,.0f}",
            expanded=False,
        ):
            ecol1, ecol2, ecol3, ecol4 = st.columns([3, 2, 2, 1])

            with ecol1:
                st.markdown(f"**Category:** {product.get('category', '—')}")
                st.markdown(f"**Unit:** {product.get('unit', '—')}")
                if product.get("description"):
                    st.markdown(f"*{product['description']}*")

            with ecol2:
                st.metric("Bulk Price", f"₨ {product.get('bulk_price', 0):,.0f}")

            with ecol3:
                st.metric("Stock", f"{product.get('stock_quantity', 0):,} units")

            with ecol4:
                if is_seeded:
                    st.markdown(
                        "<span class='badge-seeded'>🌱 Pre-loaded</span>",
                        unsafe_allow_html=True,
                    )
                elif is_mine:
                    st.markdown(
                        "<span class='badge-mine'>✏️ Mine</span>",
                        unsafe_allow_html=True,
                    )

            # Only allow edit/delete on own products
            if is_mine:
                st.markdown("---")
                action_col1, action_col2, _, new_price_col, new_stock_col = st.columns([1, 1, 2, 2, 2])

                with new_price_col:
                    new_price = st.number_input(
                        "New Price (PKR)",
                        min_value=1.0,
                        value=float(product.get("bulk_price", 100)),
                        step=5.0,
                        format="%.0f",
                        key=f"price_{pid}",
                    )
                with new_stock_col:
                    new_stock = st.number_input(
                        "New Stock",
                        min_value=0,
                        value=int(product.get("stock_quantity", 0)),
                        step=10,
                        key=f"stock_{pid}",
                    )
                with action_col1:
                    if st.button("💾 Update", key=f"upd_{pid}", use_container_width=True):
                        if update_product(pid, {"bulk_price": new_price, "stock_quantity": new_stock}):
                            st.success("Updated!")
                            st.rerun()
                        else:
                            st.error("Update failed.")
                with action_col2:
                    if st.button("🗑️ Remove", key=f"del_{pid}", use_container_width=True, type="secondary"):
                        if remove_product(pid):
                            st.warning("Product removed.")
                            st.rerun()
                        else:
                            st.error("Remove failed.")
