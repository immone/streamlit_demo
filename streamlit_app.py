import streamlit as st
import pandas as pd
import numpy as np
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

property_data = {
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
    "energy_rating": "C"
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

st.markdown(f"""
    <style>
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
    .info-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['primary']};
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    .warning-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['warning']};
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    .success-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['success']};
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    .kpi-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: 'Calibri Light', 'Calibri', sans-serif;
    }}
    .kpi-label {{
        font-size: 0.9rem;
        color: {colors['slate']};
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        font-weight: 500;
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    
    /* Improved clean finance styles */
    .finance-table {{
        width: 100%;
        border-spacing: 0;
        font-size: 16px;
        margin-bottom: 20px;
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    
    .finance-table tr {{
        height: 40px;
    }}
    
    .finance-table td {{
        padding: 8px 0;
    }}
    
    .finance-table tr.total-row {{
        border-top: 1px solid #ddd;
        font-weight: 700;
    }}
    
    .finance-table .amount {{
        text-align: right;
        font-family: 'Calibri Light', 'Calibri', monospace;
        font-weight: 600;
    }}
    
    .finance-table .positive {{
        color: {colors['positive']};
    }}
    
    .finance-table .negative {{
        color: {colors['negative']};
    }}
    
    .finance-card {{
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 1.5rem;
        height: 100%;
        margin-bottom: 20px;
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    
    /* Number input styling */
    .stNumberInput [data-testid="stNumberInput"] > div > div > input {{
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 500;
    }}
    
    /* Slider styling */
    .stSlider [data-testid="stSlider"] {{
        font-family: 'Calibri Light', 'Calibri', sans-serif;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        font-family: 'Calibri Light', 'Calibri', sans-serif !important;
    }}
    
    /* General text styling */
    p, div, span {{
        font-family: 'Calibri Light', 'Calibri', sans-serif;
        font-weight: 300;
    }}
    
    /* Style for dataframe cells to color positive/negative values */
    [data-testid="stDataFrame"] td:nth-child(2) {{
        font-family: 'Calibri Light', 'Calibri', monospace;
        font-weight: 600;
    }}
    
    [data-testid="stDataFrame"] td:nth-child(2):contains("+") {{
        color: #4DAA57 !important;
    }}
    
    [data-testid="stDataFrame"] td:nth-child(2):contains("-") {{
        color: #E63946 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------- APP TITLE --------------------
st.markdown("<h1 class='main-header'>Housing Loan Advisor</h1>", unsafe_allow_html=True)

# -------------------- SIDEBAR: PROPERTY DETAILS & API --------------------
with st.sidebar:
    # Add OP Bank logo at the top of the sidebar
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Back-to-the-future-logo.svg/1600px-Back-to-the-future-logo.svg.png", width=250)
    
    st.markdown("### Apartment Search")
    st.markdown("Enter an Oikotie apartment URL to fetch property details:")
    apt_url = st.text_input("Apartment URL", "https://asunnot.oikotie.fi/myytavat-asunnot/helsinki/22930110")
    
    if st.button("Fetch Property Data"):
        selected_address = random.choice(helsinki_addresses)
        property_data["price"] = random.randint(300000, 500000)
        property_data["size"] = random.randint(40, 120)
        property_data["type"] = random.choice(["Apartment", "House", "Townhouse"])
        property_data["year"] = random.randint(1950, datetime.now().year)
        property_data["address"] = selected_address["address"]
        property_data["latitude"] = selected_address["latitude"]
        property_data["longitude"] = selected_address["longitude"]
        property_data["maintenance_fee"] = random.randint(180, 350)
        property_data["condition"] = random.choice(["Excellent", "Good", "Satisfactory", "Poor"])
        property_data["energy_rating"] = random.choice(["A", "B", "C", "D", "E", "F", "G"])
        
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
            estimated_cost = round(cost_per_sqm * property_data["size"])
            renovations.append({
                "year": renovation_year,
                "type": renovation["type"],
                "estimated_cost": estimated_cost,
                "impact": renovation["impact"]
            })
        
        property_data["upcoming_renovations"] = renovations
        st.success("Property data fetched successfully!")
    
    st.markdown("### Property Details")
    st.markdown(f"**Price:** €{property_data['price']:,}")
    st.markdown(f"**Size:** {property_data['size']} m²")
    st.markdown(f"**Type:** {property_data['type']}")
    st.markdown(f"**Year:** {property_data['year']}")
    st.markdown(f"**Address:** {property_data['address']}")
    st.markdown(f"**Maintenance Fee:** €{property_data['maintenance_fee']}/month")

# -------------------- LOAN & FINANCIAL PARAMETERS --------------------
mi = financial_vars["monthly_income"]
me = financial_vars["monthly_expenses"]
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

monthly_maintenance = property_data["maintenance_fee"]
renovation_cost_monthly = sum([r["estimated_cost"] for r in property_data["upcoming_renovations"]]) / (10 * 12) if property_data["upcoming_renovations"] else 0
total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
total_housing_ratio = (total_monthly_housing_cost / mi) * 100

risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
risk_color = colors['success'] if risk_score < 20 else colors['primary'] if risk_score < 35 else colors['warning']

# Now show the financial info UI if selected (but calculations are already done)
# Always start by setting the financial variables from the stored state
# This ensures calculations are done regardless of UI visibility
mi = financial_vars["monthly_income"]
me = financial_vars["monthly_expenses"]
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

monthly_maintenance = property_data["maintenance_fee"]
renovation_cost_monthly = sum([r["estimated_cost"] for r in property_data["upcoming_renovations"]]) / (10 * 12) if property_data["upcoming_renovations"] else 0
total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
total_housing_ratio = (total_monthly_housing_cost / mi) * 100

risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
risk_color = colors['success'] if risk_score < 20 else colors['primary'] if risk_score < 35 else colors['warning']

# Now show the financial info UI if selected (but calculations are already done)
show_financial_info = st.checkbox("Show Key Financial Information", value=True)
if show_financial_info:
    st.markdown("### Key Financial Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        financial_vars["monthly_income"] = st.number_input("Monthly Net Income (€)", value=financial_vars["monthly_income"], key="global_monthly_income")
        financial_vars["monthly_expenses"] = st.number_input("Monthly Expenses (€)", value=financial_vars["monthly_expenses"], key="global_monthly_expenses")
        financial_vars["other_loans"] = st.number_input("Other Monthly Loan Payments (€)", value=financial_vars["other_loans"], key="global_other_loans")

    with col2:
        financial_vars["loan_amount"] = st.number_input("Loan Amount (€)", value=financial_vars["loan_amount"], key="global_loan_amount")
        financial_vars["down_payment"] = st.number_input("Down Payment (€)", value=financial_vars["down_payment"], key="global_down_payment")
        financial_vars["other_assets"] = st.number_input("Other Assets (€)", value=financial_vars["other_assets"], key="global_other_assets")

    with col3:
        financial_vars["loan_term"] = st.slider("Loan Term (years)", min_value=10, max_value=30, value=financial_vars["loan_term"], key="global_loan_term")
        financial_vars["interest_rate"] = st.slider("Interest Rate (%)", min_value=1.0, max_value=10.0, value=financial_vars["interest_rate"], step=0.1, key="global_interest_rate")
    
    # Update our variables after user input changes
    mi = financial_vars["monthly_income"]
    me = financial_vars["monthly_expenses"]
    ol = financial_vars["other_loans"]
    oa = financial_vars["other_assets"]
    la = financial_vars["loan_amount"]
    dp = financial_vars["down_payment"]
    lt = financial_vars["loan_term"]
    ir = financial_vars["interest_rate"]
    
    # Recalculate financial metrics with updated values
    monthly_payment = (la * (ir/100/12) * (1 + ir/100/12)**(lt*12)) / ((1 + ir/100/12)**(lt*12) - 1)
    loan_to_value = (la / (la + dp)) * 100
    debt_to_income = ((monthly_payment + ol) / mi) * 100
    disposable_income = mi - me - monthly_payment - ol
    asset_to_loan_ratio = (oa / la) * 100
    total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
    total_housing_ratio = (total_monthly_housing_cost / mi) * 100
    risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
    risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
    risk_color = colors['success'] if risk_score < 20 else colors['primary'] if risk_score < 35 else colors['warning']

# -------------------- CALCULATIONS --------------------
monthly_payment = (la * (ir/100/12) * (1 + ir/100/12)**(lt*12)) / ((1 + ir/100/12)**(lt*12) - 1)
loan_to_value = (la / (la + dp)) * 100
debt_to_income = ((monthly_payment + ol) / mi) * 100
disposable_income = mi - me - monthly_payment - ol
asset_to_loan_ratio = (oa / la) * 100

monthly_maintenance = property_data["maintenance_fee"]
renovation_cost_monthly = sum([r["estimated_cost"] for r in property_data["upcoming_renovations"]]) / (10 * 12) if property_data["upcoming_renovations"] else 0
total_monthly_housing_cost = monthly_payment + monthly_maintenance + renovation_cost_monthly
total_housing_ratio = (total_monthly_housing_cost / mi) * 100

risk_score = (debt_to_income * 0.4 + loan_to_value * 0.4 - (disposable_income/mi)*20 - (asset_to_loan_ratio*0.1))
risk_category = "Low Risk" if risk_score < 20 else "Moderate Risk" if risk_score < 35 else "High Risk"
risk_color = colors['success'] if risk_score < 20 else colors['primary'] if risk_score < 35 else colors['warning']

# -------------------- ENHANCED REAL-WORLD STRESS SCENARIOS --------------------
scenarios = {
    "Divorce Settlement": {
        "income_drop": 40,
        "expense_increase": 25,
        "interest_increase": 0.5,
        "description": "Spouse leaves, reducing household income by 40%; legal fees, new housing costs, and living adjustments increase expenses by 25%; slight interest rate hike due to credit risk."
    },
    "Unexpected Medical Emergency": {
        "income_drop": 15,
        "expense_increase": 50,
        "interest_increase": 0.0,
        "description": "Serious illness reduces work capacity by 15% (sick leave); medical bills, treatments, and rehabilitation spike expenses by 50%; no direct interest rate impact."
    },
    "Housing Market Crash": {
        "income_drop": 10,
        "expense_increase": 5,
        "interest_increase": 2.0,
        "description": "Property value drops, affecting job security in related sectors (10% income drop); slight expense increase (5%) from market adjustments; interest rates rise 2% due to economic instability."
    },
    "Job Promotion Relocation": {
        "income_drop": 0,
        "expense_increase": 20,
        "interest_increase": 0.0,
        "description": "New job offer in a more expensive city increases income slightly but moving costs, higher rent during transition, and lifestyle adjustments raise expenses by 20%; no income loss due to Finland's employment support."
    }
}

scenario_results = {"Current": {
    "Monthly Payment": monthly_payment,
    "Cash Flow": disposable_income,
    "Payment to Income": (monthly_payment/mi*100),
    "Description": "Current financial situation with no disruptions."
}}
for scenario, params in scenarios.items():
    scenario_income = mi * (1 - params["income_drop"]/100)
    scenario_expenses = me * (1 + params["expense_increase"]/100)
    scenario_interest_rate = ir + params["interest_increase"]
    scenario_monthly_payment = (la * (scenario_interest_rate/100/12) * (1 + scenario_interest_rate/100/12)**(lt*12)) / ((1 + scenario_interest_rate/100/12)**(lt*12) - 1)
    scenario_cash_flow = scenario_income - scenario_expenses - scenario_monthly_payment - ol - monthly_maintenance - renovation_cost_monthly
    scenario_results[scenario] = {
        "Monthly Payment": scenario_monthly_payment,
        "Cash Flow": scenario_cash_flow,
        "Payment to Income": (scenario_monthly_payment/scenario_income*100),
        "Description": params["description"]
    }

# -------------------- FUNCTIONS FOR TABS --------------------

# Function for the Financial Impact Summary
def render_financial_summary():
    # Make the financial impact summary wider by not using columns for the main visualization
    st.subheader("Loan Impact Overview")
    
    # Key financial metrics display
    st.markdown("### Key Financial Indicators")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        ltv_color = "green" if loan_to_value < 80 else "orange" if loan_to_value < 90 else "red"
        st.markdown(f"""
        <div class="kpi-container" style="position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; cursor: help; color: #708090;" title="Loan amount divided by property value. Lower is better, indicating more equity. Banks typically prefer under 80%.">❓</div>
            <div class="kpi-value" style="color: {ltv_color};">{loan_to_value:.1f}%</div>
            <div class="kpi-label">Loan-to-Value</div>
            <div class="kpi-trend">{'Good' if loan_to_value < 80 else 'Moderate' if loan_to_value < 90 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        dti_color = "green" if debt_to_income < 35 else "orange" if debt_to_income < 45 else "red"
        st.markdown(f"""
        <div class="kpi-container" style="position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; cursor: help; color: #708090;" title="Monthly debt payments divided by monthly income. Banks typically prefer under 43%. Your €{monthly_payment:.0f} payment is {debt_to_income:.1f}% of your €{mi:.0f} income.">❓</div>
            <div class="kpi-value" style="color: {dti_color};">{debt_to_income:.1f}%</div>
            <div class="kpi-label">Debt-to-Income</div>
            <div class="kpi-trend">{'Good' if debt_to_income < 35 else 'Moderate' if debt_to_income < 45 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        thr_color = "green" if total_housing_ratio < 35 else "orange" if total_housing_ratio < 45 else "red"
        st.markdown(f"""
        <div class="kpi-container" style="position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; cursor: help; color: #708090;" title="Total housing costs (€{total_monthly_housing_cost:.0f}/month) divided by income (€{mi:.0f}/month). Includes mortgage, maintenance, and renovation reserves.">❓</div>
            <div class="kpi-value" style="color: {thr_color};">{total_housing_ratio:.1f}%</div>
            <div class="kpi-label">Housing Costs to Income</div>
            <div class="kpi-trend">{'Good' if total_housing_ratio < 35 else 'Moderate' if total_housing_ratio < 45 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-container" style="position: relative;">
            <div style="position: absolute; top: 10px; right: 10px; cursor: help; color: #708090;" title="Composite score based on LTV, DTI and other factors. Lower scores (under 20) indicate less financial risk. Your score is {risk_category}.">❓</div>
            <div class="kpi-value" style="color: {risk_color};">{risk_score:.1f}</div>
            <div class="kpi-label">Overall Risk Score</div>
            <div class="kpi-trend" style="color: {risk_color};">{risk_category}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display the chart - full width for better visibility
    st.markdown("### Monthly Budget Comparison")
    chart_data = pd.DataFrame({
        "Category": ["Incomes", "Living Expenses / Rent", "Other Expenses", "Savings/Investments", "Net Leftover"],
        "Before": [4000, -1200, -800, -600, 1400],
        "After": [4000, -1300, -800, -600, 900]
    })

    # Melt for plotly
    chart_melted = chart_data.melt(id_vars=["Category"], var_name="Scenario", value_name="Amount")
    
    # Basic bar chart with your original color scheme - now full width
    fig = px.bar(
        chart_melted, 
        x="Category", 
        y="Amount", 
        color="Scenario", 
        barmode="group",
        title="Before vs. After Comparison",
        color_discrete_map={"Before": "#FF9500", "After": "#FF5A00"}
    )
    fig.update_layout(height=350)  # Slightly taller for better visibility
    
    # Show the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # After the chart, show the detailed tables side by side
    st.markdown("### Detailed Monthly Budget")
    
    # Set up the data - keeping your original values
    before_data = {
        "Incomes": 4000,
        "Living Expenses + Rent": -1200,
        "Other Expenses (food, hobbies)": -800,
        "Savings/Investments": -600,
        "Net Leftover": 1400
    }
    after_data = {
        "Incomes": 4000,
        "Monthly Installment": -1300,
        "Living Expenses": -400,
        "Other Expenses (food, hobbies)": -800,
        "Savings/Investments": -600,
        "Net Leftover": 900
    }

    # Two columns side by side with improved styling
    col_before, col_after = st.columns(2)
    
    with col_before:
        st.markdown('<div class="finance-card">', unsafe_allow_html=True)
        st.markdown("#### Before Loan")
        
        # Create a DataFrame for the before data
        before_df = pd.DataFrame(list(before_data.items()), columns=["Category", "Amount (€)"])
        before_df["Amount (€)"] = before_df["Amount (€)"].apply(lambda x: f"+{x}€" if x > 0 else f"{x}€")
        st.dataframe(before_df, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_after:
        st.markdown('<div class="finance-card">', unsafe_allow_html=True)
        st.markdown("#### After Loan")
        
        # Create a DataFrame for the after data
        after_df = pd.DataFrame(list(after_data.items()), columns=["Category", "Amount (€)"])
        after_df["Amount (€)"] = after_df["Amount (€)"].apply(lambda x: f"+{x}€" if x > 0 else f"{x}€")
        st.dataframe(after_df, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_loan_calculator():
    st.subheader("Personal Budget Calculator")
    
    st.info("""
    This calculator uses the same financial information you provided in the "Key Financial Information" section. 
    Any changes you make there will be reflected here automatically.
    """)
    
    st.markdown("### Key Financial Metrics")
    
    monthly_interest = ir / 100 / 12
    num_payments = lt * 12
    monthly_payment = (la * monthly_interest * (1 + monthly_interest) ** num_payments) / (
        (1 + monthly_interest) ** num_payments - 1
    )
    
    payment_to_income = (monthly_payment / mi) * 100
    total_debt_ratio = ((monthly_payment + ol) / mi) * 100
    disposable_income = mi - me - monthly_payment - ol
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Payment", f"€{monthly_payment:.0f}")
    col2.metric("Payment to Income", f"{payment_to_income:.1f}%")
    col3.metric("Total Debt Ratio", f"{total_debt_ratio:.1f}%")
    col4.metric("Leftover Income", f"€{disposable_income:.0f}")
    
    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    
    col_inputs, col_results = st.columns([3, 2])
    
    with col_inputs:
        st.markdown('<div class="finance-card">', unsafe_allow_html=True)
        
        st.markdown("#### Your Monthly Budget")
        
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
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; font-size: 0.9rem;">
            <p style="margin-bottom: 0;">Using loan parameters from the "Key Financial Information" section above.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div><strong>Loan Amount:</strong> €{la:,}</div>
            <div><strong>Term:</strong> {lt} years</div>
            <div><strong>Interest Rate:</strong> {ir}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    monthly_payment = (la * monthly_interest * (1 + monthly_interest) ** num_payments) / (
        (1 + monthly_interest) ** num_payments - 1
    )
    
    net_income_after_expenses = monthly_income - living_expenses - other_expenses - savings_investments - current_housing
    leftover_after_loan = net_income_after_expenses - monthly_payment + current_housing
    
    with col_results:
        st.markdown('<div class="finance-card">', unsafe_allow_html=True)
        
        payment_to_income = (monthly_payment / monthly_income) * 100
        
        st.markdown("#### Financial Health Indicators")
        
        st.markdown(f"""
        <div style="margin-bottom:20px;">
            <div style="font-size:1rem; font-weight:500; margin-bottom:10px;">Payment to Income Ratio: {payment_to_income:.1f}%</div>
            <div style="display:flex; align-items:center;">
                <div style="flex-grow:1; height:8px; background-color:#f0f2f6; border-radius:4px;">
                    <div style="width:{min(payment_to_income * 2, 100)}%; height:100%; background-color:{
                        '#4DAA57' if payment_to_income < 30 else
                        '#FF9500' if payment_to_income < 40 else
                        '#E63946'
                    }; border-radius:4px;"></div>
                </div>
                <div style="margin-left:10px; font-weight:500;">
                    {
                        'Good' if payment_to_income < 30 else
                        'Moderate' if payment_to_income < 40 else
                        'High'
                    }
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Loan Term Options")
        
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
        
        # Bar plot removed as requested
        
        term_display = term_df.copy()
        term_display["Monthly Payment"] = term_display["Monthly Payment"].round().astype(int).apply(lambda x: f"€{x:,}")
        term_display["Total Interest"] = term_display["Total Interest"].round().astype(int).apply(lambda x: f"€{x:,}")
        term_display["Total Cost"] = term_display["Total Cost"].round().astype(int).apply(lambda x: f"€{x:,}")
        st.dataframe(term_display, hide_index=True, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Function for Loan Setup Recommender - UPDATED to ensure HTML renders properly
# Function for Loan Setup Recommender - MODIFIED to keep info on one page and fix rendering
def render_loan_recommender():
    # Header with clearer explanation
    st.subheader("Personalized Loan Setup Recommendations")
    
    # Create subtabs within the loan recommender
    info_subtab, recommendation_subtab = st.tabs(["Loan Information", "Loan Recommendation"])
    
    # First subtab: ALL information and inputs
    with info_subtab:
        # Add image placeholder in the left corner
        col_img, col_text = st.columns([1, 3])
        
        with col_img:
            st.image("https://via.placeholder.com/150x150?text=OP+Bank", width=150)
        
        with col_text:
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <strong>What This Tool Does:</strong> Analyzes your financial situation to recommend the optimal loan structure based on your priorities and real-world banking criteria.
                <br><br>
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
        
        with profile_col1:
            st.markdown(f"""
            <div style="padding: 15px; border: 1px solid #e6e6e6; border-radius: 5px; height: 100%;">
                <h5 style="color: #4DAA57; margin-top: 0;">Conservative Profile</h5>
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
            <div style="padding: 15px; border: 1px solid #e6e6e6; border-radius: 5px; height: 100%;">
                <h5 style="color: #FF9500; margin-top: 0;">Balanced Profile</h5>
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
            <div style="padding: 15px; border: 1px solid #e6e6e6; border-radius: 5px; height: 100%;">
                <h5 style="color: #FF5A00; margin-top: 0;">Growth-Focused Profile</h5>
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
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF9500; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You'll get a longer loan term (25-30 years) with 
                lower monthly payments (around €{growth_monthly:.0f}/month in your case), but will pay more in total interest over time.</p>
            </div>
            """, unsafe_allow_html=True)
        elif priority_option == "Balanced Approach":
            payment_priority = 3
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF9500; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You'll get a moderate loan term (around 25 years) 
                with reasonable monthly payments (around €{balanced_monthly:.0f}/month in your case) and moderate total interest costs.</p>
            </div>
            """, unsafe_allow_html=True)
        else:  # Lower Total Interest
            payment_priority = 5
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF9500; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You'll get a shorter loan term (15-20 years) with 
                higher monthly payments (around €{conservative_monthly:.0f}/month in your case), but will save significantly on total interest.</p>
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
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4DAA57; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You prefer financial security with higher down 
                payments (€{conservative_down:,.0f}+) and lower loan-to-value ratios (under 75%). This gives you better interest 
                rates and less risk if property values decline.</p>
            </div>
            """, unsafe_allow_html=True)
        elif risk_option == "Balanced":
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF9500; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You prefer a moderate approach with standard down 
                payments (around €{balanced_down:,.0f} or 20%) and conventional loan terms. This balances financial security with 
                keeping cash available for other needs.</p>
            </div>
            """, unsafe_allow_html=True)
        else:  # Aggressive options
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF5A00; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You're comfortable with higher financial leverage, 
                using lower down payments (around €{growth_down:,.0f} or 15%) and longer terms to maximize cash flow and investment 
                potential elsewhere.</p>
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
        <div style="margin-bottom: 15px;">
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
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4DAA57; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>Bank Examples:</strong> OP Bank and other major banks with stricter criteria. 
                They typically require debt-to-income ratios under 35%, loan-to-value ratios under 80%, 
                and excellent credit history.</p>
            </div>
            """, unsafe_allow_html=True)
        elif target_approval == "High (80-95%)":
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF9500; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>Bank Examples:</strong> Most Finnish banks including OP Bank. 
                They typically accept debt-to-income ratios up to 40%, loan-to-value ratios up to 85%, 
                and good credit history.</p>
            </div>
            """, unsafe_allow_html=True)
        elif target_approval == "Moderate (65-80%)":
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #FF5A00; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>Bank Examples:</strong> Some online lenders and smaller banks. 
                They may accept debt-to-income ratios up to 45%, loan-to-value ratios up to 90%, 
                and average credit history.</p>
            </div>
            """, unsafe_allow_html=True)
        else:  # Flexible
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #6c757d; border-radius: 4px; margin: 15px 0; font-size: 0.9rem;">
                <p style="margin-bottom: 0;"><strong>What this means:</strong> You'll see all options regardless of approval likelihood. 
                Some may require special considerations or programs that OP Bank might offer based on your unique situation.</p>
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
            st.info("""
            Please go to the 'Loan Information' tab and fill out your preferences, 
            then click 'Generate My Personalized Recommendation' to see your personalized loan setup.
            """)
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
            
            # FIXED FORMATTING for the recommendation display
            st.markdown(f"**Recommended: {rec['name']} Profile**", unsafe_allow_html=True)
            
            # Using properly formatted HTML with st.markdown()
            st.markdown(f"""
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
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-top: 15px;">
                <h5 style="margin-bottom: 10px;">Bank Approval Factors</h5>
                <p><strong>Loan-to-Value Ratio:</strong> <span style="color: {'green' if ltv_status == 'Excellent' else 'orange' if ltv_status == 'Good' else '#FF5A00'};">{ltv_status}</span> ({rec['ltv_ratio']:.1f}%)</p>
                <p><strong>Debt-to-Income Ratio:</strong> <span style="color: {'green' if dti_status == 'Excellent' else 'orange' if dti_status == 'Good' else '#FF5A00'};">{dti_status}</span> ({rec['dti_ratio']:.1f}%)</p>
                <p><strong>Overall Approval Likelihood:</strong> {rec['approval_odds']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-top: 15px; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
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
            """, unsafe_allow_html=True)
            
            # Key benefits and considerations section - clean formatting
            st.markdown("**Key Benefits**")
            benefits_list = "\n".join([f"* {benefit}" for benefit in rec["key_benefits"]])
            st.markdown(benefits_list)
            
            st.markdown("**Key Considerations**")
            considerations_list = "\n".join([f"* {consideration}" for consideration in rec["considerations"]])
            st.markdown(considerations_list)
            
            # Compare all options
            st.markdown("**Compare All Options**")
            
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
            st.markdown(f"**OP Bank Recommendation:** With your financial profile and this loan structure, you're an ideal candidate for OP Bank's mortgage services.", unsafe_allow_html=True)
            
            st.markdown(f"""
            <p style="margin-top: 10px;">Finnish lenders typically prefer loan-to-value ratios below 85% and debt-to-income 
            ratios below 40%. Your recommended option has {rec['ltv_ratio']:.1f}% LTV and {rec['dti_ratio']:.1f}% DTI, 
            making it a {ltv_status.lower()}/{dti_status.lower()} candidate for OP Bank's approval criteria.</p>
            
            <p style="margin-top: 10px;"><strong>Next steps:</strong> Schedule a meeting with an OP Bank advisor to get your pre-approval. 
            Ask about both fixed and variable rate options, and any available first-time homebuyer benefits that OP Bank offers.</p>
            """, unsafe_allow_html=True)

# Function for the Financial Risk Simulator
def render_financial_risk_simulator():
    st.subheader("Financial Risk Simulator")
    
    st.markdown("""
    This simulator helps you understand how different life events might impact your financial situation.
    See how well your current finances would handle these common scenarios.
    """)
    
    # Define realistic risk scenarios
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
        list(risk_scenarios.keys())
    )
    
    scenario = risk_scenarios[selected_scenario]
    
    # Display scenario details
    st.markdown(f"""
    ### {selected_scenario} Scenario
    
    **Description:** {scenario['description']}
    
    **Financial Impact:**
    - Income change: {scenario['income_change']}%
    - Expense change: {scenario['expense_change']}%
    {f"- Interest rate change: +{scenario['rate_change']}%" if 'rate_change' in scenario else ""}
    """)
    
    # Calculate the financial impact
    original_income = financial_vars["monthly_income"]
    original_expenses = financial_vars["monthly_expenses"]
    original_payment = monthly_payment
    
    # Calculate new values
    new_income = original_income * (1 + scenario['income_change']/100)
    new_expenses = original_expenses * (1 + scenario['expense_change']/100)
    
    # Calculate new payment if interest rate changes
    new_payment = original_payment
    if 'rate_change' in scenario:
        new_rate = financial_vars["interest_rate"] + scenario['rate_change']
        new_payment = (la * (new_rate/100/12) * (1 + new_rate/100/12)**(lt*12)) / ((1 + new_rate/100/12)**(lt*12) - 1)
    
    # Calculate financial health indicators
    original_leftover = original_income - original_expenses - original_payment - monthly_maintenance - renovation_cost_monthly
    new_leftover = new_income - new_expenses - new_payment - monthly_maintenance - renovation_cost_monthly
    
    original_dti = (original_payment / original_income) * 100
    new_dti = (new_payment / new_income) * 100
    
    # Display comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Before")
        st.markdown(f"""
        - **Monthly Income:** €{original_income:.0f}
        - **Monthly Expenses:** €{original_expenses:.0f}
        - **Loan Payment:** €{original_payment:.0f}
        - **Housing Costs:** €{monthly_maintenance + renovation_cost_monthly:.0f}
        - **Leftover:** €{original_leftover:.0f}
        - **Payment-to-Income Ratio:** {original_dti:.1f}%
        """)
    
    with col2:
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
    st.markdown("### Preparation Recommendations")
    
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

def render_payment_analysis():
    st.markdown("<h2>Payment Analysis</h2>", unsafe_allow_html=True)
    
    st.markdown("### Monthly Payment Breakdown")
    col_payment1, col_payment2 = st.columns([1, 1])
    
    with col_payment1:
        total_monthly = monthly_payment + monthly_maintenance + renovation_cost_monthly
        
        payment_data = pd.DataFrame({
            "Category": ["Loan Payment", "Maintenance Fee", "Renovation Reserve"],
            "Amount": [monthly_payment, monthly_maintenance, renovation_cost_monthly]
        })
        
        fig_payment = px.pie(
            payment_data, 
            names="Category", 
            values="Amount",
            color_discrete_sequence=[colors['primary'], colors['secondary'], colors['warning']],
            title="Monthly Housing Cost Breakdown"
        )
        fig_payment.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color="white", size=14),
            pull=[0.05, 0, 0]
        )
        fig_payment.update_layout(
            height=350, 
            margin=dict(t=50, b=20, l=20, r=20),
            title_font_size=16,
            font_family="Calibri Light"
        )
        st.plotly_chart(fig_payment, use_container_width=True)
    
    with col_payment2:
        st.markdown(f"### Total Monthly Housing Cost: €{total_monthly:.0f}")
        
        payment_breakdown = pd.DataFrame([
            {"Category": "Loan Payment", "Amount": f"€{monthly_payment:.0f}"},
            {"Category": "Maintenance Fee", "Amount": f"€{monthly_maintenance:.0f}"},
            {"Category": "Renovation Reserve", "Amount": f"€{renovation_cost_monthly:.0f}"}
        ])
        
        st.table(payment_breakdown)
    
    st.markdown("### Amortization Schedule")
    periods = lt * 12
    monthly_interest_rate = ir / 100 / 12
    balance = la
    amortization_data = []
    
    for period in range(1, periods + 1):
        interest_payment = balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        amortization_data.append({
            "Month": period,
            "Principal": principal_payment,
            "Interest": interest_payment,
            "Balance": max(balance, 0)
        })
        if balance <= 0:
            break
    
    amortization_df = pd.DataFrame(amortization_data)
    
    fig_amort = go.Figure()
    fig_amort.add_trace(go.Scatter(x=amortization_df["Month"], y=amortization_df["Principal"], name="Principal", line=dict(color=colors['primary'])))
    fig_amort.add_trace(go.Scatter(x=amortization_df["Month"], y=amortization_df["Interest"], name="Interest", line=dict(color=colors['secondary'])))
    fig_amort.update_layout(
        title="Loan Amortization Over Time",
        xaxis_title="Month",
        yaxis_title="Amount (€)",
        height=400,
        legend=dict(x=0.1, y=0.9),
        font_family="Calibri Light"
    )
    st.plotly_chart(fig_amort, use_container_width=True)

# Also update the improved monthly housing costs function for property details tab
def render_improved_monthly_housing_costs():
    st.markdown("### Monthly Housing Costs")
    
    col1, col2 = st.columns([3, 2])
    
    total_monthly_housing = monthly_maintenance + renovation_cost_monthly
    
    with col1:
        st.metric("Total Monthly Maintenance", f"€{total_monthly_housing:.0f}")
        
        st.markdown("#### Monthly Cost Breakdown")
        
        housing_costs = pd.DataFrame([
            {"Cost Type": "Maintenance Fee", "Amount": f"€{monthly_maintenance:.0f}", "Description": "Standard monthly fee paid to the housing company"},
            {"Cost Type": "Renovation Reserve", "Amount": f"€{renovation_cost_monthly:.0f}", "Description": "Recommended monthly savings for upcoming renovations"}
        ])
        
        st.table(housing_costs)
    
    with col2:
        st.markdown("#### Understanding Housing Costs")
        st.markdown("• **Maintenance Fee:** Paid monthly to the housing company for building upkeep, water, and common area maintenance.")
        st.markdown("• **Renovation Reserve:** Recommended savings for planned renovations. This helps avoid future financial surprises.")
        st.markdown("• **Total Cost:** The combined monthly expense beyond your mortgage payment.")
        
        st.info("**Pro Tip:** In Finland, older buildings often have lower purchase prices but higher maintenance fees and renovation needs.")

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
    
    col_property, col_trends = st.columns([1, 1])
    
    with col_property:
        price_per_sqm = property_data["price"] / property_data["size"]
        current_year = datetime.now().year
        property_age = current_year - property_data["year"]
        
        st.markdown(f"""
        <div class="info-card">
            <h4>{property_data["type"]} in {property_data["address"].split(',')[1] if ',' in property_data["address"] else property_data["address"]}</h4>
            <p><strong>Price:</strong> €{property_data["price"]:,} (€{price_per_sqm:,.0f}/m²)</p>
            <p><strong>Size:</strong> {property_data["size"]} m²</p>
            <p><strong>Year Built:</strong> {property_data["year"]} ({property_age} years old)</p>
            <p><strong>Condition:</strong> {property_data["condition"]}</p>
            <p><strong>Energy Rating:</strong> {property_data["energy_rating"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Improved Monthly Housing Costs section
        render_improved_monthly_housing_costs()
        
        if property_data["upcoming_renovations"]:
            with st.expander("View Upcoming Renovations Timeline & Insights"):
                renovation_df = pd.DataFrame(property_data["upcoming_renovations"])
                renovation_df["Years Until"] = renovation_df["year"] - current_year
                renovation_df["Monthly Reserve"] = renovation_df["estimated_cost"] / ((renovation_df["year"] - current_year) * 12)
                
                fig_renovation = px.timeline(
                    renovation_df,
                    x_start=renovation_df["year"].apply(lambda x: datetime(x, 1, 1)),
                    x_end=renovation_df["year"].apply(lambda x: datetime(x, 12, 31)),
                    y="type",
                    title="Renovation Timeline",
                    color="estimated_cost",
                    color_continuous_scale=[colors['primary'], colors['warning']],
                    labels={"type": "Renovation Type", "estimated_cost": "Cost (€)"}
                )
                fig_renovation.update_yaxes(categoryorder="total ascending")
                fig_renovation.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_renovation, use_container_width=True)
                
                st.markdown("#### Renovation Details & Planning Tips")
                total_renovation_cost = renovation_df["estimated_cost"].sum()
                st.markdown(f"**Total Renovation Cost:** €{total_renovation_cost:,}")
                st.markdown(f"**Average Monthly Reserve Needed:** €{total_renovation_cost / ((max(renovation_df['year']) - current_year) * 12):.0f}")
                st.markdown("""
                **Why This Matters:**
                - Upcoming renovations can significantly impact your monthly budget and property value.
                - Costs are spread over time, but unexpected delays or cost overruns are common.
                - In Finland, housing companies often increase maintenance fees to fund these projects.
                
                **Planning Tips:**
                - **Save Ahead:** Start setting aside the monthly reserve now to avoid financial strain later.
                - **Check Funding:** Ask the housing company if loans are planned—these could increase your monthly costs further.
                - **Tax Benefits:** Some renovations (e.g., energy efficiency upgrades) may qualify for tax deductions.
                - **Value Impact:** Renovations like facade or windows can boost resale value—consider timing if you plan to sell.
                """)
                
                for i, renovation in renovation_df.iterrows():
                    st.markdown(f"**{renovation['year']} ({renovation['Years Until']} years):** {renovation['type']} (€{renovation['estimated_cost']:,})")
                    st.markdown(f"- *Impact:* {renovation['impact']}")
                    st.markdown(f"- *Monthly Reserve:* €{renovation['Monthly Reserve']:.0f} (if saved from now)")
    
    with col_trends:
        st.markdown("### Neighborhood Price Comparison")
        
        years = list(range(current_year-4, current_year+1))
        base_price = 5000
        price_data = []
        
        for year in years:
            growth = 1 + (year - (current_year-4)) * 0.03
            price = base_price * growth
            price_data.append({"Year": year, "Price per m²": price})
        
        price_df = pd.DataFrame(price_data)
        
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
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        avg_price_current = price_df[price_df["Year"] == current_year]["Price per m²"].values[0]
        price_diff = price_per_sqm - avg_price_current
        price_diff_pct = (price_diff / avg_price_current) * 100
        
        st.markdown(f"""
        <div class="info-card">
            <p><strong>Area Average:</strong> €{avg_price_current:,.0f}/m²</p>
            <p><strong>This Property:</strong> €{price_per_sqm:,.0f}/m² 
               <span style="color: {'green' if price_diff_pct <= 0 else 'orange'}">
                  ({price_diff_pct:.1f}% {'below' if price_diff_pct <= 0 else 'above'} average)
               </span>
            </p>
            <p><strong>5-Year Trend:</strong> {(price_df.iloc[-1]["Price per m²"] / price_df.iloc[0]["Price per m²"] - 1) * 100:.1f}% growth</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Location")
        map_data = pd.DataFrame({
            'lat': [property_data["latitude"]],
            'lon': [property_data["longitude"]]
        })
        
        st.map(map_data, zoom=13)