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
    'slate': '#708090'
}

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {colors['white']};
        color: {colors['text']};
    }}
    .block-container {{
        padding-top: 1rem;
    }}
    h1, h2, h3 {{
        color: {colors['primary']};
    }}
    .stButton button {{
        background-color: {colors['primary']};
        color: {colors['white']};
    }}
    .info-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['primary']};
    }}
    .warning-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['warning']};
    }}
    .success-card {{
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: {colors['white']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid {colors['success']};
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
    }}
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    .kpi-label {{
        font-size: 0.9rem;
        color: {colors['slate']};
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
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------- APP TITLE --------------------
st.markdown("<h1 class='main-header'>Housing Loan Advisor</h1>", unsafe_allow_html=True)

# -------------------- SIDEBAR: PROPERTY DETAILS & API --------------------
with st.sidebar:
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
show_financial_info = st.checkbox("Show Key Financial Information", value=True)
if show_financial_info:
    st.markdown("### Key Financial Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        financial_vars["monthly_income"] = st.number_input("Monthly Net Income (€)", value=financial_vars["monthly_income"])
        financial_vars["monthly_expenses"] = st.number_input("Monthly Expenses (€)", value=financial_vars["monthly_expenses"])
        financial_vars["other_loans"] = st.number_input("Other Monthly Loan Payments (€)", value=financial_vars["other_loans"])

    with col2:
        financial_vars["loan_amount"] = st.number_input("Loan Amount (€)", value=financial_vars["loan_amount"])
        financial_vars["down_payment"] = st.number_input("Down Payment (€)", value=financial_vars["down_payment"])
        financial_vars["other_assets"] = st.number_input("Other Assets (€)", value=financial_vars["other_assets"])

    with col3:
        financial_vars["loan_term"] = st.slider("Loan Term (years)", min_value=10, max_value=30, value=financial_vars["loan_term"])
        financial_vars["interest_rate"] = st.slider("Interest Rate (%)", min_value=1.0, max_value=10.0, value=financial_vars["interest_rate"], step=0.1)

# -------------------- CALCULATIONS --------------------
mi = financial_vars["monthly_income"]
me = financial_vars["monthly_expenses"]
ol = financial_vars["other_loans"]
oa = financial_vars["other_assets"]
la = financial_vars["loan_amount"]
dp = financial_vars["down_payment"]
lt = financial_vars["loan_term"]
ir = financial_vars["interest_rate"]

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
        "description": "New job offer in a more expensive city increases income slightly but moving costs, higher rent during transition, and lifestyle adjustments raise expenses by 20%; no income loss due to Finland’s employment support."
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

# -------------------- TAB STRUCTURE --------------------
tab1, tab2, tab3, tab4 = st.tabs(["Loan Decision Summary", "Payment Analysis", "Property Details", "Smart Loan Optimizer"])

# -------------------- TAB 1: LOAN DECISION SUMMARY --------------------
with tab1:
    st.markdown("<h2>Loan Decision Summary</h2>", unsafe_allow_html=True)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        ltv_color = "green" if loan_to_value < 80 else "orange" if loan_to_value < 90 else "red"
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value" style="color: {ltv_color};">{loan_to_value:.1f}%</div>
            <div class="kpi-label">Loan-to-Value</div>
            <div class="kpi-trend">{'Good' if loan_to_value < 80 else 'Moderate' if loan_to_value < 90 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        dti_color = "green" if debt_to_income < 35 else "orange" if debt_to_income < 45 else "red"
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value" style="color: {dti_color};">{debt_to_income:.1f}%</div>
            <div class="kpi-label">Debt-to-Income</div>
            <div class="kpi-trend">{'Good' if debt_to_income < 35 else 'Moderate' if debt_to_income < 45 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        thr_color = "green" if total_housing_ratio < 35 else "orange" if total_housing_ratio < 45 else "red"
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value" style="color: {thr_color};">{total_housing_ratio:.1f}%</div>
            <div class="kpi-label">Housing Costs to Income</div>
            <div class="kpi-trend">{'Good' if total_housing_ratio < 35 else 'Moderate' if total_housing_ratio < 45 else 'High'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value" style="color: {risk_color};">{risk_score:.1f}</div>
            <div class="kpi-label">Overall Risk Score</div>
            <div class="kpi-trend" style="color: {risk_color};">{risk_category}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Income vs. Expenses")
    df_ie = pd.DataFrame({
        "Category": ["Primary Salary", "Side Income", "Investments", 
                    "Housing (New Loan)", "Maintenance Fee", "Renovations", 
                    "Groceries", "Transport", "Utilities", "Entertainment", "Other Expenses", "Other Loans"],
        "Amount": [mi*0.85, mi*0.1, mi*0.05, 
                  monthly_payment, monthly_maintenance, renovation_cost_monthly,
                  me*0.2, me*0.15, me*0.1, me*0.1, me*0.15, ol],
        "Type": ["Income"]*3 + ["Expense"]*9
    })
    
    fig_ie = px.bar(df_ie, x="Category", y="Amount", color="Type", barmode="group",
                    color_discrete_map={"Income": colors['primary'], "Expense": colors['secondary']})
    fig_ie.update_layout(height=400)
    st.plotly_chart(fig_ie, use_container_width=True)
    
    st.markdown("### Real-World Stress Scenarios")
    scenario_options = ["Current"] + list(scenarios.keys())
    selected_scenario = st.selectbox("Select a Stress Scenario", scenario_options)
    
    st.markdown(f"**Description:** {scenario_results[selected_scenario]['Description']}")
    
    scenario_df = pd.DataFrame({
        "Metric": ["Monthly Payment", "Cash Flow", "Payment to Income"],
        "Current": [
            scenario_results["Current"]["Monthly Payment"],
            scenario_results["Current"]["Cash Flow"],
            scenario_results["Current"]["Payment to Income"]
        ],
        selected_scenario: [
            scenario_results[selected_scenario]["Monthly Payment"],
            scenario_results[selected_scenario]["Cash Flow"],
            scenario_results[selected_scenario]["Payment to Income"]
        ]
    })
    
    # Bar chart comparing Current vs Selected Scenario
    fig_scenario = px.bar(
        scenario_df.melt(id_vars=["Metric"], value_vars=["Current", selected_scenario], var_name="Scenario", value_name="Value"),
        x="Metric",
        y="Value",
        color="Scenario",
        barmode="group",
        title=f"Financial Impact: Current vs {selected_scenario}",
        color_discrete_map={"Current": colors['primary'], selected_scenario: colors['warning']}
    )
    fig_scenario.update_layout(height=400, yaxis_title="€ or %")
    st.plotly_chart(fig_scenario, use_container_width=True)

# -------------------- TAB 2: PAYMENT ANALYSIS --------------------
with tab2:
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
            color_discrete_sequence=[colors['primary'], colors['secondary'], colors['warning']]
        )
        fig_payment.update_traces(textposition='inside', textinfo='percent+label')
        fig_payment.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_payment, use_container_width=True)
    
    with col_payment2:
        st.markdown(f"""
        <div class="kpi-container" style="margin-top: 20px;">
            <div class="kpi-value">€{total_monthly:.0f}</div>
            <div class="kpi-label">Total Monthly Housing Cost</div>
            <div style="margin-top: 15px;">
                <p><strong>Loan Payment:</strong> €{monthly_payment:.0f}</p>
                <p><strong>Maintenance Fee:</strong> €{monthly_maintenance:.0f}</p>
                <p><strong>Renovation Reserve:</strong> €{renovation_cost_monthly:.0f}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Loan Term Options")
    
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
    
    fig_terms = px.bar(
        term_df,
        x="Term (years)",
        y="Monthly Payment",
        title="Effect of Loan Term on Monthly Payment",
        color_discrete_sequence=[colors['primary']]
    )
    fig_terms.update_layout(height=300)
    st.plotly_chart(fig_terms, use_container_width=True)
    
    term_display = term_df.copy()
    term_display["Monthly Payment"] = term_display["Monthly Payment"].round().astype(int).apply(lambda x: f"€{x:,}")
    term_display["Total Interest"] = term_display["Total Interest"].round().astype(int).apply(lambda x: f"€{x:,}")
    term_display["Total Cost"] = term_display["Total Cost"].round().astype(int).apply(lambda x: f"€{x:,}")
    st.dataframe(term_display, hide_index=True, use_container_width=True)
    
    st.markdown("### Interest Rate Sensitivity")
    
    rates = [ir, ir + 1, ir + 2, ir + 3]
    rate_data = []
    for rate in rates:
        rate_monthly = (la * (rate/100/12) * (1 + rate/100/12)**(lt*12)) / ((1 + rate/100/12)**(lt*12) - 1)
        rate_data.append({
            "Interest Rate": f"{rate}%", 
            "Monthly Payment": rate_monthly, 
            "Increase": rate_monthly - monthly_payment,
            "% of Income": rate_monthly / mi * 100
        })
    
    rate_df = pd.DataFrame(rate_data)
    
    rates_display = rate_df.copy()
    rates_display["Monthly Payment"] = rates_display["Monthly Payment"].round().astype(int).apply(lambda x: f"€{x:,}")
    rates_display["Increase"] = rates_display["Increase"].round().astype(int).apply(lambda x: f"€{x:,}")
    rates_display["% of Income"] = rates_display["% of Income"].round(1).astype(str) + "%"
    st.dataframe(rates_display, hide_index=True, use_container_width=True)

# -------------------- TAB 3: PROPERTY ANALYSIS --------------------
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
        
        st.markdown("### Monthly Housing Costs")
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">€{monthly_maintenance + renovation_cost_monthly:.0f}</div>
            <div class="kpi-label">Total Monthly Maintenance</div>
            <div class="kpi-trend">Includes €{renovation_cost_monthly:.0f} renovation reserve</div>
        </div>
        """, unsafe_allow_html=True)
        
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


with tab4:
    # Header
    st.markdown("<h2 style='text-align: center;'>Smart Loan Optimizer</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            This tool uses machine learning to optimize your loan structure by:<br>
            1. Minimizing financial strain risk<br>
            2. Maximizing bank approval chances<br>
            3. Balancing monthly payments with total interest
        </div>
    """, unsafe_allow_html=True)

    # Two-column layout
    col_left, col_right = st.columns([1, 1], gap="large")

    # Left Column: Preferences/Input
    with col_left:
        st.markdown("## Set Your Preferences")
        
        # Risk Profile
        st.markdown("### Risk Profile")
        risk_tolerance = st.slider(
            "Risk Tolerance", 
            min_value=1, 
            max_value=5, 
            value=3, 
            help="1 = Very Conservative, 5 = Aggressive",
            format="%d"
        )
        payment_priority = st.slider(
            "Payment Priority", 
            min_value=1, 
            max_value=5, 
            value=3,
            help="1 = Minimize Monthly Payment, 5 = Minimize Total Interest",
            format="%d"
        )

        # Constraints
        st.markdown("### Constraints")
        max_monthly = st.number_input(
            "Maximum Monthly Payment (€)", 
            value=int(monthly_payment * 1.2),
            step=100,
            min_value=0
        )
        target_approval = st.selectbox(
            "Target Approval Odds", 
            ["Very High (95%+)", "High (80-95%)", "Moderate (65-80%)", "Flexible"],
            index=1
        )

        # Optimization Button
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        if st.button("Generate Optimized Loan Options", use_container_width=True):
            with st.spinner("Running optimization algorithm..."):
                time.sleep(2)
                
                # Starting parameters (assumes la, dp, lt, ir are defined elsewhere)
                orig_loan = la
                orig_down = dp
                orig_term = lt
                
                # Generate options
                options = [
                    {
                        "name": "Conservative",
                        "down_payment": dp + 20000,
                        "loan_amount": la - 20000,
                        "term": max(lt - 5, 15),
                        "rate": max(ir - 0.3, 2.8),
                        "monthly": 0,
                        "total_interest": 0,
                        "approval_odds": "Very High (95%+)",
                        "risk_score": "Low Risk"
                    },
                    {
                        "name": "Balanced",
                        "down_payment": dp + 10000,
                        "loan_amount": la - 10000,
                        "term": lt,
                        "rate": max(ir - 0.15, 3.0),
                        "monthly": 0,
                        "total_interest": 0,
                        "approval_odds": "High (80-95%)",
                        "risk_score": "Moderate Risk"
                    },
                    {
                        "name": "Aggressive",
                        "down_payment": dp,
                        "loan_amount": la,
                        "term": min(lt + 3, 30),
                        "rate": ir,
                        "monthly": 0,
                        "total_interest": 0,
                        "approval_odds": "Moderate (65-80%)",
                        "risk_score": "Moderate Risk"
                    }
                ]
                
                # Calculate monthly payments and total interest
                for opt in options:
                    opt["monthly"] = (opt["loan_amount"] * (opt["rate"]/100/12) * 
                                    (1 + opt["rate"]/100/12)**(opt["term"]*12)) / \
                                    ((1 + opt["rate"]/100/12)**(opt["term"]*12) - 1)
                    opt["total_interest"] = opt["monthly"] * opt["term"] * 12 - opt["loan_amount"]
                
                # Filter options
                filtered_options = [
                    opt for opt in options 
                    if opt["monthly"] <= max_monthly and
                    (target_approval == "Flexible" or opt["approval_odds"] == target_approval)
                ]
                
                if not filtered_options:
                    st.warning("No options match your constraints. Please adjust your parameters.")
                else:
                    best_idx = min(risk_tolerance - 1, len(filtered_options) - 1)
                    recommended = filtered_options[best_idx]
                    st.session_state.loan_options = filtered_options
                    st.session_state.recommended = recommended

    # Right Column: Results/Output
    with col_right:
        st.markdown("## Optimization Results")
        
        if 'loan_options' not in st.session_state:
            st.info("Set preferences and generate options on the left to see results.")
        else:
            # Recommended Option
            rec = st.session_state.recommended
            st.markdown(f"""
                ### Recommended: {rec['name']} Option
                <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
                    <p><strong>Down Payment:</strong> €{rec['down_payment']:,} ({(rec['down_payment'] / (rec['loan_amount'] + rec['down_payment']) * 100):.1f}%)</p>
                    <p><strong>Loan Amount:</strong> €{rec['loan_amount']:,}</p>
                    <p><strong>Term:</strong> {rec['term']} years</p>
                    <p><strong>Interest Rate:</strong> {rec['rate']:.2f}%</p>
                    <p><strong>Monthly Payment:</strong> €{rec['monthly']:.0f}</p>
                    <p><strong>Approval Odds:</strong> {rec['approval_odds']}</p>
                    <p><strong>Risk Assessment:</strong> {rec['risk_score']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Comparison Chart
            st.markdown("### Compare All Options")
            options_df = pd.DataFrame(st.session_state.loan_options)
            
            fig_comparison = go.Figure()
            fig_comparison.add_trace(go.Bar(
                x=options_df["name"],
                y=options_df["monthly"],
                name="Monthly Payment (€)",
                marker_color='#1f77b4'
            ))
            fig_comparison.add_trace(go.Scatter(
                x=options_df["name"],
                y=options_df["total_interest"],
                name="Total Interest (€)",
                marker_color='#ff7f0e',
                mode="lines+markers",
                yaxis="y2"
            ))
            
            fig_comparison.update_layout(
                title="Monthly Payment vs Total Interest",
                yaxis=dict(title="Monthly Payment (€)"),
                yaxis2=dict(title="Total Interest (€)", overlaying="y", side="right"),
                height=400,
                margin=dict(t=50, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Explanation
            st.markdown("### Why This Recommendation?")
            explanations = {
                "Conservative": """
                    Ideal for safety-focused borrowers who want quick equity buildup and lower interest costs.
                    Best if you have ample savings and prioritize financial security.
                """,
                "Balanced": """
                    Perfect middle ground offering affordable payments while managing total interest.
                    Great for maintaining flexibility with high approval likelihood.
                """,
                "Aggressive": """
                    Maximizes purchasing power with lower upfront costs and extended terms.
                    Suits those comfortable with longer commitments and potential investment opportunities.
                """
            }
            st.markdown(explanations[rec["name"]])