"""
auth.py — Zariya B2B Authentication & KYC Registration
Google OAuth gate + mandatory first-time registration flow.
"""

import re
import streamlit as st
from data_store import register_user, get_user

# ── Pakistani Provinces ───────────────────────────────────────────────────────
PROVINCES = [
    "Punjab",
    "Sindh",
    "KPK (Khyber Pakhtunkhwa)",
    "Balochistan",
    "Islamabad (ICT)",
    "Gilgit-Baltistan",
    "AJK (Azad Jammu & Kashmir)",
]

BUSINESS_TYPES = [
    "General Store / Kiryana",
    "Supermarket / Mini-Mart",
    "Pharmacy / Medical Store",
    "Wholesale Distributor",
    "Cash & Carry",
    "Departmental Store",
    "Restaurant / Food Service",
    "E-Commerce / Online Store",
    "Other",
]

CNIC_PATTERN = re.compile(r"^\d{5}-\d{7}-\d{1}$")


def validate_cnic(cnic: str) -> bool:
    return bool(CNIC_PATTERN.match(cnic.strip()))


# ══════════════════════════════════════════════════════════════════════════════
# KYC REGISTRATION FORM
# ══════════════════════════════════════════════════════════════════════════════

def show_registration_form(email: str, display_name: str) -> None:
    """Render the mandatory KYC registration screen."""

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="kyc-header">
            <div class="zariya-logo-small">🌿 Zariya</div>
            <h2>Welcome! Complete Your Profile</h2>
            <p class="kyc-sub">آپ کا کاروباری سفر یہاں سے شروع ہوتا ہے</p>
            <p class="kyc-email">Logged in as <strong>{email}</strong></p>
        </div>
        """.replace("{email}", email),
        unsafe_allow_html=True,
    )

    st.divider()

    with st.form("kyc_form", clear_on_submit=False):
        # ── Role ──────────────────────────────────────────────────────────────
        st.markdown("#### 👤 Select Your Role")
        col1, col2 = st.columns(2)
        with col1:
            role_option = st.radio(
                "I am a:",
                options=["🏭  Wholesaler / Distributor", "🏪  Shopkeeper / Retailer"],
                label_visibility="collapsed",
            )
        role = "Wholesaler" if "Wholesaler" in role_option else "Shopkeeper"

        st.markdown("---")

        # ── Identity ─────────────────────────────────────────────────────────
        st.markdown("#### 🪪 Identity Verification (KYC)")
        cnic = st.text_input(
            "CNIC Number",
            placeholder="XXXXX-XXXXXXX-X  (e.g. 35202-1234567-8)",
            help="Pakistan National Identity Card — 13-digit format",
        )

        st.markdown("---")

        # ── Business Info ─────────────────────────────────────────────────────
        st.markdown("#### 🏢 Business Information")
        col3, col4 = st.columns(2)
        with col3:
            business_name = st.text_input(
                "Shop / Mall / Company Name *",
                placeholder="e.g. Al-Razzaq Traders",
            )
        with col4:
            business_type = st.selectbox("Business Type *", BUSINESS_TYPES)

        st.markdown("---")

        # ── Location ─────────────────────────────────────────────────────────
        st.markdown("#### 📍 Detailed Location")
        col5, col6 = st.columns(2)
        with col5:
            province = st.selectbox("Province / Territory *", PROVINCES)
        with col6:
            city = st.text_input("City *", placeholder="e.g. Lahore, Karachi, Peshawar")

        col7, col8 = st.columns(2)
        with col7:
            area_name = st.text_input("Area / Locality *", placeholder="e.g. Gulberg, F-7, Saddar")
        with col8:
            landmark = st.text_input(
                "Local Landmark *",
                placeholder="e.g. Near Al-Fatah Super Store",
            )

        st.markdown("")
        submitted = st.form_submit_button(
            "✅  Complete Registration & Enter Zariya",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            errors = []

            # Validate CNIC
            if not cnic:
                errors.append("CNIC is required.")
            elif not validate_cnic(cnic):
                errors.append("Invalid CNIC format. Use XXXXX-XXXXXXX-X (e.g. 35202-1234567-8).")

            # Validate required fields
            for field_name, value in [
                ("Business Name", business_name),
                ("City", city),
                ("Area Name", area_name),
                ("Landmark", landmark),
            ]:
                if not value or not value.strip():
                    errors.append(f"{field_name} is required.")

            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                profile = {
                    "display_name": display_name,
                    "role": role,
                    "cnic": cnic.strip(),
                    "business_name": business_name.strip(),
                    "business_type": business_type,
                    "province": province,
                    "city": city.strip(),
                    "area_name": area_name.strip(),
                    "landmark": landmark.strip(),
                }
                register_user(email, profile)

                st.session_state["user_profile"] = get_user(email)
                st.session_state["kyc_complete"] = True

                st.success("🎉 Registration complete! Welcome to Zariya.")
                st.balloons()
                st.rerun()
