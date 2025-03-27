import streamlit as st
import pandas as pd
import numpy as np
import streamlit_shadcn_ui as ui
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pydeck as pdk
import random
import time

# MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Housing Loan Advisor", page_icon="house", layout="wide")

# -------------------- GLOBAL VARIABLES --------------------

financial_vars = {
    "monthly_income": 3500,
    "monthly_expenses": 1200,
    "other_loans": 200,
    "existing_student_debt": 7000,
    "monthly_student_payment": 150,
    "other_assets": 25000,
    "loan_amount": 280000,
    "down_payment": 70000,
    "loan_term": 25,
    "interest_rate": 3.5
}

# Real-world Helsinki addresses with coordinates
helsinki_addresses = [
    {"address": "Erottajankatu 15, 00130 Helsinki", "latitude": 60.1665, "longitude": 24.9452},
    {"address": "Bulevardi 12, 00120 Helsinki", "latitude": 60.1648, "longitude": 24.9398},
    {"address": "Kaptensgatan 25, 00140 Helsinki", "latitude": 60.1602, "longitude": 24.9515},
    {"address": "Hämeentie 15, 00530 Helsinki", "latitude": 60.1866, "longitude": 24.9632},
    {"address": "Mannerheimintie 45, 00250 Helsinki", "latitude": 60.1795, "longitude": 24.9251}
]
if 'st.session_state.property_data' not in st.session_state:
    st.session_state.property_data = {
        "price": 350000,
        "size": 65,
        "type": "Apartment",
        "year": 2005,
        "address": helsinki_addresses[0]["address"],
        "latitude": helsinki_addresses[0]["latitude"],
        "longitude": helsinki_addresses[0]["longitude"],
        "maintenance_fee": 245,
        "condition": "Good",
        "upcoming_renovations": [
            {"year": 2027, "type": "Plumbing", "estimated_cost": 12500, "impact": "Major water system overhaul"},
            {"year": 2029, "type": "Facade", "estimated_cost": 8000, "impact": "Exterior aesthetic and insulation upgrade"}
        ],
        "energy_rating": "C",
    }

# -------------------- CUSTOM THEME --------------------
colors = {
    'primary': '#FF9500',
    'secondary': '#FF5A00',
    'success': '#4DAA57',
    'warning': '#FF5A00',
    'light': '#FFF4E6',
    'white': '#FFFFFF',
    'text': '#333333',
    'slate': '#708090',
    'positive': '#4DAA57',
    'negative': '#E63946'
}

# Define CSS styles for the banking application
banking_css = f"""
<style>
/* Base styles */
@import url('https://fonts.googleapis.com/css2?family=Calibri:wght@300;400;700&display=swap');

.stApp {{
    background-color: {colors['white']};
    color: {colors['text']};
    font-family: 'Calibri Light', 'Calibri', sans-serif;
    font-weight: 300;
}}

.block-container {{
    padding-top: 1rem;
}}

h1, h2, h3 {{
    color: {colors['primary']};
    font-family: 'Calibri Light', 'Calibri', sans-serif;
    font-weight: 300;
}}

.stButton button {{
    background-color: {colors['primary']};
    color: {colors['white']};
    font-family: 'Calibri Light', 'Calibri', sans-serif;
    font-weight: 300;
}}

/* Bank-like UI components */
.bank-card {{
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}}

.bank-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}}

.bank-card-title {{
    color: #333333;
    font-size: 18px;
    font-weight: 500;
}}

.bank-card-arrow {{
    color: {colors['primary']};
    font-size: 18px;
}}

.bank-widget {{
    background-color: #f8f9fa;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
}}

.bank-item {{
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
}}

.bank-item-label {{
    flex-grow: 1;
    font-size: 14px;
}}

.bank-item-value {{
    font-weight: 500;
    font-size: 14px;
}}

.bank-item-arrow {{
    width: 15px;
    text-align: right;
    color: {colors['primary']};
}}

.bank-notice {{
    background-color: {colors['light']};
    border-left: 4px solid {colors['primary']};
    border-radius: 4px;
    padding: 10px;
    margin-top: 15px;
    font-size: 13px;
}}

.positive-value {{
    color: {colors['positive']};
}}

.negative-value {{
    color: {colors['negative']};
}}

.bank-progress-bar {{
    background-color: #f0f0f0;
    border-radius: 10px;
    height: 8px;
    position: relative;
    overflow: hidden;
}}

.bank-progress-fill {{
    position: absolute;
    height: 100%;
    border-radius: 10px;
}}

.bank-metric {{
    flex: 1; 
    background-color: white; 
    border-radius: 10px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
    margin: 0 5px; 
    padding: 15px; 
    text-align: center;
}}

.bank-metric-label {{
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
}}

.bank-metric-value {{
    font-size: 22px;
    font-weight: 500;
}}
</style>
"""

# Apply the CSS
st.markdown(banking_css, unsafe_allow_html=True)

# -------------------- APP TITLE --------------------
st.markdown("<h1 class='main-header'>Housing Loan Advisor</h1>", unsafe_allow_html=True)

# -------------------- SIDEBAR: PROPERTY DETAILS & API --------------------
with st.sidebar:
    # Add OP Bank logo at the top of the sidebar
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/OP_Financial_Group.svg/1200px-OP_Financial_Group.svg.png", width=300)
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("### Apartment Search")
    st.markdown("Enter an Oikotie apartment URL to fetch property details:")
    apt_url = st.text_input("Apartment URL", "https://asunnot.oikotie.fi/myytavat-asunnot/helsinki/22930110")
    
    if ui.button("Fetch Property Data", className="bg-orange-500 text-white", key="clicked_button"):
        selected_address = random.choice(helsinki_addresses)
        st.session_state.property_data.update({
            "price": random.randint(300000, 500000),
            "size": random.randint(40, 120),
            "type": random.choice(["Apartment", "House", "Townhouse"]),
            "year": random.randint(1950, datetime.now().year),
            "address": selected_address["address"],
            "latitude": selected_address["latitude"],
            "longitude": selected_address["longitude"],
            "maintenance_fee": random.randint(180, 350),
            "condition": random.choice(["Excellent", "Good", "Satisfactory", "Poor"]),
            "energy_rating": random.choice(["A", "B", "C", "D", "E", "F", "G"])
        })
        
        renovations = []
        renovation_types = [
            {"type": "Plumbing", "impact": "Major water system overhaul"},
            {"type": "Facade", "impact": "Exterior aesthetic and insulation upgrade"},
            {"type": "Roof", "impact": "Structural integrity and leak prevention"},
            {"type": "Windows", "impact": "Energy efficiency improvement"},
            {"type": "Elevator", "impact": "Accessibility and convenience upgrade"}
        ]
        current_year = datetime.now().year
        
        for i in range(random.randint(1, 3)):
            renovation_year = current_year + random.randint(1, 8)
            renovation = random.choice(renovation_types)
            cost_per_sqm = random.randint(150, 550)
            estimated_cost = round(cost_per_sqm * st.session_state.property_data["size"])
            renovations.append({
                "year": renovation_year,
                "type": renovation["type"],
                "estimated_cost": estimated_cost,
                "impact": renovation["impact"]
            })
        
        st.session_state.property_data["upcoming_renovations"] = renovations
        st.success("Property data fetched successfully!")
        st.markdown("### Property Details")
        st.markdown(f"**Price:** €{st.session_state.property_data['price']:,}")
        st.markdown(f"**Size:** {st.session_state.property_data['size']} m²")
        st.markdown(f"**Type:** {st.session_state.property_data['type']}")
        st.markdown(f"**Year:** {st.session_state.property_data['year']}")
        st.markdown(f"**Address:** {st.session_state.property_data['address']}")
        st.markdown(f"**Maintenance Fee:** €{st.session_state.property_data['maintenance_fee']}/month")

# -------------------- LOAN & FINANCIAL PARAMETERS --------------------
mi = financial_vars["monthly_income"]
me = financial_vars["monthly_expenses"]
sd = financial_vars["existing_student_debt"]
ms = financial_vars["monthly_student_payment"]
ol = financial_vars["other_loans"]
oa = financial_vars["other_assets"]
la = financial_vars["loan_amount"]
dp = financial_vars["down_payment"]
lt = financial_vars["loan_term"]
ir = financial_vars["interest_rate"]

# Always calculate core financial metrics regardless of UI state
monthly_payment = (la * (ir/100/12) * (1 + ir/100/12)**(lt*12)) / ((1 + ir/100/12)**(lt*12) - 1)
loan_to_value = (la / (la + dp)) * 100
debt_to_income = ((monthly_payment + ol) / mi) * 100
disposable_income = mi - me - monthly_payment - ol
asset_to_loan_ratio = (oa / la) * 100

monthly_maintenance = st.session_state.property_data["maintenance_fee"]
renovation_cost_monthly = sum([r["estimated_cost"] for r in st.session_state.property_data["upcoming_renovations"]]) / (10 * 12) if st.session_state.property_data["upcoming_renovations"] else 0
total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
total_housing_ratio = (total_monthly_housing_cost / mi) * 100

risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
risk_color = colors['success'] if risk_score < 20 else colors['primary'] if risk_score < 35 else colors['warning']

