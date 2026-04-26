"""
payments.py — Zariya B2B Mock Payment Gateway
Supports Raast, JazzCash, and NayaPay Arc with animated processing flow.
"""

import time
import uuid
import random
import streamlit as st
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHECKOUT UI
# ══════════════════════════════════════════════════════════════════════════════

def show_checkout(cart: dict, inventory: list) -> None:
    """Render the full checkout + payment flow."""

    if not cart:
        st.info("🛒 Your cart is empty. Add products from the Marketplace.")
        return

    # Build order lines
    order_lines = []
    grand_total = 0.0
    product_map = {p["id"]: p for p in inventory}

    for product_id, qty in cart.items():
        product = product_map.get(product_id)
        if not product:
            continue
        line_total = product["bulk_price"] * qty
        grand_total += line_total
        order_lines.append(
            {
                "Product": product["name"],
                "Company": product["company"],
                "Unit Price (PKR)": f"₨ {product['bulk_price']:,.0f}",
                "Qty": qty,
                "Subtotal (PKR)": f"₨ {line_total:,.0f}",
            }
        )

    # ── Order Summary ─────────────────────────────────────────────────────────
    st.markdown("### 🧾 Order Summary")
    st.markdown(
        """
        <div class="checkout-card">
        """,
        unsafe_allow_html=True,
    )
    st.table(order_lines)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        st.markdown(
            f"""
            <div class="total-box">
                <span class="total-label">Grand Total</span>
                <span class="total-amount">₨ {grand_total:,.0f}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Payment Method ────────────────────────────────────────────────────────
    st.markdown("### 💳 Select Payment Gateway")

    gateway_col1, gateway_col2, gateway_col3 = st.columns(3)

    with gateway_col1:
        st.markdown(
            """
            <div class="gateway-card raast">
                <div class="gateway-logo">🏦</div>
                <div class="gateway-name">Raast</div>
                <div class="gateway-desc">SBP Instant Payment</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with gateway_col2:
        st.markdown(
            """
            <div class="gateway-card jazzcash">
                <div class="gateway-logo">📱</div>
                <div class="gateway-name">JazzCash</div>
                <div class="gateway-desc">Mobile Wallet</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with gateway_col3:
        st.markdown(
            """
            <div class="gateway-card nayapay">
                <div class="gateway-logo">⚡</div>
                <div class="gateway-name">NayaPay Arc</div>
                <div class="gateway-desc">Digital Banking</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    gateway = st.selectbox(
        "Payment Method",
        options=["Raast (SBP)", "JazzCash", "NayaPay Arc"],
        label_visibility="collapsed",
    )

    # Gateway-specific input
    st.markdown("#### Account Details")
    if "JazzCash" in gateway:
        account_input = st.text_input(
            "JazzCash Mobile Number",
            placeholder="03XX-XXXXXXX",
            max_chars=11,
        )
    elif "NayaPay" in gateway:
        account_input = st.text_input(
            "NayaPay IBAN / Account ID",
            placeholder="PK36 NAYP XXXX XXXX XXXX XXXX",
        )
    else:  # Raast
        account_input = st.text_input(
            "Raast ID (Mobile / CNIC / IBAN)",
            placeholder="03XX-XXXXXXX or 35202-XXXXXXX-X",
        )

    st.markdown("")

    pay_btn = st.button(
        f"🚀  Pay ₨ {grand_total:,.0f} via {gateway}",
        use_container_width=True,
        type="primary",
    )

    if pay_btn:
        if not account_input or not account_input.strip():
            st.error("⚠️ Please enter your account / payment details before proceeding.")
            return

        _process_payment(gateway, grand_total, cart, order_lines)


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT PROCESSING ANIMATION
# ══════════════════════════════════════════════════════════════════════════════

def _process_payment(gateway: str, total: float, cart: dict, order_lines: list) -> None:
    """Simulate payment processing with animation."""

    placeholder = st.empty()

    steps = [
        ("🔐", "Establishing secure connection…", 0.6),
        ("📡", f"Connecting to {gateway} gateway…", 0.8),
        ("🔍", "Verifying account details…", 0.7),
        ("💸", "Initiating fund transfer…", 1.0),
        ("✅", "Transaction confirmed!", 0.5),
    ]

    for icon, message, delay in steps:
        placeholder.markdown(
            f"""
            <div class="processing-card">
                <div class="processing-icon">{icon}</div>
                <div class="processing-text">{message}</div>
                <div class="processing-bar"><div class="processing-fill"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(delay)

    placeholder.empty()

    # Generate receipt
    tx_id = f"ZRY-{uuid.uuid4().hex[:8].upper()}"
    tx_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
    ref_no = f"REF{random.randint(100000, 999999)}"

    st.markdown(
        f"""
        <div class="receipt-card">
            <div class="receipt-header">
                <span class="receipt-check">✅</span>
                <h3>Payment Successful!</h3>
                <p>آپ کی ادائیگی کامیابی سے ہوگئی</p>
            </div>
            <div class="receipt-body">
                <div class="receipt-row">
                    <span class="r-label">Transaction ID</span>
                    <span class="r-value tx-id">{tx_id}</span>
                </div>
                <div class="receipt-row">
                    <span class="r-label">Reference No.</span>
                    <span class="r-value">{ref_no}</span>
                </div>
                <div class="receipt-row">
                    <span class="r-label">Gateway</span>
                    <span class="r-value">{gateway}</span>
                </div>
                <div class="receipt-row">
                    <span class="r-label">Amount Paid</span>
                    <span class="r-value amount">₨ {total:,.0f}</span>
                </div>
                <div class="receipt-row">
                    <span class="r-label">Date & Time</span>
                    <span class="r-value">{tx_time}</span>
                </div>
                <div class="receipt-row">
                    <span class="r-label">Status</span>
                    <span class="r-value status-badge">COMPLETED</span>
                </div>
            </div>
            <div class="receipt-footer">
                <p>Thank you for using Zariya B2B • شکریہ</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.balloons()

    # Clear cart after successful payment
    if st.button("🏠 Back to Marketplace", type="secondary"):
        st.session_state["cart"] = {}
        st.session_state["active_tab"] = "marketplace"
        st.rerun()