def render_loan_recommender():
    # Header with clearer explanation
    st.subheader("Personalized Loan Setup Recommendations")
    # Create subtabs within the loan recommender
    with st.container(border=True):
        # First subtab: ALL information and inputs
        info_subtab, recommendation_subtab = st.tabs(["Loan Information", "Loan Recommendation"])
        with info_subtab:
            # Add image placeholder in the left corner
            col_img, col_text = st.columns([0.5, 3])
            
            with col_img:
                st.image("https://github.com/immone/streamlit_demo_small/blob/main/assets/decision.png?raw=true", width=175)
            
            with col_text:
                st.markdown("""
                <div class="bank-widget" style="padding: 20px; margin-bottom: 20px;">
                    <strong>What is this tool?</strong> 
                    <br>
                    <br>
                    Analyzes your financial situation to recommend the optimal loan structure based on your priorities and real-world banking criteria.
                    <br>
                    Our recommendations are based on Finnish banking standards and financial best practices, not just estimates. We factor in your debt-to-income ratio, loan-to-value ratio, and overall financial health.
                </div>
                """, unsafe_allow_html=True)
            
            # Explain the options in more digestible format with concrete examples
            st.markdown("### Common Loan Profiles in Finland")
            
            profile_col1, profile_col2, profile_col3 = st.columns(3)
            
            # Calculate concrete examples based on the user's actual loan amount
            conservative_down = max(dp + 20000, 0.25 * (la + dp))
            conservative_loan = (la + dp) - conservative_down
            conservative_term = max(lt - 5, 15)
            conservative_rate = max(ir - 0.3, 2.8)
            conservative_monthly = (conservative_loan * (conservative_rate/100/12) * (1 + conservative_rate/100/12)**(conservative_term*12)) / ((1 + conservative_rate/100/12)**(conservative_term*12) - 1)
            
            balanced_down = max(dp + 10000, 0.20 * (la + dp))
            balanced_loan = (la + dp) - balanced_down
            balanced_term = lt
            balanced_rate = max(ir - 0.15, 3.0)
            balanced_monthly = (balanced_loan * (balanced_rate/100/12) * (1 + balanced_rate/100/12)**(balanced_term*12)) / ((1 + balanced_rate/100/12)**(balanced_term*12) - 1)
            
            growth_down = max(dp, 0.15 * (la + dp))
            growth_loan = (la + dp) - growth_down
            growth_term = min(lt + 3, 30)
            growth_rate = ir
            growth_monthly = (growth_loan * (growth_rate/100/12) * (1 + growth_rate/100/12)**(growth_term*12)) / ((1 + growth_rate/100/12)**(growth_term*12) - 1)
            
            # Use bank-style cards for each profile
            with profile_col1:
                st.markdown(f"""
                <div class="bank-card">
                    <div class="bank-card-header">
                        <span class="bank-card-title" style="color: #4DAA57;">Conservative Profile</span>
                    </div>
                    <ul style="padding-left: 15px; margin-bottom: 10px;">
                        <li><strong>Down payment:</strong> €{conservative_down:,.0f} (25%+)</li>
                        <li><strong>Loan amount:</strong> €{conservative_loan:,.0f}</li>
                        <li><strong>Term:</strong> {conservative_term} years</li>
                        <li><strong>Monthly payment:</strong> €{conservative_monthly:.0f}</li>
                        <li><strong>Interest rate:</strong> Typically {conservative_rate}%</li>
                    </ul>
                    <p style="font-size: 0.9rem; color: #666; font-style: italic; margin-bottom: 0;">Example: A family with €80,000 in savings choosing a 15-year loan with lower total interest costs.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with profile_col2:
                st.markdown(f"""
                <div class="bank-card">
                    <div class="bank-card-header">
                        <span class="bank-card-title" style="color: #FF9500;">Balanced Profile</span>
                    </div>
                    <ul style="padding-left: 15px; margin-bottom: 10px;">
                        <li><strong>Down payment:</strong> €{balanced_down:,.0f} (20%)</li>
                        <li><strong>Loan amount:</strong> €{balanced_loan:,.0f}</li>
                        <li><strong>Term:</strong> {balanced_term} years</li>
                        <li><strong>Monthly payment:</strong> €{balanced_monthly:.0f}</li>
                        <li><strong>Interest rate:</strong> Typically {balanced_rate}%</li>
                    </ul>
                    <p style="font-size: 0.9rem; color: #666; font-style: italic; margin-bottom: 0;">Example: A couple with €70,000 savings choosing a 25-year loan with balanced payments vs. interest.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with profile_col3:
                st.markdown(f"""
                <div class="bank-card">
                    <div class="bank-card-header">
                        <span class="bank-card-title" style="color: #FF5A00;">Growth-Focused Profile</span>
                    </div>
                    <ul style="padding-left: 15px; margin-bottom: 10px;">
                        <li><strong>Down payment:</strong> €{growth_down:,.0f} (15%)</li>
                        <li><strong>Loan amount:</strong> €{growth_loan:,.0f}</li>
                        <li><strong>Term:</strong> {growth_term} years</li>
                        <li><strong>Monthly payment:</strong> €{growth_monthly:.0f}</li>
                        <li><strong>Interest rate:</strong> Typically {growth_rate}%</li>
                    </ul>
                    <p style="font-size: 0.9rem; color: #666; font-style: italic; margin-bottom: 0;">Example: A young professional with €50,000 savings choosing a 30-year loan to minimize monthly payments.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Simplify the inputs - more guided approach with real examples
            st.markdown("### What's Your Financial Priority?")
            
            priority_option = st.radio(
                "Choose what matters most to you:",
                ["Lower Monthly Payments", "Balanced Approach", "Lower Total Interest Costs"],
                index=1,
                key="recommender_priority_option"
            )
            
            # Map the selection to the slider value
            if priority_option == "Lower Monthly Payments":
                payment_priority = 1
                st.markdown(f"""
                <div class="bank-notice">
                    <strong>What this means:</strong> You'll get a longer loan term (25-30 years) with 
                    lower monthly payments (around €{growth_monthly:.0f}/month in your case), but will pay more in total interest over time.
                </div>
                """, unsafe_allow_html=True)
            elif priority_option == "Balanced Approach":
                payment_priority = 3
                st.markdown(f"""
                <div class="bank-notice">
                    <strong>What this means:</strong> You'll get a moderate loan term (around 25 years) 
                    with reasonable monthly payments (around €{balanced_monthly:.0f}/month in your case) and moderate total interest costs.
                </div>
                """, unsafe_allow_html=True)
            else:  # Lower Total Interest
                payment_priority = 5
                st.markdown(f"""
                <div class="bank-notice">
                    <strong>What this means:</strong> You'll get a shorter loan term (15-20 years) with 
                    higher monthly payments (around €{conservative_monthly:.0f}/month in your case), but will save significantly on total interest.
                </div>
                """, unsafe_allow_html=True)
            
            # Risk tolerance selection
            st.markdown("### How comfortable are you with financial risk?")
            
            risk_option = st.radio(
                "Choose your comfort level with financial stretching:",
                ["Very Conservative", "Moderately Conservative", "Balanced", "Moderately Aggressive", "Aggressive"],
                index=2,
                key="recommender_risk_option"
            )
            
            # Map the selection to risk tolerance value
            risk_mapping = {
                "Very Conservative": 1,
                "Moderately Conservative": 2,
                "Balanced": 3,
                "Moderately Aggressive": 4,
                "Aggressive": 5
            }
            
            risk_tolerance = risk_mapping[risk_option]
            
            # Show risk implications with concrete numbers
            if risk_option == "Very Conservative" or risk_option == "Moderately Conservative":
                st.markdown(f"""
                <div class="bank-notice" style="border-left: 4px solid #4DAA57;">
                    <strong>What this means:</strong> You prefer financial security with higher down 
                    payments (€{conservative_down:,.0f}+) and lower loan-to-value ratios (under 75%). This gives you better interest 
                    rates and less risk if property values decline.
                </div>
                """, unsafe_allow_html=True)
            elif risk_option == "Balanced":
                st.markdown(f"""
                <div class="bank-notice" style="border-left: 4px solid #FF9500;">
                    <strong>What this means:</strong> You prefer a moderate approach with standard down 
                    payments (around €{balanced_down:,.0f} or 20%) and conventional loan terms. This balances financial security with 
                    keeping cash available for other needs.
                </div>
                """, unsafe_allow_html=True)
            else:  # Aggressive options
                st.markdown(f"""
                <div class="bank-notice" style="border-left: 4px solid #FF5A00;">
                    <strong>What this means:</strong> You're comfortable with higher financial leverage, 
                    using lower down payments (around €{growth_down:,.0f} or 15%) and longer terms to maximize cash flow and investment 
                    potential elsewhere.
                </div>
                """, unsafe_allow_html=True)
            
            # Constraints section with better guidance
            st.markdown("### Financial Constraints")
            
            # Show the current calculated monthly payment
            current_monthly = (la * (ir/100/12) * (1 + ir/100/12)**(lt*12)) / ((1 + ir/100/12)**(lt*12) - 1)
            
            # Calculate percentages of income for different payment levels
            low_payment = current_monthly * 0.8
            low_payment_pct = (low_payment / mi) * 100
            
            high_payment = current_monthly * 1.2
            high_payment_pct = (high_payment / mi) * 100
            
            current_payment_pct = (current_monthly / mi) * 100
            
            st.markdown(f"""
            <div class="bank-widget" style="margin-bottom: 15px;">
                <strong>Current Calculated Monthly Payment:</strong> €{current_monthly:.0f} ({current_payment_pct:.1f}% of your income)
            </div>
            """, unsafe_allow_html=True)
            
            max_monthly = st.slider(
                "Maximum Comfortable Monthly Payment (€)", 
                min_value=int(current_monthly * 0.7),
                max_value=int(current_monthly * 1.5),
                value=int(current_monthly * 1.1),
                step=50,
                key="recommender_max_payment"
            )
            
            # Show what percentage of income the selected payment is
            selected_payment_pct = (max_monthly / mi) * 100
            payment_assessment = "good" if selected_payment_pct < 30 else "moderate" if selected_payment_pct < 40 else "high"
            payment_color = "#4DAA57" if payment_assessment == "good" else "#FF9500" if payment_assessment == "moderate" else "#E63946"
            
            st.markdown(f"""
            <div style="font-size: 0.9rem; margin: 10px 0;">
                Your selected payment (€{max_monthly:.0f}) is <span style="color:{payment_color}; font-weight:600;">{selected_payment_pct:.1f}%</span> of your monthly income.
                This is considered <span style="color:{payment_color}; font-weight:600;">{payment_assessment}</span> by most lenders.
            </div>
            """, unsafe_allow_html=True)
            
            # Bank approval odds with explanation and concrete examples
            st.markdown("""
            <div style="margin: 20px 0 15px 0;">
                <strong>Bank Approval Standards:</strong> Different banks have different risk tolerance levels.
            </div>
            """, unsafe_allow_html=True)
            
            target_approval = st.selectbox(
                "Target Approval Likelihood", 
                ["Very High (95%+)", "High (80-95%)", "Moderate (65-80%)", "Flexible"],
                index=1,
                key="recommender_approval"
            )
            
            # Add concrete examples for each approval tier - modified to only reference OP Bank
            if target_approval == "Very High (95%+)":
                st.markdown("""
                <div class="bank-notice" style="border-left: 4px solid #4DAA57;">
                    <strong>Bank Examples:</strong> OP Bank and other major banks with stricter criteria. 
                    They typically require debt-to-income ratios under 35%, loan-to-value ratios under 80%, 
                    and excellent credit history.
                </div>
                """, unsafe_allow_html=True)
            elif target_approval == "High (80-95%)":
                st.markdown("""
                <div class="bank-notice" style="border-left: 4px solid #FF9500;">
                    <strong>Bank Examples:</strong> Most Finnish banks including OP Bank. 
                    They typically accept debt-to-income ratios up to 40%, loan-to-value ratios up to 85%, 
                    and good credit history.
                </div>
                """, unsafe_allow_html=True)
            elif target_approval == "Moderate (65-80%)":
                st.markdown("""
                <div class="bank-notice" style="border-left: 4px solid #FF5A00;">
                    <strong>Bank Examples:</strong> Some online lenders and smaller banks. 
                    They may accept debt-to-income ratios up to 45%, loan-to-value ratios up to 90%, 
                    and average credit history.
                </div>
                """, unsafe_allow_html=True)
            else:  # Flexible
                st.markdown("""
                <div class="bank-notice" style="border-left: 4px solid #6c757d;">
                    <strong>What this means:</strong> You'll see all options regardless of approval likelihood. 
                    Some may require special considerations or programs that OP Bank might offer based on your unique situation.
                </div>
                """, unsafe_allow_html=True)
            
            # Generate button - in the info tab but affects the recommendation tab
            if st.button("Generate My Personalized Recommendation", use_container_width=True, key="recommender_button"):
                with st.spinner("Analyzing financial profiles and bank approval criteria..."):
                    time.sleep(2)
                    
                    # Generate options based on real mortgage lending standards
                    # Calculate realistic options based on the user's financial profile
                    options = [
                        {
                            "name": "Conservative",
                            "down_payment": max(dp + 20000, 0.25 * (la + dp)),  # At least 25% down payment
                            "loan_amount": min(la - 20000, 0.75 * (la + dp)),
                            "term": max(lt - 5, 15),
                            "rate": max(ir - 0.3, 2.8),  # Better rates for conservative profiles
                            "monthly": 0,
                            "total_interest": 0,
                            "approval_odds": "Very High (95%+)",
                            "risk_score": "Low Risk",
                            "key_benefits": [
                                "Lower total interest costs",
                                "Faster equity building",
                                "Better interest rates",
                                "Higher approval likelihood"
                            ],
                            "considerations": [
                                "Higher monthly payments",
                                "More cash needed upfront",
                                "Less funds for other investments"
                            ]
                        },
                        {
                            "name": "Balanced",
                            "down_payment": max(dp + 10000, 0.20 * (la + dp)),  # 20% down payment (standard)
                            "loan_amount": min(la - 10000, 0.80 * (la + dp)),
                            "term": lt,
                            "rate": max(ir - 0.15, 3.0),
                            "monthly": 0,
                            "total_interest": 0,
                            "approval_odds": "High (80-95%)",
                            "risk_score": "Moderate Risk",
                            "key_benefits": [
                                "Good balance of payment vs. interest",
                                "Meets standard bank requirements",
                                "Moderate cash needs upfront",
                                "Leaves room for other investments"
                            ],
                            "considerations": [
                                "Moderate total interest costs",
                                "Average equity building pace",
                                "Standard interest rates"
                            ]
                        },
                        {
                            "name": "Growth-Focused",
                            "down_payment": max(dp, 0.15 * (la + dp)),  # 15% minimum down payment
                            "loan_amount": min(la, 0.85 * (la + dp)),
                            "term": min(lt + 3, 30),
                            "rate": ir,  # Standard rate for higher LTV
                            "monthly": 0,
                            "total_interest": 0,
                            "approval_odds": "Moderate (65-80%)",
                            "risk_score": "Moderate Risk",
                            "key_benefits": [
                                "Lower monthly payment burden",
                                "Minimum cash needed upfront",
                                "More cash available for other investments",
                                "Flexibility for career growth"
                            ],
                            "considerations": [
                                "Higher total interest costs",
                                "Slower equity building",
                                "May require mortgage insurance",
                                "Higher interest rates"
                            ]
                        }
                    ]
                    
                    # Calculate monthly payments and total interest using actual formulas
                    for opt in options:
                        opt["monthly"] = (opt["loan_amount"] * (opt["rate"]/100/12) * 
                                        (1 + opt["rate"]/100/12)**(opt["term"]*12)) / \
                                        ((1 + opt["rate"]/100/12)**(opt["term"]*12) - 1)
                        opt["total_interest"] = opt["monthly"] * opt["term"] * 12 - opt["loan_amount"]
                        # Calculate real-world metrics
                        opt["ltv_ratio"] = (opt["loan_amount"] / (opt["loan_amount"] + opt["down_payment"])) * 100
                        opt["dti_ratio"] = (opt["monthly"] / mi) * 100
                    
                    # Filter options based on constraints and real approval criteria
                    filtered_options = [
                        opt for opt in options 
                        if opt["monthly"] <= max_monthly and
                        (target_approval == "Flexible" or opt["approval_odds"] == target_approval) and
                        opt["ltv_ratio"] <= 95  # Real-world maximum LTV
                    ]
                    
                    if not filtered_options:
                        st.warning("""
                        No options match your constraints. This happens when your maximum payment is too low 
                        or your approval requirements are too strict for your financial situation. Try adjusting your parameters.
                        """)
                    else:
                        # Map risk tolerance to profile index, with more nuanced selection
                        if risk_tolerance == 1:  # Very Conservative
                            best_idx = 0  # Conservative profile
                        elif risk_tolerance == 2:  # Moderately Conservative
                            # Lean conservative but consider balanced
                            best_idx = min(1, len(filtered_options) - 1)
                        elif risk_tolerance == 3:  # Balanced
                            # Pick middle option when possible
                            best_idx = min(1, len(filtered_options) - 1)
                        elif risk_tolerance == 4:  # Moderately Aggressive
                            # Lean growth-focused but consider balanced
                            best_idx = min(len(filtered_options) - 1, 1)
                        else:  # Aggressive
                            best_idx = min(2, len(filtered_options) - 1)  # Growth-Focused profile
                        
                        # Adjust based on payment priority preference
                        if payment_priority == 1 and len(filtered_options) > 1:  # Lower Monthly Payment
                            # Sort by monthly payment, lowest first
                            filtered_options.sort(key=lambda x: x["monthly"])
                            best_idx = 0
                        elif payment_priority == 5 and len(filtered_options) > 1:  # Lower Total Interest
                            # Sort by total interest, lowest first
                            filtered_options.sort(key=lambda x: x["total_interest"])
                            best_idx = 0
                        
                        recommended = filtered_options[best_idx]
                        st.session_state.loan_options = filtered_options
                        st.session_state.recommended = recommended
                        st.session_state.all_options = options

                        # After calculation, automatically switch to the recommendation tab
                        st.success("Recommendation generated! Check the 'Loan Recommendation' tab for your personalized recommendation.")
    
    # Second subtab: Recommendation display only
    with recommendation_subtab:
        if 'loan_options' not in st.session_state:
            st.markdown("""
            <div class="bank-widget" style="text-align: center; padding: 30px;">
                <div style="font-size: 18px; margin-bottom: 10px;">No Recommendation Yet</div>
                <p>Please go to the 'Loan Information' tab and fill out your preferences, 
                then click 'Generate My Personalized Recommendation' to see your personalized loan setup.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display detailed recommendation with fixed formatting
            rec = st.session_state.recommended
            
            # Determine actual bank approval status based on real criteria
            ltv_status = "Excellent" if rec["ltv_ratio"] < 80 else "Good" if rec["ltv_ratio"] < 90 else "Acceptable"
            dti_status = "Excellent" if rec["dti_ratio"] < 30 else "Good" if rec["dti_ratio"] < 40 else "Acceptable"
            
            # Calculate the full financial impact
            total_cost = rec["monthly"] * rec["term"] * 12
            interest_percentage = (rec["total_interest"] / rec["loan_amount"]) * 100
            
            # Calculate real-world comparisons
            interest_savings = 0
            if 'all_options' in st.session_state:
                interest_savings = st.session_state.all_options[0]["total_interest"] - rec["total_interest"]

            # And similarly for monthly_difference:
            monthly_difference = 0
            if 'all_options' in st.session_state:
                monthly_difference = st.session_state.all_options[0]["monthly"] - rec["monthly"]
            
            # Use bank-style card for the recommendation display
            st.html(f"""
            <div class="bank-card">
                <div class="bank-card-header">
                    <span class="bank-card-title">Recommended: {rec['name']} Profile</span>
                    <span class="bank-card-arrow">›</span>
                </div>
                
                <div style="display: flex; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h5 style="margin-bottom: 10px;">Loan Structure</h5>
                        <p><strong>Down Payment:</strong> €{rec['down_payment']:,} ({rec['ltv_ratio']:.1f}% LTV)</p>
                        <p><strong>Loan Amount:</strong> €{rec['loan_amount']:,}</p>
                        <p><strong>Term:</strong> {rec['term']} years</p>
                        <p><strong>Interest Rate:</strong> {rec['rate']:.2f}%</p>
                    </div>
                    <div style="flex: 1;">
                        <h5 style="margin-bottom: 10px;">Financial Impact</h5>
                        <p><strong>Monthly Payment:</strong> €{rec['monthly']:.0f}</p>
                        <p><strong>Total Cost:</strong> €{total_cost:,.0f}</p>
                        <p><strong>Total Interest:</strong> €{rec['total_interest']:,.0f} ({interest_percentage:.1f}%)</p>
                        <p><strong>Payment-to-Income:</strong> {rec['dti_ratio']:.1f}%</p>
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <h5 style="margin-bottom: 10px;">Bank Approval Factors</h5>
                    <p><strong>Loan-to-Value Ratio:</strong> <span style="color: {'green' if ltv_status == 'Excellent' else 'orange' if ltv_status == 'Good' else '#FF5A00'};">{ltv_status}</span> ({rec['ltv_ratio']:.1f}%)</p>
                    <p><strong>Debt-to-Income Ratio:</strong> <span style="color: {'green' if dti_status == 'Excellent' else 'orange' if dti_status == 'Good' else '#FF5A00'};">{dti_status}</span> ({rec['dti_ratio']:.1f}%)</p>
                    <p><strong>Overall Approval Likelihood:</strong> {rec['approval_odds']}</p>
                </div>
                
                <div class="bank-notice" style="margin-top: 15px;">
                    <h5 style="margin: 0 0 10px 0;">What This Means For You</h5>
                    <p>
                        With this option, you'll pay <strong>€{rec['monthly']:.0f} per month</strong> for <strong>{rec['term']} years</strong>. 
                        {
                            f"This is <strong style='color:green'>€{abs(monthly_difference):.0f} less per month</strong> than the most conservative option, " if monthly_difference > 0 else 
                            f"This is <strong style='color:#E63946'>€{abs(monthly_difference):.0f} more per month</strong> than the most aggressive option, " if monthly_difference < 0 else ""
                        }
                        {
                            f" you'll pay <strong style='color:#E63946'>€{abs(interest_savings):.0f} more in total interest</strong> over the life of the loan." if interest_savings < 0 else
                            f" you'll save <strong style='color:green'>€{abs(interest_savings):.0f} in total interest</strong> over the life of the loan." if interest_savings > 0 else ""
                        }
                    </p>
                </div>
            </div>
            """)
            
            
            st.markdown("<h5>Key Benefits</h5>", unsafe_allow_html=True)
            benefits_list = "\n".join([f"* {benefit}" for benefit in rec["key_benefits"]])
            st.markdown(benefits_list)
            
            st.markdown("<h5>Key Considerations</h5>", unsafe_allow_html=True)
            considerations_list = "\n".join([f"* {consideration}" for consideration in rec["considerations"]])
            st.markdown(considerations_list)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Compare all options in a bank-style card
            st.markdown("""
            <div class="bank-card">
                <div class="bank-card-header">
                    <span class="bank-card-title">Compare All Options</span>
                    <span class="bank-card-arrow">›</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Create a comparison table with the most relevant metrics
            comparison_df = pd.DataFrame([
                {
                    "Profile": opt["name"],
                    "Down Payment": f"€{opt['down_payment']:,}",
                    "Loan Amount": f"€{opt['loan_amount']:,}",
                    "Term (years)": opt["term"],
                    "Interest Rate": f"{opt['rate']}%",
                    "Monthly Payment": f"€{opt['monthly']:.0f}",
                    "Total Interest": f"€{opt['total_interest']:,.0f}",
                    "LTV Ratio": f"{opt['ltv_ratio']:.1f}%",
                    "Approval": opt["approval_odds"]
                } for opt in st.session_state.loan_options
            ])
            
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)
            
            # Add real-world recommendation specific to OP Bank - with proper formatting
            st.markdown(f"""
            <div class="bank-notice">
                <strong>OP Bank Recommendation:</strong> With your financial profile and this loan structure, you're an ideal candidate for OP Bank's mortgage services.
                <br><br>
                Finnish lenders typically prefer loan-to-value ratios below 85% and debt-to-income 
                ratios below 40%. Your recommended option has {rec['ltv_ratio']:.1f}% LTV and {rec['dti_ratio']:.1f}% DTI, 
                making it a {ltv_status.lower()}/{dti_status.lower()} candidate for OP Bank's approval criteria.
                <br><br>
                <strong>Next steps:</strong> Schedule a meeting with an OP Bank advisor to get your pre-approval. 
                Ask about both fixed and variable rate options, and any available first-time homebuyer benefits that OP Bank offers.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            

# -------------------- FUNCTIONS FOR TABS --------------------
def render_financial_summary():
    # Pre-loan wealth (status quo)
    debt_amount_pre = sd  # Student debt only
    assets_amount_pre = oa  # Savings only
    total_amount_pre = debt_amount_pre + assets_amount_pre
    debt_percentage_pre = (debt_amount_pre / total_amount_pre) * 100 if total_amount_pre > 0 else 0
    assets_percentage_pre = 100 - debt_percentage_pre

    # Post-loan wealth
    property_value = la + dp  # 350000 €
    debt_amount_post = sd + la  # Student debt + housing loan
    assets_amount_post = oa - dp + property_value  # Remaining savings + property
    total_amount_post = debt_amount_post + assets_amount_post
    debt_percentage_post = (debt_amount_post / total_amount_post) * 100 if total_amount_post > 0 else 0
    assets_percentage_post = 100 - debt_percentage_post

    monthly_income = mi
    monthly_expenses = me  # Pre-loan includes rent
    student_payment = ms
    loan_payment = monthly_payment
    
    # Post-loan expenses (rent replaced by housing costs)
    total_expenses = monthly_expenses - 900 + loan_payment + student_payment + monthly_maintenance + renovation_cost_monthly  # Subtract rent, add housing costs
    monthly_balance = monthly_income - total_expenses
    
    # Payment ratios
    payment_to_income_ratio = (loan_payment / monthly_income) * 100
    
    # Key financial indicators
    st.markdown("### Key Financial Indicators")
    
    col1, col2 = st.columns([1.5,1])
    with col1:
        with st.container(border=True):
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                ui.metric_card(title="Loan-to-Value", content=f"{loan_to_value:.1f}%", description=f"{'Good' if loan_to_value < 80 else 'Moderate' if loan_to_value < 90 else 'High'}")
            with kpi_col2:
                ui.metric_card(title="Debt-to-Income", content=f"{debt_to_income:.1f}%", description=f"{'Good' if debt_to_income < 35 else 'Moderate' if debt_to_income < 45 else 'High'}")
            with kpi_col3:
                ui.metric_card(title="Housing Costs to Income", content=f"{total_housing_ratio:.1f}%", description=f"{'Good' if total_housing_ratio < 35 else 'Moderate' if total_housing_ratio < 45 else 'High'}")
            with kpi_col4:
                ui.metric_card(title="Overall Risk Score", content=f"{risk_score:.1f}", description=risk_category)

            # Wealth section (show pre- and post-loan)
            wealth_html = f"""
            <div class="bank-card">
                <div class="bank-card-header">
                    <span class="bank-card-title">Wealth</span>
                    <span class="bank-card-arrow">›</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div style="flex: 1; padding-right: 10px;">
                        <h4>Before Loan</h4>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="color: #555; font-size: 14px;">Debt</div>
                            <div style="color: #555; font-size: 14px;">Assets</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div style="font-weight: 500; font-size: 14px;">-{debt_amount_pre:,.2f} €</div>
                            <div style="font-weight: 500; font-size: 14px;">{assets_amount_pre:,.2f} €</div>
                        </div>
                        <div style="height: 10px; background-color: #e0e0e0; border-radius: 5px; margin: 15px 0; position: relative;">
                            <div style="position: absolute; width: 1px; height: 16px; background-color: #333; top: -3px; left: {assets_percentage_pre}%;"></div>
                            <div style="position: absolute; height: 100%; left: 0; width: {debt_percentage_pre}%; background-color: #555; border-radius: 5px 0 0 5px;"></div>
                            <div style="position: absolute; height: 100%; right: 0; width: {assets_percentage_pre}%; background-color: #FF9500; border-radius: 0 5px 5px 0;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <div style="font-size: 13px; color: #555;">Existing student debt</div>
                            <div style="font-size: 13px; font-weight: 500;">{sd:,.2f} €</div>
                        </div>
                    </div>
                    <div style="flex: 1; padding-left: 10px;">
                        <h4>After Loan</h4>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="color: #555; font-size: 14px;">Debt</div>
                            <div style="color: #555; font-size: 14px;">Assets</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div style="font-weight: 500; font-size: 14px;">-{debt_amount_post:,.2f} €</div>
                            <div style="font-weight: 500; font-size: 14px;">{assets_amount_post:,.2f} €</div>
                        </div>
                        <div style="height: 10px; background-color: #e0e0e0; border-radius: 5px; margin: 15px 0; position: relative;">
                            <div style="position: absolute; width: 1px; height: 16px; background-color: #333; top: -3px; left: {assets_percentage_post}%;"></div>
                            <div style="position: absolute; height: 100%; left: 0; width: {debt_percentage_post}%; background-color: #555; border-radius: 5px 0 0 5px;"></div>
                            <div style="position: absolute; height: 100%; right: 0; width: {assets_percentage_post}%; background-color: #FF9500; border-radius: 0 5px 5px 0;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <div style="font-size: 13px; color: #555;">Loan {lt}-year fixed</div>
                            <div style="font-size: 13px; font-weight: 500;">{la:,.2f} €</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <div style="font-size: 13px; color: #555;">Existing student debt</div>
                            <div style="font-size: 13px; font-weight: 500;">{sd:,.2f} €</div>
                        </div>
                    </div>
                </div>
            </div>
            """

            # Everyday finance section
            necessaries = (me - 900) * 0.6  # Adjust for rent removal
            loan_repayment = monthly_payment + ms
            fun_benefits = (me - 900) * 0.4
            
            finance_html = f"""
            <div class="bank-card">
                <div class="bank-card-header">
                    <span class="bank-card-title">Everyday Finance</span>
                    <span class="bank-card-arrow">›</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 14px; color: #555; margin-bottom: 8px;">Income</div>
                        <div style="font-size: 22px; font-weight: 500; color: #4DAA57;">{monthly_income:,.2f} €</div>
                    </div>
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 14px; color: #555; margin-bottom: 8px;">Expenditure</div>
                        <div style="font-size: 22px; font-weight: 500; color: #E63946;">-{total_expenses:,.2f} €</div>
                    </div>
                </div>
                <div style="height: 1px; background-color: #f0f0f0; margin: 15px 0;"></div>
                <div class="bank-item">
                    <div class="bank-item-label">Necessaries</div>
                    <div class="bank-item-value negative-value">-{necessaries:,.2f} €</div>
                    <div class="bank-item-arrow">›</div>
                </div>
                <div class="bank-item">
                    <div class="bank-item-label">Loan repayment</div>
                    <div class="bank-item-value negative-value">-{loan_repayment:,.2f} €</div>
                    <div class="bank-item-arrow">›</div>
                </div>
                <div class="bank-item" style="border-bottom: none;">
                    <div class="bank-item-label">Fun and benefits</div>
                    <div class="bank-item-value negative-value">-{fun_benefits:,.2f} €</div>
                    <div class="bank-item-arrow">›</div>
                </div>
            </div>
            """

            # Loan impact section
            loan_html = f"""
            <div class="bank-card">
                <div class="bank-card-header">
                    <span class="bank-card-title">Loan Impact</span>
                    <span class="bank-card-arrow">›</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div style="color: #555; font-size: 14px;">Monthly Payment</div>
                    <div style="font-weight: 500; font-size: 14px;">{monthly_payment:,.2f} €</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div style="color: #555; font-size: 14px;">Payment-to-Income Ratio</div>
                    <div style="font-weight: 500; font-size: 14px;">{payment_to_income_ratio:.1f}%</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div style="color: #555; font-size: 14px;">Loan-to-Value Ratio</div>
                    <div style="font-weight: 500; font-size: 14px;">{loan_to_value:.1f}%</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <div style="color: #555; font-size: 14px;">Monthly Balance After Expenses</div>
                    <div style="font-weight: 500; font-size: 14px; color: {'#4DAA57' if monthly_balance > 0 else '#E63946'};">{monthly_balance:,.2f} €</div>
                </div>
                <div class="bank-notice">
                    <strong>Note:</strong> Loan service costs in relation to net income must not exceed 60%. 
                    Current ratio: <span style="color: {'#4DAA57' if payment_to_income_ratio < 40 else '#FF9500' if payment_to_income_ratio < 60 else '#E63946'};">{payment_to_income_ratio:.1f}%</span>
                </div>
            </div>
            """
            st.html(finance_html)
            st.html(wealth_html)
            st.html(loan_html)

    with col2:
        with st.container(border=True):
            # User avatar and profile data
            st.markdown("""
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="https://api.dicebear.com/6.x/avataaars/svg?seed=Felix" 
                     style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #FF9500;" 
                     alt="Profile Avatar">
                <h4 style="margin: 10px 0 5px 0; font-family: 'Calibri Light', sans-serif; font-weight: 400;">Marty McFly</h4>
                <div style="font-size: 13px; color: #708090;">OP Premium Customer</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Financial health progress bars
            st.html(f"""
            <div style="margin-bottom: 15px;">
                <div style="font-size: 14px; color: #555; margin-bottom: 10px;">Financial Health Metrics</div>
                
                <!-- Savings Goal Progress -->
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <div style="font-size: 12px; color: #555;">Savings Goal</div>
                        <div style="font-size: 12px; font-weight: 500;">75%</div>
                    </div>
                    <div class="bank-progress-bar" style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                        <div class="bank-progress-fill" style="width: 75%; background-color: #4DAA57; height: 100%; border-radius: 3px;"></div>
                    </div>
                </div>
                
                <!-- Budget Adherence -->
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <div style="font-size: 12px; color: #555;">Budget Adherence</div>
                        <div style="font-size: 12px; font-weight: 500;">92%</div>
                    </div>
                    <div class="bank-progress-bar" style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                        <div class="bank-progress-fill" style="width: 92%; background-color: #4DAA57; height: 100%; border-radius: 3px;"></div>
                    </div>
                </div>
                
                <!-- Debt-to-Income -->
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <div style="font-size: 12px; color: #555;">Debt-to-Income</div>
                        <div style="font-size: 12px; font-weight: 500;">{debt_to_income:.1f}%</div>
                    </div>
                    <div class="bank-progress-bar" style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                        <div class="bank-progress-fill" style="width: {min(debt_to_income * 2, 100)}%; 
                            background-color: {'#4DAA57' if debt_to_income < 35 else '#FF9500' if debt_to_income < 45 else '#E63946'}; 
                            height: 100%; border-radius: 3px;"></div>
                    </div>
                </div>
                
                <!-- Emergency Fund -->
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <div style="font-size: 12px; color: #555;">Emergency Fund</div>
                        <div style="font-size: 12px; font-weight: 500;">4.2 months</div>
                    </div>
                    <div class="bank-progress-bar" style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                        <div class="bank-progress-fill" style="width: 84%; background-color: #FF9500; height: 100%; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            """)
            
            # Customer details
            st.markdown("""
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 13px; color: #555;">Customer Since</div>
                    <div style="font-size: 13px; font-weight: 500;">March 2018</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 13px; color: #555;">Savings Accounts</div>
                    <div style="font-size: 13px; font-weight: 500;">2</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 13px; color: #555;">Credit Score</div>
                    <div style="font-size: 13px; font-weight: 500;">Excellent</div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-size: 13px; color: #555;">Advisor</div>
                    <div style="font-size: 13px; font-weight: 500;">Liisa Korhonen</div>
                </div>
               <br>
            </div>
            
            """, unsafe_allow_html=True)

def render_payment_analysis():
    st.subheader("Payment Analysis")
    
    # Create the loan amortization schedule
    loan_amount = financial_vars["loan_amount"]
    interest_rate = financial_vars["interest_rate"]
    loan_term_years = financial_vars["loan_term"]
    
    # Calculate monthly payment
    monthly_interest_rate = interest_rate / 100 / 12
    loan_term_months = loan_term_years * 12
    monthly_payment = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / \
                     ((1 + monthly_interest_rate) ** loan_term_months - 1)
    
    # Generate amortization data
    amortization_data = []
    remaining_balance = loan_amount
    
    for month in range(1, loan_term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        # Only store data for each year (to reduce data points)
        if month % 12 == 0 or month == 1:
            year = (month - 1) // 12 + 1
            amortization_data.append({
                "Year": year,
                "Month": month,
                "Payment": monthly_payment,
                "Principal": principal_payment,
                "Interest": interest_payment,
                "Remaining Balance": remaining_balance
            })
    
    amortization_df = pd.DataFrame(amortization_data)
    
    # Calculate total interest
    total_interest = monthly_payment * loan_term_months - loan_amount
    interest_to_principal_ratio = total_interest / loan_amount * 100
    
    # Payment distribution metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ui.metric_card(
            title="Monthly Payment",
            content=f"€{monthly_payment:.0f}",
            description="Fixed Monthly Payment"
        )
    
    with col2:
        ui.metric_card(
            title="Total Interest",
            content=f"€{total_interest:,.0f}",
            description=f"{interest_to_principal_ratio:.1f}% of Principal"
        )
    
    with col3:
        ui.metric_card(
            title="Total Amount Paid",
            content=f"€{(monthly_payment * loan_term_months):,.0f}",
            description=f"Over {loan_term_years} Years"
        )
    
    # Create visualization tabs
    viz_tab1, viz_tab2 = st.tabs(["Payment Distribution", "Amortization Schedule"])
    
    with viz_tab1:
        # Payment Distribution - Principal vs Interest
        
        # Create a pie chart with Plotly using go.Pie directly for better color control
        principal_interest_data = [
            {"Category": "Principal", "Amount": loan_amount},
            {"Category": "Interest", "Amount": total_interest}
        ]
        
        principal_interest_df = pd.DataFrame(principal_interest_data)
        
        # Use go.Pie instead of px.pie for more direct control of colors
        fig_pie = go.Figure(data=[go.Pie(
            labels=principal_interest_df["Category"],
            values=principal_interest_df["Amount"],
            hole=0.4,
            marker=dict(colors=[colors['primary'], colors['secondary']]),
            textinfo='percent+label'
        )])
        
        fig_pie.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        fig_pie.update_traces(
            textinfo='percent+label',
            textfont_size=14
        )
        
        # First year payment breakdown
        first_year_interest = sum(amortization_df[amortization_df["Year"] == 1]["Interest"])
        first_year_principal = sum(amortization_df[amortization_df["Year"] == 1]["Principal"])
        first_year_total = first_year_interest + first_year_principal
        
        col_pie, col_first_year = st.columns([3, 2])
        
        with col_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_first_year:
            
            st.html(f"""
            <div class="bank-widget">
                <div style="font-size: 14px; color: #555; margin-bottom: 8px;">Total First Year Payments</div>
                <div style="font-size: 24px; font-weight: 500;">€{first_year_total:.0f}</div>
                
                <div style="height: 1px; background-color: #f0f0f0; margin: 15px 0;"></div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div style="color: #555; font-size: 14px;">Applied to Principal:</div>
                    <div style="font-weight: 500; font-size: 14px;">€{first_year_principal:.0f} ({first_year_principal/first_year_total*100:.1f}%)</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <div style="color: #555; font-size: 14px;">Paid in Interest:</div>
                    <div style="font-weight: 500; font-size: 14px;">€{first_year_interest:.0f} ({first_year_interest/first_year_total*100:.1f}%)</div>
                </div>
            </div>
            """)
    
    with viz_tab2:
        # Amortization Schedule
        
        # Create yearly payment breakdown data
        yearly_data = []
        current_principal = loan_amount
        
        for year in range(1, loan_term_years + 1):
            # Calculate payments for this year
            yearly_interest = 0
            yearly_principal = 0
            
            for _ in range(12):
                interest_payment = current_principal * monthly_interest_rate
                principal_payment = monthly_payment - interest_payment
                
                yearly_interest += interest_payment
                yearly_principal += principal_payment
                current_principal -= principal_payment
            
            yearly_data.append({
                "Year": year,
                "Interest": yearly_interest,
                "Principal": yearly_principal,
                "Remaining Balance": current_principal
            })
        
        yearly_df = pd.DataFrame(yearly_data)
        
        # Create area chart for amortization - updated with brand colors
        fig_area = go.Figure()
        
        fig_area.add_trace(go.Scatter(
            x=yearly_df["Year"],
            y=yearly_df["Principal"],
            name="Principal",
            mode='none',
            fill='tonexty',
            fillcolor=colors['primary'],
            line=dict(width=0)
        ))
        
        fig_area.add_trace(go.Scatter(
            x=yearly_df["Year"],
            y=yearly_df["Principal"] + yearly_df["Interest"],
            name="Interest",
            mode='none',
            fill='tonexty',
            fillcolor=colors['secondary'],
            line=dict(width=0)
        ))
        
        fig_area.update_layout(
            height=400,
            title="Yearly Payment Breakdown",
            xaxis_title="Year",
            yaxis_title="Amount (€)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=70, b=40)
        )
        
        col_area, col_balance = st.columns([3, 2])
        
        with st.container(border=True):
            with col_area:
                st.plotly_chart(fig_area, use_container_width=True)
            
            with col_balance:
                # Remaining balance chart - updated with brand colors
                fig_balance = go.Figure()
                
                fig_balance.add_trace(go.Scatter(
                    x=yearly_df["Year"],
                    y=yearly_df["Remaining Balance"],
                    name="Remaining Balance",
                    line=dict(color=colors['primary'], width=3),
                    mode="lines+markers"
                ))
                
                fig_balance.update_layout(
                    height=400,
                    title="Remaining Loan Balance",
                    xaxis_title="Year",
                    yaxis_title="Remaining Balance (€)",
                    margin=dict(l=20, r=20, t=70, b=40)
                )
                
                st.plotly_chart(fig_balance, use_container_width=True)
    
    # Additional insights about the loan
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # Calculate when 50% of the loan is paid off
        half_paid_year = 0
        for i, row in yearly_df.iterrows():
            if row["Remaining Balance"] <= loan_amount / 2:
                half_paid_year = row["Year"]
                break
        
        st.html(f"""
        <div class="bank-card">
            <div class="bank-card-header">
                <span class="bank-card-title">Loan Milestones</span>
                <span class="bank-card-arrow">›</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div style="color: #555; font-size: 14px;">50% Paid Off:</div>
                <div style="font-weight: 500; font-size: 14px;">Year {half_paid_year}</div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div style="color: #555; font-size: 14px;">Interest Equals Principal:</div>
                <div style="font-weight: 500; font-size: 14px;">Year {min(loan_term_years // 2 + 2, loan_term_years)}</div>
            </div>
            
            <div style="height: 1px; background-color: #f0f0f0; margin: 15px 0;"></div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div style="color: #555; font-size: 14px;">Average Monthly Payment:</div>
                <div style="font-weight: 500; font-size: 14px;">€{monthly_payment:.0f}</div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <div style="color: #555; font-size: 14px;">Payment-to-Income Ratio:</div>
                <div style="font-weight: 500; font-size: 14px; color: {'#4DAA57' if monthly_payment / financial_vars['monthly_income'] * 100 < 30 else '#FF9500' if monthly_payment / financial_vars['monthly_income'] * 100 < 40 else '#E63946'};">
                    {monthly_payment / financial_vars['monthly_income'] * 100:.1f}%
                </div>
            </div>
        </div>
        """)
    
    with insight_col2:
        # Early payment scenarios
        st.html(f"""
        <div class="bank-card">
            <div class="bank-card-header">
                <span class="bank-card-title">Early Payment Savings</span>
                <span class="bank-card-arrow">›</span>
            </div>
            
            <div class="bank-widget" style="margin-bottom: 10px;">
                <div style="font-size: 13px; margin-bottom: 5px;">
                    If you pay an extra €100/month:
                </div>
                <div style="font-weight: 500; margin-bottom: 5px;">
                    Save ~€{(total_interest * 0.15):.0f} in interest
                </div>
                <div style="font-size: 12px; color: #666;">
                    Pay off ~{loan_term_years * 0.9:.1f} years early
                </div>
            </div>
            
            <div class="bank-widget" style="margin-bottom: 10px;">
                <div style="font-size: 13px; margin-bottom: 5px;">
                    If you pay an extra €200/month:
                </div>
                <div style="font-weight: 500; margin-bottom: 5px;">
                    Save ~€{(total_interest * 0.25):.0f} in interest
                </div>
                <div style="font-size: 12px; color: #666;">
                    Pay off ~{loan_term_years * 0.75:.1f} years early
                </div>
            </div>
        </div>
        """)


def render_enhanced_property_details():
    """Render an enhanced version of the property details with st.html"""
    price_per_sqm = st.session_state.property_data["price"] / st.session_state.property_data["size"]
    current_year = datetime.now().year
    property_age = current_year - st.session_state.property_data["year"]
    
    property_html = f"""
    <div class="bank-card">
        <div class="bank-card-header">
            <span class="bank-card-title">{st.session_state.property_data["type"]} in {st.session_state.property_data["address"].split(',')[1] if ',' in st.session_state.property_data["address"] else st.session_state.property_data["address"]}</span>
            <span class="bank-card-arrow">›</span>
        </div>
        
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background-color: #FFF4E6; color: #FF9500; font-weight: 500; padding: 5px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">
                {st.session_state.property_data["condition"]}
            </div>
            <div style="background-color: #f8f9fa; color: #555; padding: 5px 10px; border-radius: 4px; font-size: 14px;">
                Energy: {st.session_state.property_data["energy_rating"]}
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Price</div>
                <div style="font-weight: 500; font-size: 16px;">€{st.session_state.property_data["price"]:,}</div>
                <div style="color: #708090; font-size: 12px;">€{price_per_sqm:,.0f}/m²</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Size</div>
                <div style="font-weight: 500; font-size: 16px;">{st.session_state.property_data["size"]} m²</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Year Built</div>
                <div style="font-weight: 500; font-size: 16px;">{st.session_state.property_data["year"]}</div>
                <div style="color: #708090; font-size: 12px;">{property_age} years old</div>
            </div>
        </div>
        
        <div style="height: 1px; background-color: #f0f0f0; margin: 15px 0;"></div>
        
        <div style="color: #555; font-size: 14px; margin-bottom: 5px;">Address</div>
        <div style="font-weight: 500; font-size: 15px;">{st.session_state.property_data["address"]}</div>
    </div>
    """
    st.html(property_html)

def render_enhanced_property_price_comparison():
    """Render an enhanced version of the property price comparison with st.html"""
    current_year = datetime.now().year
    price_per_sqm = st.session_state.property_data["price"] / st.session_state.property_data["size"]
    
    # Calculate area price trends
    years = list(range(current_year-4, current_year+1))
    base_price = 5000
    price_data = []
    
    for year in years:
        growth = 1 + (year - (current_year-4)) * 0.03
        price = base_price * growth
        price_data.append({"Year": year, "Price per m²": price})
    
    price_df = pd.DataFrame(price_data)
    avg_price_current = price_df[price_df["Year"] == current_year]["Price per m²"].values[0]
    price_diff = price_per_sqm - avg_price_current
    price_diff_pct = (price_diff / avg_price_current) * 100
    
    # Create the price comparison HTML
    comparison_html = f"""
    <div class="bank-card">
        <div class="bank-card-header">
            <span class="bank-card-title">Price Comparison</span>
            <span class="bank-card-arrow">›</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Area Average</div>
                <div style="font-weight: 500; font-size: 16px;">€{avg_price_current:,.0f}/m²</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">This Property</div>
                <div style="font-weight: 500; font-size: 16px;">€{price_per_sqm:,.0f}/m²</div>
                <div style="color: {'#4DAA57' if price_diff_pct <= 0 else '#FF9500'}; font-size: 12px;">
                    {price_diff_pct:.1f}% {'below' if price_diff_pct <= 0 else 'above'} average
                </div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">5-Year Trend</div>
                <div style="font-weight: 500; font-size: 16px; color: #4DAA57;">
                    +{(price_df.iloc[-1]["Price per m²"] / price_df.iloc[0]["Price per m²"] - 1) * 100:.1f}%
                </div>
            </div>
        </div>
        
        <div class="bank-notice">
            <strong>Neighborhood Assessment:</strong> This property is priced {price_diff_pct:.1f}% {'below' if price_diff_pct <= 0 else 'above'} 
            the area average. The area has shown a {(price_df.iloc[-1]["Price per m²"] / price_df.iloc[0]["Price per m²"] - 1) * 100:.1f}% 
            price growth over the past 5 years.
        </div>
    </div>
    """
    st.html(comparison_html)

def render_enhanced_renovation_summary():
    """Render an enhanced version of the renovation summary with st.html if renovations exist"""
    if not st.session_state.property_data["upcoming_renovations"]:
        return
    
    current_year = datetime.now().year
    renovation_df = pd.DataFrame(st.session_state.property_data["upcoming_renovations"])
    renovation_df["Years Until"] = renovation_df["year"] - current_year
    renovation_df["Monthly Reserve"] = renovation_df["estimated_cost"] / ((renovation_df["year"] - current_year) * 12)
    total_renovation_cost = renovation_df["estimated_cost"].sum()
    
    # Create the renovation summary HTML
    renovations_html = f"""
    <div class="bank-card">
        <div class="bank-card-header">
            <span class="bank-card-title">Upcoming Renovations</span>
            <span class="bank-card-arrow">›</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Total Cost</div>
                <div style="font-weight: 500; font-size: 16px;">€{total_renovation_cost:,}</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Monthly Reserve</div>
                <div style="font-weight: 500; font-size: 16px;">€{total_renovation_cost / ((max(renovation_df['year']) - current_year) * 12):.0f}</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #555; font-size: 13px;">Next Renovation</div>
                <div style="font-weight: 500; font-size: 16px;">{min(renovation_df['year'])}</div>
                <div style="color: #708090; font-size: 12px;">{min(renovation_df['Years Until']):.0f} years</div>
            </div>
        </div>
        
        <div style="height: 1px; background-color: #f0f0f0; margin: 15px 0;"></div>
    """
    
    # Add each renovation to the HTML
    for _, renovation in renovation_df.iterrows():
        renovations_html += f"""
        <div class="bank-item">
            <div style="flex-grow: 1;">
                <div style="font-weight: 500; font-size: 14px;">{renovation['type']} ({renovation['year']})</div>
                <div style="color: #708090; font-size: 12px;">{renovation['impact']}</div>
            </div>
            <div style="font-weight: 500; font-size: 14px; color: #E63946; margin-left: 10px;">€{renovation['estimated_cost']:,}</div>
            <div style="width: 15px; text-align: right; color: #FF9500;">›</div>
        </div>
        """
    
    renovations_html += """
    </div>
    """
    
    st.html(renovations_html)

def render_loan_calculator():
    st.subheader("Personal Budget Calculator")
    
    with st.container(border=True):
        col_img, col_text = st.columns([0.5, 3])
        with col_img:
            st.image("https://github.com/immone/streamlit_demo_small/blob/main/assets/decision.png?raw=true", width=175)
        
        with col_text:
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <strong>What is this tool?</strong> 
                <br>
                <br>
                This evaluates your financial situation by analyzing your monthly income, expenses, and loan details by comparing the impact of different loan options on your finances.
                <br>
                This calculator uses the same financial information you provided in the "Key Financial Information" section. Any changes you make there will be reflected here automatically.
            </div>
                    """, unsafe_allow_html=True)
        
    monthly_interest = ir / 100 / 12
    num_payments = lt * 12
    monthly_payment = (la * monthly_interest * (1 + monthly_interest) ** num_payments) / (
        (1 + monthly_interest) ** num_payments - 1
    )
    
    payment_to_income = (monthly_payment / mi) * 100
    total_debt_ratio = ((monthly_payment + ol) / mi) * 100
    disposable_income = mi - me - monthly_payment - ol
    
    # Display key metrics with enhanced look using st.html
    metrics_html = f"""
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <div class="bank-metric">
            <div class="bank-metric-label">Monthly Payment</div>
            <div class="bank-metric-value" style="color: #FF9500;">€{monthly_payment:.0f}</div>
        </div>
        <div class="bank-metric">
            <div class="bank-metric-label">Payment to Income</div>
            <div class="bank-metric-value" style="color: {'#4DAA57' if payment_to_income < 30 else '#FF9500' if payment_to_income < 40 else '#E63946'};">{payment_to_income:.1f}%</div>
        </div>
        <div class="bank-metric">
            <div class="bank-metric-label">Total Debt Ratio</div>
            <div class="bank-metric-value" style="color: {'#4DAA57' if total_debt_ratio < 35 else '#FF9500' if total_debt_ratio < 45 else '#E63946'};">{total_debt_ratio:.1f}%</div>
        </div>
        <div class="bank-metric">
            <div class="bank-metric-label">Leftover Income</div>
            <div class="bank-metric-value" style="color: {'#4DAA57' if disposable_income > 0 else '#E63946'};">€{disposable_income:.0f}</div>
        </div>
    </div>
    """
    st.html(metrics_html)
    
    # Keep the original UI inputs but enhance with some spacing
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    col_inputs, col_results = st.columns([3, 2])
    
    with col_inputs:
        st.markdown("### Your Monthly Budget", unsafe_allow_html=False)
        with st.container(border=True):
            
            monthly_income = st.number_input("Monthly Net Income (€)", 
                                        value=financial_vars["monthly_income"], 
                                        key="calc_monthly_income")
            
            st.markdown("##### Monthly Expenses")
            col1, col2 = st.columns(2)
            with col1:
                living_expenses = st.number_input("Living Expenses (€)", 
                                                value=financial_vars["monthly_expenses"], 
                                                key="calc_living_expenses")
                other_expenses = st.number_input("Other Expenses (€)", 
                                            value=800, 
                                            key="calc_other_expenses")
            
            with col2:
                savings_investments = st.number_input("Savings / Investments (€)", 
                                                    value=600, 
                                                    key="calc_savings")
                current_housing = st.number_input("Current Housing Costs (€)", 
                                                value=financial_vars["other_loans"], 
                                                key="calc_current_housing")
            
            st.markdown("---")
            st.markdown("##### Loan Impact Calculator")
            st.markdown("""
            <div class="bank-notice">
                <strong>Note:</strong> Using loan parameters from the "Key Financial Information" section.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div class="bank-widget" style="flex: 1; margin-right: 5px; text-align: center;">
                    <div style="font-size: 13px; color: #555;">Loan Amount</div>
                    <div style="font-weight: 500; font-size: 15px;">€{la:,}</div>
                </div>
                <div class="bank-widget" style="flex: 1; margin-right: 5px; text-align: center;">
                    <div style="font-size: 13px; color: #555;">Term</div>
                    <div style="font-weight: 500; font-size: 15px;">{lt} years</div>
                </div>
                <div class="bank-widget" style="flex: 1; text-align: center;">
                    <div style="font-size: 13px; color: #555;">Interest Rate</div>
                    <div style="font-weight: 500; font-size: 15px;">{ir}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    monthly_payment = (la * monthly_interest * (1 + monthly_interest) ** num_payments) / (
        (1 + monthly_interest) ** num_payments - 1
    )
    
    net_income_after_expenses = monthly_income - living_expenses - other_expenses - savings_investments - current_housing
    leftover_after_loan = net_income_after_expenses - monthly_payment + current_housing
    
    with col_results:
        st.markdown("#### Loan Term Options")
        with st.container(border=True):
            payment_to_income = (monthly_payment / monthly_income) * 100
            
            # Create enhanced debt ratio indicator
            st.html(f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:1rem; font-weight:500; margin-bottom:10px;">Payment to Income Ratio: {payment_to_income:.1f}%</div>
                <div style="display:flex; align-items:center;">
                    <div class="bank-progress-bar" style="flex-grow:1;">
                        <div class="bank-progress-fill" style="width:{min(payment_to_income * 2, 100)}%; background-color:{
                            '#4DAA57' if payment_to_income < 30 else
                            '#FF9500' if payment_to_income < 40 else
                            '#E63946'
                        };"></div>
                    </div>
                    <div style="margin-left:10px; font-weight:500; color: {
                        '#4DAA57' if payment_to_income < 30 else
                        '#FF9500' if payment_to_income < 40 else
                        '#E63946'
                    };">
                        {
                            'Good' if payment_to_income < 30 else
                            'Moderate' if payment_to_income < 40 else
                            'High'
                        }
                    </div>
                </div>
            </div>
            """)
            
            terms = [15, 20, 25, 30]
            term_data = []
            for term in terms:
                term_monthly = (la * (ir/100/12) * (1 + ir/100/12)**(term*12)) / ((1 + ir/100/12)**(term*12) - 1)
                term_total_interest = term_monthly * term * 12 - la
                term_data.append({
                    "Term (years)": term, 
                    "Monthly Payment": term_monthly, 
                    "Total Interest": term_total_interest,
                    "Total Cost": term_monthly * term * 12,
                })
            
            term_df = pd.DataFrame(term_data)
            
            # Create an enhanced HTML table for loan term options
            term_table_html = """
            <div class="bank-widget" style="margin-top: 15px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <th style="text-align: left; padding: 8px;">Term (years)</th>
                            <th style="text-align: right; padding: 8px;">Monthly Payment</th>
                            <th style="text-align: right; padding: 8px;">Total Interest</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, row in term_df.iterrows():
                term_table_html += f"""
                    <tr style="border-bottom: 1px solid #f0f0f0;">
                        <td style="padding: 8px;">{row['Term (years)']}</td>
                        <td style="text-align: right; padding: 8px; font-family: 'Calibri Light', monospace;">€{row['Monthly Payment']:.0f}</td>
                        <td style="text-align: right; padding: 8px; font-family: 'Calibri Light', monospace;">€{row['Total Interest']:,.0f}</td>
                    </tr>
                """
            
            term_table_html += """
                    </tbody>
                </table>
            </div>
            """
            
            st.html(term_table_html)
            
            # Also display the original dataframe for comparison functionality
            term_display = term_df.copy()
            term_display["Monthly Payment"] = term_display["Monthly Payment"].round().astype(int).apply(lambda x: f"€{x:,}")
            term_display["Total Interest"] = term_display["Total Interest"].round().astype(int).apply(lambda x: f"€{x:,}")
            term_display["Total Cost"] = term_display["Total Cost"].round().astype(int).apply(lambda x: f"€{x:,}")
            ui.table(term_display)
            
            st.markdown('</div>', unsafe_allow_html=True)

def render_enhanced_scenario_comparison(current_values, scenario_values, scenario_name, scenario_description):
    """
    Render enhanced comparison of financial values before and after a life event scenario
    """
    # Extract values for readability
    original_income = current_values["income"]
    original_expenses = current_values["expenses"]
    original_payment = current_values["payment"]
    original_maintenance = current_values["maintenance"]
    original_renovations = current_values["renovations"]
    original_leftover = current_values["leftover"]
    original_dti = current_values["dti"]
    
    new_income = scenario_values["income"]
    new_expenses = scenario_values["expenses"]
    new_payment = scenario_values["payment"]
    new_leftover = scenario_values["leftover"]
    new_dti = scenario_values["dti"]
    
    # Determine colors based on financial health
    leftover_color = "#4DAA57" if new_leftover > 0 else "#E63946"
    dti_color = "#4DAA57" if new_dti < 40 else "#FF9500" if new_dti < 50 else "#E63946"
    
    # Create HTML for the comparison display
    html = f"""
    <div class="bank-card">
        <div class="bank-card-header">
            <span class="bank-card-title">{scenario_name} Scenario</span>
            <span class="bank-card-arrow">›</span>
        </div>
        
        <div class="bank-widget" style="margin-bottom: 20px;">
            <p style="margin: 0; font-size: 14px;">{scenario_description}</p>
        </div>
        
        <div style="display: flex; margin-bottom: 15px;">
            <div style="flex: 1; border-right: 1px solid #f0f0f0; padding-right: 15px;">
                <div style="font-weight: 500; font-size: 16px; margin-bottom: 10px; color: #333;">Before</div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Monthly Income:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #4DAA57;">€{original_income:.0f}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Monthly Expenses:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #E63946;">€{original_expenses:.0f}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Loan Payment:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #E63946;">€{original_payment:.0f}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Housing Costs:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #E63946;">€{original_maintenance + original_renovations:.0f}</div>
                </div>
                
                <div style="height: 1px; background-color: #f0f0f0; margin: 10px 0;"></div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px; font-weight: 500;">Leftover:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #4DAA57;">€{original_leftover:.0f}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between;">
                    <div style="color: #555; font-size: 14px;">Payment-to-Income:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {"#4DAA57" if original_dti < 40 else "#FF9500" if original_dti < 50 else "#E63946"};">
                        {original_dti:.1f}%
                    </div>
                </div>
            </div>
            
            <div style="flex: 1; padding-left: 15px;">
                <div style="font-weight: 500; font-size: 16px; margin-bottom: 10px; color: #333;">After</div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Monthly Income:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {("#4DAA57" if new_income >= original_income else "#E63946")};">
                        €{new_income:.0f}
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Monthly Expenses:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {("#4DAA57" if new_expenses <= original_expenses else "#E63946")};">
                        €{new_expenses:.0f}
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Loan Payment:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {("#4DAA57" if new_payment <= original_payment else "#E63946")};">
                        €{new_payment:.0f}
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px;">Housing Costs:</div>
                    <div style="font-weight: 500; font-size: 14px; color: #E63946;">€{original_maintenance + original_renovations:.0f}</div>
                </div>
                
                <div style="height: 1px; background-color: #f0f0f0; margin: 10px 0;"></div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="color: #555; font-size: 14px; font-weight: 500;">Leftover:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {leftover_color};">€{new_leftover:.0f}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between;">
                    <div style="color: #555; font-size: 14px;">Payment-to-Income:</div>
                    <div style="font-weight: 500; font-size: 14px; color: {dti_color};">{new_dti:.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="bank-notice" style="background-color: {
            "#F0FFF4" if new_leftover > 300 else 
            "#FFF4E6" if new_leftover > 0 else 
            "#FFF5F5"
        }; border-left: 4px solid {
            "#4DAA57" if new_leftover > 300 else 
            "#FF9500" if new_leftover > 0 else 
            "#E63946"
        };">
            <div style="font-size: 14px; font-weight: 500; margin-bottom: 5px;">
                Risk Assessment: {
                    "Low Risk" if new_leftover > 300 else 
                    "Moderate Risk" if new_leftover > 0 else 
                    "High Risk"
                }
            </div>
            <div style="font-size: 13px;">
                {
                    f"Your finances could likely handle this scenario with €{new_leftover:.0f} left over each month." if new_leftover > 300 else
                    f"This scenario leaves you with very little buffer (€{new_leftover:.0f}/month). Consider building an emergency fund." if new_leftover > 0 else
                    f"This scenario would create a monthly deficit of €{abs(new_leftover):.0f}. You would need savings or additional income to cover expenses."
                }
            </div>
        </div>
    </div>
    """
    
    st.html(html)

def render_enhanced_interest_scenario_card(scenario, base_scenario=None):
    """
    Render an enhanced card for an interest rate scenario
    """
    # Extract values for readability
    rate = scenario["Rate"]
    monthly_payment = scenario["Monthly Payment"]
    dti_ratio = scenario["DTI Ratio"]
    color = scenario["Color"]
    scenario_name = scenario["Scenario"]
    
    # Calculate difference if base scenario is provided
    payment_diff = ""
    payment_pct = ""
    if base_scenario is not None:
        payment_difference = monthly_payment - base_scenario["Monthly Payment"]
        payment_percentage = (payment_difference / base_scenario["Monthly Payment"]) * 100
        payment_diff = f"+€{payment_difference:.0f}" if payment_difference > 0 else f"-€{abs(payment_difference):.0f}"
        payment_pct = f"({payment_percentage:.1f}%)" if payment_percentage != 0 else ""
    
    html = f"""
    <div style="background-color: white; border-left: 4px solid {color}; border-radius: 5px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px;">
        <div style="font-weight: 500; font-size: 15px; margin-bottom: 8px; color: #333;">
            {scenario_name}
        </div>
        
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="flex-grow: 1; font-size: 22px; font-weight: 600; color: {color};">€{monthly_payment:.0f}</div>
            <div style="text-align: right; font-size: 13px; color: #708090;">{payment_diff} {payment_pct}</div>
        </div>
        
        <div style="display: flex; align-items: center;">
            <div class="bank-progress-bar" style="flex-grow: 1;">
                <div class="bank-progress-fill" style="width:{min(dti_ratio * 2, 100)}%; background-color: {color};"></div>
            </div>
            <div style="font-size: 12px; margin-left: 10px; color: #555; min-width: 75px;">DTI: {dti_ratio:.1f}%</div>
        </div>
    </div>
    """
    
    return html

def render_financial_risk_simulator():
    # Add global variables declaration to fix scope issues
    global colors, mi, me, ol, la, lt, ir, monthly_payment, monthly_maintenance, renovation_cost_monthly

    st.subheader("Financial Risk Simulator")
    risk_tab1, risk_tab2 = st.tabs(["Interest Rate Risk Scenarios", "Life Event Scenarios"])
    with risk_tab1:
        with st.container(border=True):
            col_img, col_text = st.columns([0.5, 3])
            
            with col_img:
                st.image("https://github.com/immone/streamlit_demo_small/blob/main/assets/decision.png?raw=true", width=300)
                
            with col_text:
                st.markdown("""
                <div class="bank-widget" style="padding: 20px; margin-bottom: 20px;">
                    <strong>What is this tool?</strong>
                    <br>
                    This tool helps you simulate the financial impact of major life events and economic changes on your mortgage and overall financial health.
                    <br><br>
                    <strong> Interest Rate Risk Changes</strong><br>
                    Simulates how interest rate changes would impact your immediate monthly budget and lifestyle as well as total cost of your loan and long-term wealth building.
                    <br><br>
                    <strong> Life Event Scenarios </strong><br>
                    Simulates how unexpected life events would affect your finances. 
                </div>
                """, unsafe_allow_html=True)
        
        # Define the interest rate increase scenarios
        rate_scenarios = [2, 4, 6]
        
        # Get current details
        current_rate = ir
        loan_amount = la
        loan_term = lt
        monthly_income = mi
        
        # Base calculation - current payment
        monthly_interest = current_rate / 100 / 12
        current_payment = monthly_payment  # Use the globally calculated value
        current_total_interest = current_payment * loan_term * 12 - loan_amount
        current_dti = (current_payment / monthly_income) * 100
        
        # Calculate payments for each scenario
        scenario_data = []
        
        # Add current scenario
        scenario_data.append({
            "Scenario": f"Current\n({current_rate:.1f}%)",
            "Monthly Payment": current_payment,
            "Total Interest": current_total_interest,
            "DTI Ratio": current_dti,
            "Rate": current_rate,
            "Color": colors['primary']
        })
        
        # Add each rate increase scenario
        for rate_increase in rate_scenarios:
            new_rate = current_rate + rate_increase
            new_monthly_interest = new_rate / 100 / 12
            new_payment = (loan_amount * new_monthly_interest * (1 + new_monthly_interest) ** (loan_term*12)) / (
                (1 + new_monthly_interest) ** (loan_term*12) - 1
            )
            new_total_interest = new_payment * loan_term * 12 - loan_amount
            new_dti = (new_payment / monthly_income) * 100
            
            # Determine risk level and color based on DTI ratio
            if new_dti < 40:
                risk_level = "Moderate Risk"
                color = colors['primary']
            elif new_dti < 50:
                risk_level = "High Risk"
                color = colors['warning']
            else:
                risk_level = "Severe Risk"
                color = "#E63946"  # Red color for severe risk
            
            scenario_data.append({
                "Scenario": f"+{rate_increase}%\n({new_rate:.1f}%)",
                "Monthly Payment": new_payment,
                "Total Interest": new_total_interest,
                "DTI Ratio": new_dti,
                "Risk Level": risk_level,
                "Rate": new_rate,
                "Color": color
            })
        
        
        scenario_df = pd.DataFrame(scenario_data)
        
        # Display in two subtabs: Immediate Impact and Long-term Effects
        immediate_tab, longterm_tab = st.tabs(["Monthly Budget Impact", "Long-Term Financial Effects"])
        
        # Immediate Impact Tab
        with immediate_tab:  
            # Display key metrics in cards at the top
            st.markdown("### Monthly Changes in Expenses")
            with st.container(border=True):
                
                subcols = st.columns(len(scenario_data))
                
                # Calculate lifestyle impacts for each scenario
                lifestyle_impacts = []
                
                # Base lifestyle categories and costs
                lifestyle_categories = [
                    {"name": "Dining Out", "cost": 200, "priority": "low"},
                    {"name": "Entertainment", "cost": 150, "priority": "low"},
                    {"name": "Vacation Savings", "cost": 180, "priority": "medium"},
                    {"name": "Shopping", "cost": 120, "priority": "low"},
                    {"name": "Hobbies", "cost": 100, "priority": "medium"},
                    {"name": "Fitness", "cost": 80, "priority": "high"}
                ]
                
                # For each scenario, calculate what lifestyle changes would be needed
                for i, scenario in enumerate(scenario_data):
                    if i == 0:  # Skip the current scenario
                        lifestyle_impacts.append([])
                        continue
                        
                    payment_diff = scenario["Monthly Payment"] - scenario_data[0]["Monthly Payment"]
                    
                    # Track what needs to be cut to compensate
                    cuts_needed = []
                    remaining_to_cut = payment_diff
                    
                    # Sort lifestyle categories by priority (low priority gets cut first)
                    sorted_categories = sorted(lifestyle_categories, key=lambda x: {"low": 0, "medium": 1, "high": 2}[x["priority"]])
                    
                    for category in sorted_categories:
                        if remaining_to_cut <= 0:
                            break
                            
                        if remaining_to_cut >= category["cost"]:
                            # Need to cut this entirely
                            cuts_needed.append({
                                "category": category["name"],
                                "amount": category["cost"],
                                "percentage": 100
                            })
                            remaining_to_cut -= category["cost"]
                        else:
                            # Partial cut needed
                            percentage = (remaining_to_cut / category["cost"]) * 100
                            cuts_needed.append({
                                "category": category["name"],
                                "amount": remaining_to_cut,
                                "percentage": percentage
                            })
                            remaining_to_cut = 0
                    
                    lifestyle_impacts.append(cuts_needed)
            
                for i, scenario in enumerate(scenario_data):
                    with subcols[i]:
                        risk_color = scenario.get("Color", colors['primary'])
                        payment_change = ""
                        
                        delta_value = None
                        delta_color = "normal"
                        
                        if i > 0:  # Not the current scenario
                            payment_diff = scenario["Monthly Payment"] - scenario_data[0]["Monthly Payment"]
                            payment_pct = (payment_diff / scenario_data[0]["Monthly Payment"]) * 100
                            delta_value = f"€{payment_diff:.0f} ({payment_pct:.1f}%)"
                            delta_color = "off" if payment_diff <= 0 else "normal"  # Green for decreases, red for increases
                        
                        # Use st.metric for the main payment display
                        st.metric(
                            label=scenario["Scenario"],
                            value=f"€{scenario['Monthly Payment']:.0f}",
                            delta=delta_value,
                            delta_color="inverse"
                        )
                        
                        # Add DTI ratio as a caption or small text below
                        st.caption(f"DTI: {scenario['DTI Ratio']:.1f}%")
                        

            
            # Two columns for Monthly Budget and Lifestyle Impact
            col1, col2 = st.columns([1.25, 1])
            
            with col1:
                # Impact on Monthly Budget
                with st.container(border=True):
                    
                    # Define consistent colors
                    expense_colors = {
                        "Other Expenses": "#E0E0E0",         # Light gray
                        "Other Loans": "#BDBDBD",            # Medium gray
                        "Housing Costs": "#9E9E9E",          # Dark gray
                        "Mortgage Payment": "#616161"        # Very dark gray
                    }
                    
                    # Disposable income color thresholds
                    disposable_colors = {
                        "healthy": "#4CAF50",   # Green (>25%)
                        "ok": "#FF9800",        # Orange (10-25%)
                        "tight": "#FF5722",     # Deep orange (0-10%)
                        "negative": "#E53935"   # Red (negative)
                    }
                    
                    # Create data for stacked bar charts showing budget impact
                    budget_data = []
                    
                    # Define budget categories with consistent colors
                    expense_categories = [
                        {"name": "Other Expenses", "amount": financial_vars["monthly_expenses"], "color": expense_colors["Other Expenses"]},
                        {"name": "Other Loans", "amount": financial_vars["other_loans"], "color": expense_colors["Other Loans"]},
                        {"name": "Housing Costs", "amount": monthly_maintenance + renovation_cost_monthly, "color": expense_colors["Housing Costs"]}
                    ]
                    
                    # Calculate disposable income for each scenario
                    for i, scenario in enumerate(scenario_data):
                        # Fixed expenses (excluding mortgage)
                        fixed_expenses = sum([cat["amount"] for cat in expense_categories])
                        
                        # Calculate disposable income
                        disposable = monthly_income - fixed_expenses - scenario["Monthly Payment"]
                        disposable_pct = disposable / monthly_income * 100
                        
                        # Determine color for disposable income based on percentage
                        if disposable <= 0:
                            disposable_color = disposable_colors["negative"]
                        elif disposable_pct < 10:
                            disposable_color = disposable_colors["tight"]
                        elif disposable_pct < 25:
                            disposable_color = disposable_colors["ok"]
                        else:
                            disposable_color = disposable_colors["healthy"]
                        
                        # Add mortgage payment to budget data
                        budget_data.append({
                            "Category": "Mortgage Payment",
                            "Amount": scenario["Monthly Payment"],
                            "Scenario": scenario["Scenario"],
                            "Color": expense_colors["Mortgage Payment"]
                        })
                        
                        # Add expenses to budget data
                        for category in expense_categories:
                            budget_data.append({
                                "Category": category["name"],
                                "Amount": category["amount"],
                                "Scenario": scenario["Scenario"],
                                "Color": category["color"]
                            })
                        
                        # Add disposable income to budget data
                        budget_data.append({
                            "Category": "Disposable Income",
                            "Amount": disposable,
                            "Scenario": scenario["Scenario"],
                            "Color": disposable_color
                        })
                    
                    # Create DataFrame for budget visualization
                    budget_df = pd.DataFrame(budget_data)
                 
                    # Add each category as a bar segment in specific order (bottom to top)
                    fig_budget = go.Figure()

                    # Add each category as a bar segment in specific order (bottom to top)
                    for category in ["Other Expenses", "Other Loans", "Housing Costs", "Mortgage Payment", "Disposable Income"]:
                        category_data = budget_df[budget_df["Category"] == category]
                        
                        fig_budget.add_trace(go.Bar(
                            x=category_data["Scenario"],
                            y=category_data["Amount"],
                            name=category,
                            marker=dict(
                                color=category_data["Color"],
                                line=dict(width=0)
                            ),
                            hovertemplate=f"{category}: €%{{y:.0f}}<extra></extra>"
                        ))

                    # Add invisible scatter trace for "Total Income" legend item
                    fig_budget.add_trace(go.Scatter(
                        x=[None],
                        y=[None],
                        mode="lines",
                        name=f"Total Income",  # Legend entry
                        line=dict(
                            color=colors['primary'],
                            width=2,
                            dash="dash"
                        ),
                        showlegend=True
                    ))

                    # Update layout
                    fig_budget.update_layout(
                        barmode='stack',
                        height=300,
                        margin=dict(l=20, r=20, t=10, b=20),
                        legend=dict(
                            orientation="v",
                            yanchor="bottom",
                            y=0.15,
                            xanchor="center",
                            x=1.135
                        ),
                        yaxis_title="Monthly Amount (€)",
                        xaxis_title="Interest Rate Change",
                        font=dict(family="Calibri Light"),
                        plot_bgcolor="white"
                    )

                    # Add a horizontal line for total income (white line)
                    fig_budget.add_shape(
                        type="line",
                        x0=-0.5,
                        x1=len(scenario_data) - 0.5,
                        y0=monthly_income,
                        y1=monthly_income,
                        line=dict(
                            color=colors['primary'],
                            width=2,
                            dash="dash"
                        )
                    )

                    # Add annotation for income line (white text)
                    fig_budget.add_annotation(
                        x=0,
                        y=monthly_income,
                        text=f"Total Income: €{monthly_income:.0f}",
                        showarrow=False,
                        yshift=15,
                        font=dict(
                            size=11,
                            color="black"
                        )
                    )

                    st.markdown("""
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; font-size: 0.8em;">
                        <div><span style="display: inline-block; width: 8px; height: 8px; background-color: #4CAF50; margin-right: 5px;"></span>Healthy (&gt;25%)</div>
                        <div><span style="display: inline-block; width: 8px; height: 8px; background-color: #FF9800; margin-right: 5px;"></span>OK (10-25%)</div>
                        <div><span style="display: inline-block; width: 8px; height: 8px; background-color: #FF5722; margin-right: 5px;"></span>High Risk (0-10%)</div>
                        <div><span style="display: inline-block; width: 8px; height: 8px; background-color: #E53935; margin-right: 5px;"></span>Severe Risk</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(fig_budget, use_container_width=True)
                    
                    # Add a legend explaining disposable income colors
                  
                            
            with col2:
                # Lifestyle Impact Analysis - using tabs for each scenario
                #st.markdown("### Lifestyle Impact Analysis")
                
                # Create tabs for the scenarios with increased rates (skip current)
                with st.container(border=True):
                    impact_tabs = st.tabs([scenario["Scenario"] for scenario in scenario_data[1:]])
                    
                    for i, tab in enumerate(impact_tabs):
                        scenario_idx = i + 1  # Skip the first scenario (current)
                        scenario = scenario_data[scenario_idx]
                        payment_diff = scenario["Monthly Payment"] - scenario_data[0]["Monthly Payment"]
                        
                        with tab:
                            # Create a table of lifestyle impacts
                            impact_data = []
                            remaining = payment_diff
                            
                            for category in lifestyle_categories:
                                if remaining <= 0:
                                    impact = 0
                                    status = "No Change"
                                elif remaining >= category["cost"]:
                                    impact = category["cost"]
                                    status = "Eliminate"
                                    remaining -= category["cost"]
                                else:
                                    impact = remaining
                                    pct = (impact / category["cost"]) * 100
                                    status = f"Reduce by {pct:.0f}%"
                                    remaining = 0
                                    
                                impact_data.append({
                                    "Category": category["name"],
                                    "Current Budget": f"€{category['cost']}",
                                    "Potential Cut": f"€{impact:.0f}",
                                    "Status": status,
                                    "Priority": category["priority"].capitalize()
                                })
                            
                            # Display the table using ui.table
                            impact_df = pd.DataFrame(impact_data)

                            # Define a function to apply conditional highlighting
                            def highlight_status(val):
                                if "Reduce" in str(val):
                                    return 'background-color: orange'
                                elif val == "Eliminate":
                                    return 'background-color: red'
                                else:
                                    return ''

                            # Apply the styling and display the table
                            styled_df = impact_df.style.applymap(highlight_status, subset=['Status'])

                            # Display the styled DataFrame in Streamlit
                            st.dataframe(styled_df, hide_index=True)
                            
        
        # Long-term effects tab
        with longterm_tab:
            
            # Two columns for the long-term effects
            col1, col2 = st.columns(2)
            
            with col1:
                # Total Interest Comparison
                st.markdown("### Total Interest Paid Over Loan Term")
                with st.container(border=True):
                
                    # Create horizontal bar chart for total interest
                    fig_interest = go.Figure()
                    
                    for i, scenario in enumerate(scenario_data):
                        interest_increase = ""
                        if i > 0:  # Not the current scenario
                            interest_diff = scenario["Total Interest"] - scenario_data[0]["Total Interest"]
                            interest_diff_formatted = f"+€{interest_diff/1000:.0f}k" if interest_diff >= 1000 else f"+€{interest_diff:.0f}"
                        else:
                            interest_diff_formatted = ""
                        
                        fig_interest.add_trace(go.Bar(
                            y=[scenario["Scenario"]],
                            x=[scenario["Total Interest"]],
                            orientation='h',
                            name=scenario["Scenario"],
                            marker=dict(color=scenario.get("Color", colors['primary'])),
                            text=[f"€{scenario['Total Interest']/1000:.0f}k {interest_diff_formatted}"],
                            textposition='outside',
                            hovertemplate=f"Total Interest: €{scenario['Total Interest']:,.0f}"
                        ))
                    
                    fig_interest.update_layout(
                        height=210,
                        margin=dict(l=20, r=20, t=10, b=10),
                        xaxis_title="Total Interest (€)",
                        yaxis_title="",
                        showlegend=False,
                        barmode='group',
                        font=dict(family="Calibri Light"),
                        plot_bgcolor="white"
                    )
                    
                    st.plotly_chart(fig_interest, use_container_width=True)
            
            with col2:
                # Calculate wealth-building impact (for the table only, not showing the chart)
                retirement_data = []
                investment_return = 7.0  # Annual return percentage
                investment_years = 25  # Years of investment 
                
                for scenario in scenario_data:
                    # How much disposable income would be left
                    fixed_expenses = sum([cat["amount"] for cat in expense_categories])
                    disposable = monthly_income - fixed_expenses - scenario["Monthly Payment"]
                    
                    # Assume baseline savings is 15% of income
                    baseline_savings = monthly_income * 0.15
                    
                    # Actual savings capability would be limited by disposable income
                    actual_savings = min(baseline_savings, disposable)
                    
                    # Monthly savings gap
                    savings_gap = baseline_savings - actual_savings if actual_savings < baseline_savings else 0
                    
                    # Calculate long-term impact of savings gap
                    future_value = 0
                    if savings_gap > 0:
                        # Calculate future value using compound interest formula
                        r = investment_return / 100 / 12  # Monthly interest rate
                        n = investment_years * 12  # Number of months
                        future_value = savings_gap * ((1 + r)**n - 1) / r * (1 + r)
                    
                    retirement_data.append({
                        "Scenario": scenario["Scenario"],
                        "Monthly Savings Gap": savings_gap,
                        "25-Year Impact": future_value
                    })
                
                # Overall financial impact table
                st.markdown("### Cumulative Financial Impact")
                
                impact_data = []
                
                with st.container(border=True):

                    for scenario in scenario_data:
                        # Calculate additional interest compared to current
                        additional_interest = scenario["Total Interest"] - scenario_data[0]["Total Interest"] if scenario != scenario_data[0] else 0
                        
                        # Find corresponding retirement impact
                        retirement_impact = next((item["25-Year Impact"] for item in retirement_data if item["Scenario"] == scenario["Scenario"]), 0)
                        
                        # Total financial impact
                        total_impact = additional_interest + retirement_impact
                        
                        impact_data.append({
                            "Scenario": scenario["Scenario"],
                            "Additional Interest": f"€{additional_interest/1000:.0f}k",
                            "Lost Retirement Savings": f"€{retirement_impact/1000:.0f}k",
                            "Total Financial Impact": f"€{total_impact/1000:.0f}k"
                        })
                    
                    # Display the table using HTML instead of ui.table
                    impact_df = pd.DataFrame(impact_data)
                    ui.table(impact_df)
        
        # Risk Assessment at the bottom of the main tab
        
        with st.expander("Affordability Risk Assessment"):
        
            # Create a data frame for the risk assessment
            risk_assessment = []
            
            for scenario in scenario_data:
                dti = scenario["DTI Ratio"]
                
                if dti < 30:
                    risk_level = "Low Risk"
                    color = "#4DAA57"  # Green
                    description = "Comfortable affordability level"
                elif dti < 40:
                    risk_level = "Moderate Risk"
                    color = colors['primary']  # Orange
                    description = "Watch your budget carefully"
                elif dti < 50:
                    risk_level = "High Risk"
                    color = colors['warning']  # Darker Orange
                    description = "Financial strain likely"
                else:
                    risk_level = "Severe Risk"
                    color = "#E63946"  # Red
                    description = "May lead to financial hardship"
                
                risk_assessment.append({
                    "Scenario": scenario["Scenario"],
                    "DTI Ratio": dti,
                    "Risk Level": risk_level,
                    "Description": description,
                    "Color": color
                })
            
            # Create risk assessment table with more compact design
            with st.container(border=True):
                for risk in risk_assessment:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; background-color: white; margin-bottom: 8px; border-radius: 5px; padding: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <div style="width: 20%; font-weight: bold; font-size: 0.9rem;">{risk['Scenario']}</div>
                        <div style="width: 25%;">
                            <div style="background-color: #f0f0f0; border-radius: 10px; height: 15px; position: relative;">
                                <div style="position: absolute; top: 0; left: 0; height: 100%; width: {min(risk['DTI Ratio'] * 2, 100)}%; background-color: {risk['Color']}; border-radius: 10px;"></div>
                                <div style="position: absolute; width: 100%; text-align: center; font-size: 10px; line-height: 15px;">{risk['DTI Ratio']:.1f}%</div>
                            </div>
                        </div>
                        <div style="width: 20%; text-align: center;">
                            <span style="background-color: {risk['Color']}; color: white; padding: 3px 7px; border-radius: 10px; font-size: 10px;">
                                {risk['Risk Level']}
                            </span>
                        </div>
                        <div style="width: 35%; font-size: 12px; color: #666;">{risk['Description']}</div>
                    </div>
                    """, unsafe_allow_html=True)


    with risk_tab2:
            with st.container(border=True):
                col_img, col_text = st.columns([0.5, 3])
                with col_img:
                    st.image("https://github.com/immone/streamlit_demo_small/blob/main/assets/decision.png?raw=true", width=300)
                    
                with col_text:
                    st.markdown("""
                    <div class="bank-widget" style="padding: 20px; margin-bottom: 20px;">
                        <strong>What is this tool?</strong>
                        <br>
                        This tool helps you simulate the financial impact of major life events and economic changes on your mortgage and overall financial health.
                        <br><br>
                        <strong> Interest Rate Risk Changes</strong><br>
                        Simulates how interest rate changes would impact your immediate monthly budget and lifestyle as well as total cost of your loan and long-term wealth building.
                        <br><br>
                        <strong> Life Event Scenarios </strong><br>
                        Simulates how unexpected life events would affect your finances. 
                    </div>
                    """, unsafe_allow_html=True)
            risk_scenarios = {
                "Divorce": {
                    "income_change": -40,
                    "expense_change": +25,
                    "description": "Separation typically causes a significant drop in household income while expenses may increase due to maintaining two households, legal fees, and other separation costs."
                },
                "Having a Child": {
                    "income_change": -15,
                    "expense_change": +20,
                    "description": "Having a child often leads to temporary income reduction (parental leave) and increased expenses for childcare, healthcare, food, clothing, etc."
                },
                "Job Loss": {
                    "income_change": -70,
                    "expense_change": -10,
                    "description": "Losing your job results in a major income drop, partially offset by unemployment benefits. Some expenses might be reduced due to budget cuts."
                },
                "Medical Emergency": {
                    "income_change": -20,
                    "expense_change": +15,
                    "description": "A serious health issue can reduce your ability to work while increasing out-of-pocket medical expenses, even with insurance coverage."
                },
                "Housing Market Crash": {
                    "income_change": -5,
                    "expense_change": +0,
                    "rate_change": +2.0,
                    "description": "A market crash doesn't directly affect income, but if you have a variable-rate mortgage, interest rates might rise significantly, increasing monthly payments."
                },
                "Unexpected Home Repairs": {
                    "income_change": 0,
                    "expense_change": +15,
                    "description": "Major repairs like roof replacement, plumbing issues, or foundation problems can create significant unexpected expenses."
                }
            }

            # Let user select scenario to analyze
            selected_scenario = st.selectbox(
                "Select a life event to simulate:",
                list(risk_scenarios.keys()),
                key="life_event_selector"
            )
            
            scenario = risk_scenarios[selected_scenario]
            
            with st.container(border=True):
                # Display scenario details
                st.markdown(f"""
                ### {selected_scenario} Scenario
                
                **Description:** {scenario['description']}
                
                **Financial Impact:**
                - Income change: {scenario['income_change']}%
                - Expense change: {scenario['expense_change']}%
                {f"- Interest rate change: +{scenario['rate_change']}%" if 'rate_change' in scenario else ""}
                """)

            with st.container(border=True):
            
                # Calculate the financial impact
                original_income = mi
                original_expenses = me
                original_payment = monthly_payment
                
                # Calculate new values
                new_income = original_income * (1 + scenario['income_change']/100)
                new_expenses = original_expenses * (1 + scenario['expense_change']/100)
                
                # Calculate new payment if interest rate changes
                new_payment = original_payment
                if 'rate_change' in scenario:
                    new_rate = ir + scenario['rate_change']
                    new_payment = (la * (new_rate/100/12) * (1 + new_rate/100/12)**(lt*12)) / ((1 + new_rate/100/12)**(lt*12) - 1)
                
                # Calculate financial health indicators
                original_leftover = original_income - original_expenses - original_payment - monthly_maintenance - renovation_cost_monthly
                new_leftover = new_income - new_expenses - new_payment - monthly_maintenance - renovation_cost_monthly
                
                original_dti = (original_payment / original_income) * 100
                new_dti = (new_payment / new_income) * 100
                
                # Display comparison
                col1x, col2x = st.columns(2)
                
                with col1x:
                    st.markdown("### Before")
                    st.markdown(f"""
                    - **Monthly Income:** €{original_income:.0f}
                    - **Monthly Expenses:** €{original_expenses:.0f}
                    - **Loan Payment:** €{original_payment:.0f}
                    - **Housing Costs:** €{monthly_maintenance + renovation_cost_monthly:.0f}
                    - **Leftover:** €{original_leftover:.0f}
                    - **Payment-to-Income Ratio:** {original_dti:.1f}%
                    """)
                
                with col2x:
                    st.markdown("### After")
                    leftover_color = "green" if new_leftover > 0 else "red"
                    dti_color = "green" if new_dti < 40 else "orange" if new_dti < 50 else "red"
                    
                    st.markdown(f"""
                    - **Monthly Income:** €{new_income:.0f}
                    - **Monthly Expenses:** €{new_expenses:.0f}
                    - **Loan Payment:** €{new_payment:.0f}
                    - **Housing Costs:** €{monthly_maintenance + renovation_cost_monthly:.0f}
                    - **Leftover:** <span style="color:{leftover_color}">€{new_leftover:.0f}</span>
                    - **Payment-to-Income Ratio:** <span style="color:{dti_color}">{new_dti:.1f}%</span>
                    """, unsafe_allow_html=True)
                
                # Risk assessment
                if new_leftover < 0:
                    st.error(f"**High Risk**: This scenario would create a monthly deficit of €{abs(new_leftover):.0f}. You would need savings or additional income to cover expenses.")
                elif new_leftover < 300:
                    st.warning(f"**Moderate Risk**: This scenario leaves you with very little buffer (€{new_leftover:.0f}/month). Consider building an emergency fund.")
                else:
                    st.success(f"**Low Risk**: Your finances could likely handle this scenario with €{new_leftover:.0f} left over each month.")
                
                # Recommendations
                with st.expander("Preparation Recommendations"):
                    if selected_scenario == "Divorce":
                        st.markdown("""
                        - Build an emergency fund covering 6+ months of expenses
                        - Consider income protection insurance
                        - Maintain your own credit history and some separate finances
                        - Understand all joint financial commitments
                        """)
                    elif selected_scenario == "Having a Child":
                        st.markdown("""
                        - Save for parental leave periods before having children
                        - Research childcare costs and options in your area
                        - Check eligibility for family benefits and tax deductions
                        - Consider life and health insurance updates
                        """)
                    elif selected_scenario == "Job Loss":
                        st.markdown("""
                        - Build an emergency fund covering 6+ months of expenses
                        - Keep skills updated and network active
                        - Consider unemployment insurance options
                        - Have a budget-cutting plan ready for essential vs non-essential expenses
                        """)
                    elif selected_scenario == "Medical Emergency":
                        st.markdown("""
                        - Ensure adequate health insurance coverage
                        - Build an emergency fund for out-of-pocket expenses
                        - Consider income protection/disability insurance
                        - Understand your sick leave entitlements
                        """)
                    elif selected_scenario == "Housing Market Crash":
                        st.markdown("""
                        - Consider fixed-rate mortgage options
                        - Don't overextend on housing debt
                        - Have a plan for handling increased payments
                        - Build equity by paying down principal when possible
                        """)
                    elif selected_scenario == "Unexpected Home Repairs":
                        st.markdown("""
                        - Build a dedicated home maintenance fund (1-3% of home value annually)
                        - Get regular home inspections and maintenance
                        - Consider home warranty coverage for major systems
                        - Maintain adequate home insurance
                        """)



 

# -------------------- TAB STRUCTURE --------------------
tab1, tab2, tab3 = st.tabs(["Loan Decision Center", "Payment Analysis", "Property Details"])

# -------------------- TAB 1: LOAN DECISION CENTER WITH SUBTABS --------------------
with tab1:
    # Create subtabs to organize the content better - now includes the Financial Risk Simulator
    summary_subtab, calculator_subtab, recommender_subtab, risk_simulator_subtab = st.tabs([
        "Financial Impact", 
        "Loan Calculator", 
        "Loan Setup Recommender",
        "Financial Risk Simulator"
    ])
    
    with summary_subtab:
        render_financial_summary()
    
    with calculator_subtab:
        render_loan_calculator()
    
    with recommender_subtab:
        render_loan_recommender()
        
    with risk_simulator_subtab:
        render_financial_risk_simulator()

# -------------------- TAB 2: PAYMENT ANALYSIS --------------------
with tab2:
    render_payment_analysis()

# -------------------- TAB 3: PROPERTY DETAILS --------------------
with tab3:
    st.markdown("<h2>Property Details</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### Location")
        map_data = pd.DataFrame({
            'lat': [st.session_state.property_data["latitude"]],
            'lon': [st.session_state.property_data["longitude"]]
        })
            
        st.map(map_data, zoom=13)
        
    with st.container(border=True):
        col_property, col_trends = st.columns([1, 1])
        
        with col_property:
            # Render enhanced property details
            render_enhanced_property_details()
            
            # Render enhanced monthly housing costs
            #render_enhanced_monthly_housing_costs()
            
            # Render enhanced renovation summary if available
            render_enhanced_renovation_summary()
        
        with col_trends:
            # Render enhanced property price comparison
            render_enhanced_property_price_comparison()
            
            # Keep the original price trend chart for visualization
            current_year = datetime.now().year
            years = list(range(current_year-4, current_year+1))
            base_price = 5000
            price_data = []
            
            for year in years:
                growth = 1 + (year - (current_year-4)) * 0.03
                price = base_price * growth
                price_data.append({"Year": year, "Price per m²": price})
            
            price_df = pd.DataFrame(price_data)
            price_per_sqm = st.session_state.property_data["price"] / st.session_state.property_data["size"]        
            
            fig_price = px.bar(
                price_df,
                x="Year",
                y="Price per m²",
                title="Area Price Trends (€/m²)",
                height=300,
                color_discrete_sequence=[colors['primary']]
            )
            
            fig_price.add_scatter(
                x=[current_year],
                y=[price_per_sqm],
                mode="markers",
                marker=dict(size=12, color=colors['secondary'], symbol="diamond"),
                name="This Property"
            )
            
            fig_price.update_layout(
                yaxis_title="Price (€/m²)",
                showlegend=True,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            with st.container(border=True):
                st.plotly_chart(fig_price, use_container_width=True)

# -------------------- KEY FINANCIAL INFORMATION SECTION --------------------
with st.expander("Press to change financial parameters"):
    col3, col4 = st.columns(2)
    with col3:
        lt = st.slider("Loan Term (years)", min_value=10, max_value=30, value=lt, key="global_loan_term")
    with col4:
        ir = st.slider("Interest Rate (%)", min_value=1.0, max_value=10.0, value=ir, step=0.1, key="global_interest_rate")
    
    col1, col2 = st.columns(2)
    with col1:
        mi = st.number_input("Monthly Net Income (€)", value=mi, key="global_monthly_income")
        me = st.number_input("Monthly Expenses (€)", value=me, key="global_monthly_expenses")
        sd = st.number_input("Existing Student Debt (€)", value=sd, key="global_student_debt")
        ms = st.number_input("Monthly Student Payment (€)", value=ms, key="global_student_payment")
    with col2:
        la = st.number_input("Loan Amount (€)", value=la, key="global_loan_amount")
        dp = st.number_input("Down Payment (€)", value=dp, key="global_down_payment")
        oa = st.number_input("Other Assets (€)", value=oa, key="global_other_assets")
    
    # Recalculate financial metrics
    monthly_payment = (la * (ir/100/12) * (1 + ir/100/12)**(lt*12)) / ((1 + ir/100/12)**(lt*12) - 1)
    loan_to_value = (la / (la + dp)) * 100
    debt_to_income = ((monthly_payment + ms) / mi) * 100
    disposable_income = mi - me - monthly_payment - ms
    asset_to_loan_ratio = (oa / la) * 100
    total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
    total_housing_ratio = (total_monthly_housing_cost / mi) * 100
    risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
    risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
    
    st.markdown("""
    <div class="bank-notice" style="margin-top: 15px;">
        <strong>Financial Summary:</strong> Based on your inputs, your monthly loan payment will be 
        <strong>€{:.0f}</strong> with a loan-to-value ratio of <strong>{:.1f}%</strong> and 
        debt-to-income ratio of <strong>{:.1f}%</strong>.
    </div>
    """.format(monthly_payment, loan_to_value, debt_to_income), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)