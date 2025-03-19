import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Housing Loan Risk Assessment",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
# Enhanced CSS for a more professional dashboard
st.markdown("""
<style>
    /* Import Google fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap');

    /* Base styling for dark theme */
    .stApp, body, li, td {
        font-family: 'DM Sans', sans-serif;
        background-color: #1F2937;
        color: #D1D5DB;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;  /* Softer blue */
        margin-bottom: 1.5rem;
        padding-bottom: 10px;
        border-bottom: 3px solid #3B82F6;
    }

    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FFFFFF;  /* Lighter teal */
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
        padding-left: 10px;
    }

    /* Risk indicators */
    .risk-high {
        color: #F87171;
        font-weight: bold;
        background-color: rgba(248, 113, 113, 0.2);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .risk-medium {
        color: #FBBF24;
        font-weight: bold;
        background-color: rgba(251, 191, 36, 0.2);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .risk-low {
        color: #34D399;
        font-weight: bold;
        background-color: rgba(52, 211, 153, 0.2);
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* Info boxes */
    .info-box {
        background-color: #374151;
        padding: 1.25rem;
        border-radius: 0.75rem;
        border-left: 5px solid #3B82F6;
        color: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }

    /* Section dividers */
    .section-divider {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        border-top: 1px solid #4B5563;
    }

    /* Tables */
    table {
        width: 100%;
        color: #D1D5DB;
        border-collapse: separate;
        border-spacing: 0 5px;
    }
    table td {
        padding: 10px;
    }

    /* Payment table */
    .payment-table {
        margin-top: 10px;
    }
    .payment-table tr:hover {
        background-color: rgba(59, 130, 246, 0.1);
    }

    /* Value badges */
    .value-badge {
        background-color: #4B5563;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        color: #D1D5DB;
    }

    /* Improve sliders */
    .stSlider > div {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }

    /* Improve select boxes */
    .stSelectbox {
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }

    /* Improve buttons */
    .stButton > button {
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        background-color: #3B82F6;
        color: #FFFFFF;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563EB;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #1F2937;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 4px 4px 0 0;
        color: #D1D5DB;
    }
    .stTabs [aria-selected="true"] {
        background-color: #374151;
        border-bottom: 2px solid #3B82F6;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def calculate_monthly_payment(principal, annual_interest_rate, term_years):
    """Calculate monthly mortgage payment"""
    if annual_interest_rate == 0:
        return principal / (term_years * 12)
    
    monthly_rate = annual_interest_rate / 100 / 12
    num_payments = term_years * 12
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    return monthly_payment

def generate_amortization_schedule(principal, annual_interest_rate, term_years):
    """Generate amortization schedule"""
    monthly_rate = annual_interest_rate / 100 / 12
    num_payments = term_years * 12
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, term_years)
    
    schedule = []
    remaining_balance = principal
    
    for payment_num in range(1, num_payments + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        schedule.append({
            'Payment Number': payment_num,
            'Payment Amount': monthly_payment,
            'Principal Payment': principal_payment,
            'Interest Payment': interest_payment,
            'Remaining Balance': max(0, remaining_balance)
        })
    
    return pd.DataFrame(schedule)

def calculate_dti_ratio(monthly_income, monthly_debt_payments, proposed_loan_payment):
    """Calculate Debt-to-Income ratio"""
    total_monthly_debt = monthly_debt_payments + proposed_loan_payment
    dti_ratio = (total_monthly_debt / monthly_income) * 100
    return dti_ratio

def calculate_ltv_ratio(loan_amount, property_value):
    """Calculate Loan-to-Value ratio"""
    ltv_ratio = (loan_amount / property_value) * 100
    return ltv_ratio

def generate_market_trends():
    """Generate simulated market trends data"""
    dates = pd.date_range(end=datetime.now(), periods=60, freq='M')
    
    # Generate housing price index with seasonal patterns and trend
    base = np.linspace(100, 120, 60)
    seasonal = 5 * np.sin(np.linspace(0, 6 * np.pi, 60))
    noise = np.random.normal(0, 1, 60)
    housing_price_index = base + seasonal + noise
    
    # Generate interest rates with some correlation to housing prices but with their own trend
    interest_trend = np.linspace(3.5, 5.2, 60) + np.random.normal(0, 0.3, 60)
    interest_rates = np.clip(interest_trend, 2.8, 6.5)
    
    # Generate inflation data
    inflation = np.clip(np.linspace(2.5, 3.8, 60) + np.random.normal(0, 0.5, 60), 1.5, 5.5)
    
    return pd.DataFrame({
        'Date': dates,
        'Housing Price Index': housing_price_index,
        'Average Interest Rate': interest_rates,
        'Inflation Rate': inflation
    })

def generate_stress_test_scenarios(base_interest_rate, base_property_value, base_income):
    """Generate stress test scenarios"""
    scenarios = []
    
    # Scenario 1: Interest rate increases
    scenarios.append({
        'Scenario': 'Interest Rate +1%',
        'Interest Rate': base_interest_rate + 1,
        'Property Value': base_property_value,
        'Monthly Income': base_income,
        'Impact': 'High'
    })
    
    scenarios.append({
        'Scenario': 'Interest Rate +2%',
        'Interest Rate': base_interest_rate + 2,
        'Property Value': base_property_value,
        'Monthly Income': base_income,
        'Impact': 'High'
    })
    
    # Scenario 2: Property value decrease
    scenarios.append({
        'Scenario': 'Property Value -10%',
        'Interest Rate': base_interest_rate,
        'Property Value': base_property_value * 0.9,
        'Monthly Income': base_income,
        'Impact': 'Medium'
    })
    
    scenarios.append({
        'Scenario': 'Property Value -20%',
        'Interest Rate': base_interest_rate,
        'Property Value': base_property_value * 0.8,
        'Monthly Income': base_income,
        'Impact': 'High'
    })
    
    # Scenario 3: Income decrease
    scenarios.append({
        'Scenario': 'Income -15%',
        'Interest Rate': base_interest_rate,
        'Property Value': base_property_value,
        'Monthly Income': base_income * 0.85,
        'Impact': 'Medium'
    })
    
    # Scenario 4: Combined scenarios
    scenarios.append({
        'Scenario': 'Interest +1%, Property -10%',
        'Interest Rate': base_interest_rate + 1,
        'Property Value': base_property_value * 0.9,
        'Monthly Income': base_income,
        'Impact': 'High'
    })
    
    scenarios.append({
        'Scenario': 'Interest +1%, Income -15%',
        'Interest Rate': base_interest_rate + 1,
        'Property Value': base_property_value,
        'Monthly Income': base_income * 0.85,
        'Impact': 'High'
    })
    
    return pd.DataFrame(scenarios)

def generate_neighborhood_data(property_zipcode):
    """Generate neighborhood data based on zipcode"""
    # In a real application, this would pull from an API or database
    np.random.seed(int(property_zipcode) % 100)  # Use zipcode to seed random generator for consistent results
    
    years = list(range(datetime.now().year - 5, datetime.now().year + 1))
    appreciation_rates = np.clip(np.random.normal(3.5, 2, len(years)), -2, 8)
    
    neighborhood_data = pd.DataFrame({
        'Year': years,
        'Appreciation Rate (%)': appreciation_rates,
        'Median Sale Price': np.linspace(250000, 320000, len(years)) * (1 + np.random.normal(0, 0.05, len(years))),
        'Days on Market': np.clip(np.random.normal(45, 15, len(years)), 10, 90),
        'Sales Volume': np.clip(np.random.normal(120, 30, len(years)), 50, 200)
    })
    
    return neighborhood_data

def generate_risk_score(principal, interest_rate, term, property_value, monthly_income, monthly_debt):
    """Generate composite risk score from 0-100"""
    # Calculate key risk metrics
    dti = calculate_dti_ratio(monthly_income, monthly_debt, 
                               calculate_monthly_payment(principal, interest_rate, term))
    ltv = calculate_ltv_ratio(principal, property_value)
    
    # Assign points to different risk factors (lower is better)
    dti_points = np.interp(dti, [20, 28, 36, 43, 50], [0, 10, 20, 30, 40])
    ltv_points = np.interp(ltv, [60, 75, 80, 90, 95], [0, 5, 10, 20, 30])
    
    # Interest rate risk (compared to current average)
    rate_risk = np.interp(interest_rate, [3.5, 4.0, 4.5, 5.0, 6.0], [0, 5, 10, 15, 20])
    
    # Term risk (longer terms have slightly higher risk)
    term_risk = np.interp(term, [10, 15, 20, 30], [0, 3, 5, 10])
    
    # Total risk score (0-100, lower is better)
    risk_score = dti_points + ltv_points + rate_risk + term_risk
    
    return max(0, min(100, risk_score))

def get_risk_category(score):
    """Convert numeric risk score to category"""
    if score < 25:
        return "Low"
    elif score < 50:
        return "Medium-Low"
    elif score < 75:
        return "Medium-High"
    else:
        return "High"

def load_client_data():
    """
    In a real scenario, this would load client data from an external source.
    For this demo, we'll simulate this with some sample data.
    """
    return {
        'name': 'Matti Meikäläinen',
        'age': 35,
        'monthly_income': 6500,
        'monthly_debt': 1800,
        'employment_years': 8,
        'property_zipcode': '000220',
        'property_value': 450000,
        'desired_loan_amount': 360000,
        'desired_term_years': 30,
        'initial_interest_rate': 4.5
    }

# Main application
def main():
    # Sidebar - Client Info and Loan Parameters
    st.sidebar.markdown('<div class="main-header">Client Information</div>', unsafe_allow_html=True)
    
    # Load initial client data (in real scenario, would be uploaded or fetched)
    client_data = load_client_data()
    
    # Client info section with collapsible details
    with st.sidebar.expander("Client Details", expanded=True):
        client_name = st.text_input("Client Name", value=client_data['name'])
        client_age = st.number_input("Age", min_value=18, max_value=100, value=client_data['age'])
        employment_years = st.number_input("Years of Employment", min_value=0, max_value=50, value=client_data['employment_years'], step=1)
        monthly_income = st.number_input("Monthly Income (€)", min_value=0, value=client_data['monthly_income'], step=100)
        monthly_debt = st.number_input("Current Monthly Debt (€)", min_value=0, value=client_data['monthly_debt'], step=100)
    
    # Property info section
    with st.sidebar.expander("Property Details", expanded=True):
        property_zipcode = st.text_input("Property Zipcode", value=client_data['property_zipcode'])
        property_value = st.number_input("Property Value (€)", min_value=50000, value=client_data['property_value'], step=10000)
    
    # Loan parameters section
    st.sidebar.markdown('<div class="sub-header">Loan Parameters</div>', unsafe_allow_html=True)
    loan_amount = st.sidebar.number_input("Loan Amount (€)", min_value=10000, max_value=10000000, value=client_data['desired_loan_amount'], step=10000)
    loan_term = st.sidebar.selectbox("Loan Term (Years)", [10, 15, 20, 30], index=3)
    interest_rate = st.sidebar.slider("Interest Rate (%)", min_value=2.0, max_value=8.0, value=client_data['initial_interest_rate'], step=0.125)
    
    # Calculate key metrics
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term)
    dti_ratio = calculate_dti_ratio(monthly_income, monthly_debt, monthly_payment)
    ltv_ratio = calculate_ltv_ratio(loan_amount, property_value)
    risk_score = generate_risk_score(loan_amount, interest_rate, loan_term, 
                                     property_value, monthly_income, monthly_debt)
    risk_category = get_risk_category(risk_score)
    
    # Main content area
    st.markdown('<div class="main-header">Housing Loan Risk Assessment Dashboard</div>', unsafe_allow_html=True)
    
    # Overview section - Key metrics
    st.markdown('<div class="sub-header">Key Risk Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Payment", f"€{monthly_payment:.2f}")
    with col2:
        dtI_color = "normal" if dti_ratio < 36 else "off"
        st.metric("Debt-to-Income Ratio", f"{dti_ratio:.1f}%", delta_color=dtI_color)
    with col3:
        ltv_color = "normal" if ltv_ratio < 80 else "off"
        st.metric("Loan-to-Value Ratio", f"{ltv_ratio:.1f}%", delta_color=ltv_color)
    with col4:
        risk_color = "green" if risk_score < 25 else "orange" if risk_score < 50 else "red"
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {'#064E3B' if risk_score < 25 else '#78350F' if risk_score < 50 else '#7F1D1D'};">
            <h4 style="margin:0; color: #D1D5DB;">Risk Score</h4>
            <div style="font-size: 1.8rem; font-weight: bold; color: {'#34D399' if risk_score < 25 else '#FBBF24' if risk_score < 50 else '#F87171'};">
                {risk_score:.1f} - {risk_category}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Risk assessment explanation
    st.markdown("""
    <div class="info-box">
        <h4>Risk Assessment Explanation</h4>
        <p>The risk score is calculated based on multiple factors including debt-to-income ratio, 
        loan-to-value ratio, and loan terms. A lower score indicates lower risk.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Loan Analysis", "Payment Breakdown", "Market Trends", "Stress Test", "Neighborhood Analysis"])
    
    # Tab 1: Loan Analysis
    with tab1:
        st.markdown('<div class="sub-header">Loan Analysis</div>', unsafe_allow_html=True)
        
        # Amortization Schedule
        amortization_df = generate_amortization_schedule(loan_amount, interest_rate, loan_term)
        
        # Chart for Principal vs Interest over time
        fig = px.area(
            amortization_df, 
            x='Payment Number', 
            y=['Principal Payment', 'Interest Payment'],
            title='Principal vs Interest Payments Over Time',
            labels={'value': 'Amount (€)', 'Payment Number': 'Payment Number', 'variable': 'Payment Type'},
            color_discrete_map={
                'Principal Payment': '#3B82F6',  # Blue (matches Historical Rate)
                'Interest Payment': '#FBBF24'    # Orange (matches Rising Scenario/Selected Rate)
            }
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='#1F2937',  # Matches forecast background
            plot_bgcolor='#1F2937',
            font=dict(color='#D1D5DB'),  # Matches forecast text
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='#D1D5DB')
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Total Interest Paid
        total_interest = amortization_df['Interest Payment'].sum()
        total_payments = amortization_df['Payment Amount'].sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=['Principal', 'Interest'],
                values=[loan_amount, total_interest],
                hole=.4,
                marker_colors=['#3B82F6', '#FBBF24'],  # Blue for Principal, Orange for Interest
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(color='#D1D5DB', size=14)
            )])
            fig.update_layout(
                title_text="Total Payment Breakdown",
                height=400,
                paper_bgcolor='#1F2937',  # Matches forecast background
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB'),  # Matches forecast text
                showlegend=False,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <div class="info-box">
                <b>Total loan cost:</b> €{total_payments:.2f}<br>
                <b>Principal amount:</b> €{loan_amount:.2f}<br>
                <b>Total interest paid:</b> €{total_interest:.2f}
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            # Balance Reduction Over Time
            fig = px.line(
                amortization_df, 
                x='Payment Number', 
                y='Remaining Balance',
                title='Remaining Balance Over Time',
                labels={'Remaining Balance': 'Balance (€)', 'Payment Number': 'Payment Number'},
                line_shape='linear',
                color_discrete_sequence=['#3B82F6']  # Blue (matches Historical Rate)
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='#1F2937',  # Matches forecast background
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB'),  # Matches forecast text
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='#D1D5DB')
                )
            )
            fig.update_traces(line=dict(width=3))  # Matches width of Historical Rate
            st.plotly_chart(fig, use_container_width=True)
        
        # Amortization Table (expandable)
        with st.expander("View Full Amortization Schedule"):
            # Format the DataFrame for better display
            display_df = amortization_df.copy()
            for col in ['Payment Amount', 'Principal Payment', 'Interest Payment', 'Remaining Balance']:
                display_df[col] = display_df[col].map('€{:,.2f}'.format)
            
            # Display in chunks for better performance
            page_size = 12
            total_payments = len(display_df)
            max_pages = (total_payments + page_size - 1) // page_size
            
            page = st.number_input("Page", min_value=1, max_value=max_pages, value=1)
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_payments)
            
            st.dataframe(display_df.iloc[start_idx:end_idx], use_container_width=True)
    
    with tab2:
        st.markdown('<div class="sub-header">Payment Breakdown</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create a donut chart showing monthly payment breakdown
            monthly_principal = amortization_df.iloc[0]['Principal Payment']
            monthly_interest = amortization_df.iloc[0]['Interest Payment']
            
            # Estimate property tax and insurance
            estimated_property_tax = property_value * 0.01 / 12  # Rough estimate: 1% annually
            estimated_insurance = property_value * 0.0035 / 12   # Rough estimate: 0.35% annually
            
            # Calculate total monthly housing cost
            total_housing_cost = monthly_payment + estimated_property_tax + estimated_insurance
            
            # Create figure with consistent color scheme
            labels = ['Principal', 'Interest', 'Property Tax (est.)', 'Insurance (est.)']
            values = [monthly_principal, monthly_interest, estimated_property_tax, estimated_insurance]
            
            # Using colors consistent with the rest of the dashboard
            colors = ['#3B82F6', '#FBBF24', '#34D399', '#A78BFA']  # Blue, Orange, Green, Purple
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.4,
                marker_colors=colors,
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(color='#D1D5DB', size=14)
            )])
            fig.update_layout(
                title_text="Monthly Payment Breakdown",
                height=500,  # Increased size from 400 to 500
                paper_bgcolor='#1F2937',
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB'),
                showlegend=False,  # Removed legend since labels are now outside
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Monthly Payment Details section with better styling and removed background colors
            st.markdown('<div class="info-box"><h3>Monthly Payment Details</h3>', unsafe_allow_html=True)

            # Create styled table for payment details without colored backgrounds
            payment_details_html = f"""
            <table class="payment-table">
                <tr>
                    <td style="color: #D1D5DB; padding: 8px;">Principal & Interest:</td>
                    <td style="text-align:right; font-weight:bold; color:#3B82F6">€{monthly_payment:.2f}</td>
                </tr>
                <tr>
                    <td style="color: #D1D5DB; padding: 8px;">Principal:</td>
                    <td style="text-align:right; color:#3B82F6">€{monthly_principal:.2f}</td>
                </tr>
                <tr>
                    <td style="color: #D1D5DB; padding: 8px;">Interest:</td>
                    <td style="text-align:right; color:#FBBF24">€{monthly_interest:.2f}</td>
                </tr>
                <tr>
                    <td style="color: #D1D5DB; padding: 8px;">Est. Property Tax:</td>
                    <td style="text-align:right; color:#34D399">€{estimated_property_tax:.2f}</td>
                </tr>
                <tr>
                    <td style="color: #D1D5DB; padding: 8px;">Est. Insurance:</td>
                    <td style="text-align:right; color:#A78BFA">€{estimated_insurance:.2f}</td>
                </tr>
                <tr style="border-top:1px solid #D1D5DB; margin-top:5px; padding-top:5px;">
                    <td style="font-weight:bold; padding-top:12px; color: #D1D5DB; padding: 8px;">Total Monthly Payment:</td>
                    <td style="text-align:right; font-weight:bold; color:#3B82F6; padding-top:12px;">€{total_housing_cost:.2f}</td>
                </tr>
            </table>
            </div>
            """
            
            st.markdown(payment_details_html, unsafe_allow_html=True)
        

        
        # Calculate affordability metrics
        housing_percent = (total_housing_cost/monthly_income*100)
        
        # Determine risk levels and corresponding CSS classes
        housing_risk_class = "risk-low" if housing_percent < 28 else "risk-medium" if housing_percent < 36 else "risk-high"
        dti_risk_class = "risk-low" if dti_ratio < 36 else "risk-medium" if dti_ratio < 43 else "risk-high"
        
        # Create the affordability analysis content
        affordability_html = f"""
        <p style="color: #D1D5DB;">Housing cost is <b>€{total_housing_cost:.2f}</b>, which is <span class="{housing_risk_class}">{housing_percent:.1f}%</span> of your monthly income.</p>
        <p style="margin-top:-5px; font-style:italic; font-size:0.9em; color: #9CA3AF;">Recommended: Housing costs should be below 28% of income.</p>
        <p style="margin-top:15px; color: #D1D5DB;">Your DTI ratio including this loan would be <span class="{dti_risk_class}">{dti_ratio:.1f}%</span>.</p>
        <p style="margin-top:-5px; font-style:italic; font-size:0.9em; color: #9CA3AF;">Recommended: Total DTI should be below 36% for optimal approval chances.</p>
        """
        st.markdown(f'<div class="info-box" style="margin-top:15px;"><h3>Affordability Analysis</h3>{affordability_html}</div>', unsafe_allow_html=True)
        
        st.markdown(affordability_html, unsafe_allow_html=True)
    
        # Affordability visualization
        st.markdown('<div class="sub-header">Income Allocation</div>', unsafe_allow_html=True)
        
        # Calculate income allocation
        housing_payment = total_housing_cost
        other_debt = monthly_debt
        remaining_income = monthly_income - housing_payment - other_debt
            
        # Create a horizontal bar chart
        income_allocation = pd.DataFrame({
            'Category': ['Housing Payment', 'Other Debt', 'Remaining Income'],
            'Amount': [housing_payment, other_debt, remaining_income],
            'Percentage': [housing_payment/monthly_income*100, other_debt/monthly_income*100, remaining_income/monthly_income*100]
        })
        
        fig = px.bar(income_allocation, y='Category', x='Amount', orientation='h',
                    text='Percentage', color='Category',
                    color_discrete_map={
                        'Housing Payment': '#3B82F6',
                        'Other Debt': '#FBBF24',
                        'Remaining Income': '#34D399'
                    },
                    title='Monthly Income Allocation',
                    height=300)
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
        fig.update_layout(
            uniformtext_minsize=10, uniformtext_mode='hide',
            xaxis_title="Amount (€)", yaxis_title="",
            paper_bgcolor='#1F2937',
            plot_bgcolor='#1F2937',
            font=dict(color='#D1D5DB'),
            legend=dict(font=dict(color='#D1D5DB'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Interactive What-If Analysis
        st.markdown('<div class="sub-header">Payment Calculator: What-If Scenarios</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            what_if_amount = st.slider("Adjust Loan Amount (€)", min_value=int(loan_amount*0.5), max_value=int(loan_amount*1.5), value=int(loan_amount), step=5000)
        
        with col2:
            what_if_rate = st.slider("Adjust Interest Rate (%)", min_value=max(interest_rate-2, 2.0), max_value=min(interest_rate+3, 8.0), value=interest_rate, step=0.125)
        
        with col3:
            what_if_term = st.selectbox("Adjust Loan Term (Years)", [10, 15, 20, 30], index=[10, 15, 20, 30].index(loan_term))
        
        # Calculate what-if scenario
        what_if_payment = calculate_monthly_payment(what_if_amount, what_if_rate, what_if_term)
        payment_difference = what_if_payment - monthly_payment
        
        st.markdown(f"""
            <div class="info-box">
                <h4 style="color: #D1D5DB;">Payment Comparison</h4>
                <table style="width:100%; background: none;">
                    <tr style="background: none;">
                        <td style="color: #D1D5DB; background: none;">Current Payment:</td>
                        <td style="text-align:right; background: none;"><b>€{monthly_payment:.2f}</b></td>
                    </tr>
                    <tr style="background: none;">
                        <td style="color: #D1D5DB; background: none;">Adjusted Payment:</td>
                        <td style="text-align:right; background: none;"><b>€{what_if_payment:.2f}</b></td>
                    </tr>
                    <tr style="background: none;">
                        <td style="color: #D1D5DB; background: none;">Difference:</td>
                        <td style="text-align:right; background: none;">
                            <b style="color:{'#F87171' if payment_difference > 0 else '#34D399'}">
                                €{abs(payment_difference):.2f} {'higher' if payment_difference > 0 else 'lower'}
                            </b>
                        </td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

    
    # Tab 3: Market Trends
    with tab3:
        st.markdown('<div class="sub-header">Market Trends Analysis</div>', unsafe_allow_html=True)
        
        # Generate market data
        market_data = generate_market_trends()
        
        # Create market trends visualization
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            subplot_titles=("Housing Price Index", "Interest Rates and Inflation"),
                            vertical_spacing=0.1, 
                            specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=market_data['Date'], y=market_data['Housing Price Index'], name="Housing Price Index", line=dict(color="#3B82F6")), row=1, col=1)
        fig.add_trace(go.Scatter(x=market_data['Date'], y=market_data['Average Interest Rate'], name="Avg. Interest Rate (%)", line=dict(color="#FBBF24")), row=2, col=1)
        fig.add_trace(go.Scatter(x=market_data['Date'], y=market_data['Inflation Rate'], name="Inflation Rate (%)", line=dict(color="#F87171"), opacity=0.7), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=[market_data['Date'].iloc[-1]], y=[interest_rate], mode="markers", name="Selected Rate", marker=dict(color="#FBBF24", size=10, symbol="star")), row=2, col=1)
        fig.update_layout(
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#D1D5DB')),
            paper_bgcolor='#1F2937',
            plot_bgcolor='#1F2937',
            font=dict(color='#D1D5DB')
        )
        fig.update_yaxes(title_text="Index Value", row=1, col=1)
        fig.update_yaxes(title_text="Rate (%)", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)
                
        # Market commentary
        latest_house_index = market_data['Housing Price Index'].iloc[-1]
        latest_interest = market_data['Average Interest Rate'].iloc[-1]
        latest_inflation = market_data['Inflation Rate'].iloc[-1]
        
        six_month_change_housing = (market_data['Housing Price Index'].iloc[-1] / market_data['Housing Price Index'].iloc[-7] - 1) * 100
        six_month_change_interest = market_data['Average Interest Rate'].iloc[-1] - market_data['Average Interest Rate'].iloc[-7]

        housing_trend = "increased" if six_month_change_housing > 0 else "decreased"
        interest_trend = "increased" if six_month_change_interest > 0 else "decreased"
        rate_comparison = "above" if interest_rate > latest_interest else "below"
        
        st.markdown(f"""
        <p>Over the past 6 months, housing prices have <b>{housing_trend} by {abs(six_month_change_housing):.1f}%</b>. 
        During the same period, interest rates have <b>{interest_trend} by {abs(six_month_change_interest):.2f} percentage points</b>.</p>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <p>Your selected interest rate of <b>{interest_rate:.2f}%</b> is {rate_comparison} the current market average of <b>{latest_interest:.2f}%</b>.</p>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <p>With current inflation at <b>{latest_inflation:.1f}%</b>, this means the real (inflation-adjusted) interest rate is approximately <b>{interest_rate - latest_inflation:.1f}%</b>.</p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="info-box"><h4>What This Means For You</h4>', unsafe_allow_html=True)
        # Rate advice

        if six_month_change_interest > 0:
            rate_advice = "Consider locking in your rate soon if you believe interest rates will continue to rise."
        else:
            rate_advice = "You may want to consider a variable rate loan if you believe interest rates will continue to fall."

        st.markdown(f"<p>{rate_advice}</p>", unsafe_allow_html=True)

        # Property value advice
        if six_month_change_housing > 0:
            property_advice = "Property values in your area are appreciating, which may increase your equity position over time."
        else:
            property_advice = "Property values in your area are declining, which may affect your equity position and future refinancing options."

        st.markdown(f"<p>{property_advice}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interest rate forecast
        st.markdown('<div class="sub-header">Interest Rate Forecast</div>', unsafe_allow_html=True)
        
        # Generate forecasted interest rates
        forecast_dates = pd.date_range(start=market_data['Date'].iloc[-1] + pd.Timedelta(days=30), periods=12, freq='M')
        
        # Create three scenarios: steady, rising, falling
        base_rate = market_data['Average Interest Rate'].iloc[-1]
        
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Rising Scenario': [base_rate + i*0.125 for i in range(1, 13)],
            'Steady Scenario': [base_rate + np.random.normal(0, 0.05) for _ in range(12)],
            'Falling Scenario': [max(2.5, base_rate - i*0.1) for i in range(1, 13)]
        })
        
        # Add historical data for context
        historical_df = pd.DataFrame({
            'Date': market_data['Date'][-12:],
            'Historical Rate': market_data['Average Interest Rate'][-12:],
            'Rising Scenario': None,
            'Steady Scenario': None,
            'Falling Scenario': None
        })
        
        # Combine historical and forecast data
        combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
        
        # Create the forecast visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined_df['Date'][:12], y=combined_df['Historical Rate'], name="Historical Rate", line=dict(color="#3B82F6", width=3)))
        fig.add_trace(go.Scatter(x=combined_df['Date'][11:], y=[combined_df['Historical Rate'].iloc[-1]] + combined_df['Rising Scenario'][12:].tolist(), name="Rising Scenario", line=dict(color="#FBBF24", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=combined_df['Date'][11:], y=[combined_df['Historical Rate'].iloc[-1]] + combined_df['Steady Scenario'][12:].tolist(), name="Steady Scenario", line=dict(color="#34D399", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=combined_df['Date'][11:], y=[combined_df['Historical Rate'].iloc[-1]] + combined_df['Falling Scenario'][12:].tolist(), name="Falling Scenario", line=dict(color="#A78BFA", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=[combined_df['Date'].iloc[11]], y=[interest_rate], mode="markers", name="Selected Rate", marker=dict(color="#FBBF24", size=10, symbol="star")))
        fig.update_layout(
            title="Interest Rate Forecast - Next 12 Months",
            xaxis_title="Date",
            yaxis_title="Interest Rate (%)",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#D1D5DB')),
            paper_bgcolor='#1F2937',
            plot_bgcolor='#1F2937',
            font=dict(color='#D1D5DB')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanatory text
        st.markdown("""
            <div class="info-box">
                <h4>Understanding the Forecast</h4>
                <p>The forecast above shows three potential interest rate scenarios over the next 12 months:</p>
                <ul style="background: none; padding-left: 20px;">
                    <li style="background: none;"><b>Rising Scenario:</b> Rates increase by approximately 0.125% per month</li>
                    <li style="background: none;"><b>Steady Scenario:</b> Rates remain relatively stable with minor fluctuations</li>
                    <li style="background: none;"><b>Falling Scenario:</b> Rates decrease by approximately 0.1% per month</li>
                </ul>
                <p>These scenarios are based on historical trends and current market conditions but are not guaranteed predictions.</p>
                <p><b>What this means for your loan:</b> If you're considering an adjustable-rate mortgage, the interest rate forecast provides insight into potential future payment changes.</p>
            </div>
        """, unsafe_allow_html=True)


    
    # Tab 4: Stress Test
    with tab4:
        st.markdown('<div class="sub-header">Financial Stress Test</div>', unsafe_allow_html=True)
        
        # Generate stress test scenarios
        stress_test_df = generate_stress_test_scenarios(interest_rate, property_value, monthly_income)
        
        # Create columns for stress test parameters
        st.markdown("""
        <div class="info-box">
            <h4>What is a Stress Test?</h4>
            <p>A financial stress test helps evaluate how your loan would perform under adverse market conditions or personal financial challenges.</p>
            <p>The scenarios below simulate various potential changes to interest rates, property values, and income to assess the impact on your loan.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate payment impacts
        scenario_results = []
        
        for _, scenario in stress_test_df.iterrows():
            scenario_payment = calculate_monthly_payment(loan_amount, scenario['Interest Rate'], loan_term)
            scenario_dti = calculate_dti_ratio(scenario['Monthly Income'], monthly_debt, scenario_payment)
            scenario_ltv = calculate_ltv_ratio(loan_amount, scenario['Property Value'])
            
            scenario_results.append({
                'Scenario': scenario['Scenario'],
                'Monthly Payment': scenario_payment,
                'Payment Change': scenario_payment - monthly_payment,
                'Payment Change %': (scenario_payment / monthly_payment - 1) * 100,
                'New DTI Ratio': scenario_dti,
                'New LTV Ratio': scenario_ltv,
                'DTI Change': scenario_dti - dti_ratio,
                'LTV Change': scenario_ltv - ltv_ratio,
                'Impact': scenario['Impact']
            })
        
        results_df = pd.DataFrame(scenario_results)
        
        # Display results in a table
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create chart for payment changes
            fig = px.bar(results_df, x='Scenario', y='Payment Change', 
                        title='Impact on Monthly Payment',
                        color='Impact',
                        color_discrete_map={'High': '#F87171', 'Medium': '#FBBF24', 'Low': '#34D399'},
                        labels={'Payment Change': 'Change in Monthly Payment (€)', 'Scenario': 'Scenario'},
                        text='Payment Change %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                height=400,
                paper_bgcolor='#1F2937',
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB'),
                legend=dict(font=dict(color='#D1D5DB'))
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Display detailed results
            st.markdown("""
            <div style="margin-bottom: 15px;">
                <h4>Scenario Details</h4>
                <p>Select a scenario to see detailed impact analysis:</p>
            </div>
            """, unsafe_allow_html=True)
            
            selected_scenario = st.selectbox("Select Scenario", results_df['Scenario'].tolist())
            
            scenario_data = results_df[results_df['Scenario'] == selected_scenario].iloc[0]
            
            impact_color = '#F87171' if scenario_data['Impact'] == 'High' else '#FBBF24' if scenario_data['Impact'] == 'Medium' else '#34D399'
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; border-left: 5px solid {impact_color}; background-color: {'#7F1D1D' if scenario_data['Impact'] == 'High' else '#78350F' if scenario_data['Impact'] == 'Medium' else '#064E3B'};">
                <h4 style="color: {impact_color};">{selected_scenario}</h4>
                <p style="color: #D1D5DB;"><b>Impact Level:</b> {scenario_data['Impact']}</p>
                <p style="color: #D1D5DB;"><b>Monthly Payment:</b> €{scenario_data['Monthly Payment']:.2f} 
                (<span style="color: {'#F87171' if scenario_data['Payment Change'] > 0 else '#34D399'};">
                {'+' if scenario_data['Payment Change'] > 0 else ''}{scenario_data['Payment Change']:.2f} ({scenario_data['Payment Change %']:.1f}%)
                </span>)</p>
                <p style="color: #D1D5DB;"><b>New DTI Ratio:</b> {scenario_data['New DTI Ratio']:.1f}% 
                (<span style="color: {'#F87171' if scenario_data['DTI Change'] > 0 else '#34D399'};">
                {'+' if scenario_data['DTI Change'] > 0 else ''}{scenario_data['DTI Change']:.1f}%
                </span>)</p>
                <p style="color: #D1D5DB;"><b>New LTV Ratio:</b> {scenario_data['New LTV Ratio']:.1f}% 
                (<span style="color: {'#F87171' if scenario_data['LTV Change'] > 0 else '#34D399'};">
                {'+' if scenario_data['LTV Change'] > 0 else ''}{scenario_data['LTV Change']:.1f}%
                </span>)</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="margin-top: 15px; padding: 15px; border-radius: 5px; background-color: #374151;">
                <h4 style="color: #D1D5DB;">Risk Assessment</h4>
                <p style="color: #D1D5DB;">{"<b>High Risk:</b> This scenario would significantly impact your ability to maintain payments and may require substantial financial adjustments." if scenario_data['Impact'] == 'High' else
                "<b>Medium Risk:</b> This scenario would create noticeable pressure on your finances but might be manageable with proper budgeting and planning." if scenario_data['Impact'] == 'Medium' else
                "<b>Low Risk:</b> This scenario would have minimal impact on your financial stability and loan sustainability."}</p>
                <p style="color: #D1D5DB;">{"<b>Recommendation:</b> Consider building a larger emergency fund to handle potential payment increases." if scenario_data['Payment Change'] > 100 else
                "<b>Recommendation:</b> Evaluate if your budget can accommodate the increased payment in this scenario." if scenario_data['Payment Change'] > 0 else
                "<b>Recommendation:</b> This scenario appears manageable based on your current financial profile."}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Emergency Fund Recommendation
        st.markdown('<div class="sub-header">Emergency Fund Analysis</div>', unsafe_allow_html=True)
        
        # Calculate recommended emergency fund
        min_emergency_fund = total_housing_cost * 3
        recommended_emergency_fund = total_housing_cost * 6
        strong_emergency_fund = total_housing_cost * 12
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create an emergency fund gauge
            emergency_fund = st.slider("Your Emergency Fund", min_value=0, max_value=int(strong_emergency_fund * 1.2), value=int(recommended_emergency_fund * 0.8), step=1000)
            
            # Calculate percentage of recommended
            emergency_percentage = (emergency_fund / recommended_emergency_fund) * 100
            
            # Create a gauge visualization
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=emergency_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Emergency Fund Coverage", 'font': {'size': 24, 'color': '#D1D5DB'}},
                delta={'reference': 100, 'increasing': {'color': "#34D399"}, 'decreasing': {'color': "#F87171"}},
                gauge={
                    'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "#D1D5DB"},
                    'bar': {'color': "#3B82F6"},
                    'bgcolor': "#1F2937",
                    'borderwidth': 2,
                    'bordercolor': "#4B5563",
                    'steps': [
                        {'range': [0, 50], 'color': '#7F1D1D'},
                        {'range': [50, 100], 'color': '#78350F'},
                        {'range': [100, 200], 'color': '#064E3B'}
                    ],
                    'threshold': {
                        'line': {'color': "#F87171", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            fig.update_layout(
                height=300,
                paper_bgcolor='#1F2937',
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Show emergency fund recommendations
            st.markdown(f"""
            <div style="margin-top: 15px; padding: 15px; border-radius: 5px; background-color: #374151;">
                <h4 style="color: #D1D5DB;">Emergency Fund Recommendations</h4>
                <p style="color: #D1D5DB;">Based on your monthly housing cost of <b>€{total_housing_cost:.2f}</b>:</p>
                <ul style="color: #D1D5DB;">
                    <li><b>Minimum (3 months):</b> €{min_emergency_fund:.2f}</li>
                    <li><b>Recommended (6 months):</b> €{recommended_emergency_fund:.2f}</li>
                    <li><b>Strong Position (12 months):</b> €{strong_emergency_fund:.2f}</li>
                </ul>
                <p style="color: #D1D5DB;">Your current emergency fund would cover <b>{emergency_fund / total_housing_cost:.1f} months</b> of housing expenses.</p>
                <p style="color: #D1D5DB;">{"<b>Recommendation:</b> Consider increasing your emergency fund to at least 6 months of housing expenses." if emergency_fund < recommended_emergency_fund else
                "<b>Recommendation:</b> Your emergency fund is at a good level, providing appropriate protection against financial stress scenarios."}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 5: Neighborhood Analysis
    with tab5:
        st.markdown('<div class="sub-header">Neighborhood Analysis</div>', unsafe_allow_html=True)
        
        neighborhood_data = generate_neighborhood_data(property_zipcode)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Property value trends (keeping as is since not explicitly requested)
            fig = make_subplots(rows=2, cols=1, subplot_titles=('Median Sale Price Trends', 'Annual Appreciation Rates'),
                            vertical_spacing=0.15)
            fig.add_trace(go.Bar(x=neighborhood_data['Year'], y=neighborhood_data['Median Sale Price'], 
                                name="Median Sale Price", marker_color='#3B82F6'), row=1, col=1)
            fig.add_trace(go.Scatter(x=neighborhood_data['Year'], y=[neighborhood_data['Median Sale Price'].mean()] * len(neighborhood_data), 
                                    line=dict(color='#F87171', width=2, dash='dash'), name="Average"), row=1, col=1)
            fig.add_trace(go.Bar(x=neighborhood_data['Year'], y=neighborhood_data['Appreciation Rate (%)'], 
                                name="Appreciation Rate", marker_color='#FBBF24'), row=2, col=1)
            fig.add_trace(go.Scatter(x=neighborhood_data['Year'], y=[0] * len(neighborhood_data), 
                                    line=dict(color='#D1D5DB', width=1), showlegend=False), row=2, col=1)
            fig.update_layout(
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1, font=dict(color='#D1D5DB')),
                paper_bgcolor='#1F2937',
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB')
            )
            fig.update_yaxes(title_text="Price (€)", row=1, col=1)
            fig.update_yaxes(title_text="Rate (%)", row=2, col=1)
            st.plotly_chart(fig, use_container_width=True)
            
            # Market Activity
            st.markdown('<div class="sub-header">Market Activity</div>', unsafe_allow_html=True)
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=('Days on Market', 'Sales Volume'),
                            specs=[[{"secondary_y": False}, {"secondary_y": False}]])
            
            # Days on Market
            fig.add_trace(
                go.Scatter(
                    x=neighborhood_data['Year'], 
                    y=neighborhood_data['Days on Market'], 
                    name="Days on Market",
                    line=dict(color='#A78BFA', width=3)  # Purple (matches Falling Scenario)
                ),
                row=1, col=1
            )
            
            # Sales Volume
            fig.add_trace(
                go.Bar(
                    x=neighborhood_data['Year'], 
                    y=neighborhood_data['Sales Volume'], 
                    name="Sales Volume",
                    marker_color='#34D399'  # Green (matches Steady Scenario)
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=300,
                paper_bgcolor='#1F2937',  # Matches forecast background
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB'),  # Matches forecast text
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.125,
                    xanchor="right",
                    x=1,
                    font=dict(color='#D1D5DB')
                )
            )
            fig.update_yaxes(title_text="Days", row=1, col=1)
            fig.update_yaxes(title_text="Number of Sales", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Neighborhood statistics
            avg_price = neighborhood_data['Median Sale Price'].mean()
            avg_appreciation = neighborhood_data['Appreciation Rate (%)'].mean()
            latest_appreciation = neighborhood_data['Appreciation Rate (%)'].iloc[-1]
            price_vs_avg = property_value / avg_price * 100
            
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; background-color: #374151;">
                <h4 style="color: #D1D5DB;">Neighborhood Statistics</h4>
                <p style="color: #D1D5DB;"><b>Zipcode:</b> {property_zipcode}</p>
                <p style="color: #D1D5DB;"><b>Average Median Sale Price:</b> €{avg_price:.2f}</p>
                <p style="color: #D1D5DB;"><b>Your Property Value:</b> €{property_value:.2f} ({price_vs_avg:.1f}% of average)</p>
                <p style="color: #D1D5DB;"><b>Avg. Annual Appreciation:</b> {avg_appreciation:.1f}%</p>
                <p style="color: #D1D5DB;"><b>Latest Annual Appreciation:</b> {latest_appreciation:.1f}%</p>
                <p style="color: #D1D5DB;"><b>Market Activity:</b> {neighborhood_data['Days on Market'].iloc[-1]:.1f} days on market</p>
                <p style="color: #D1D5DB;"><b>Sales Volume:</b> {neighborhood_data['Sales Volume'].iloc[-1]:.0f} sales last year</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Market strength assessment
            avg_dom = neighborhood_data['Days on Market'].mean()
            latest_dom = neighborhood_data['Days on Market'].iloc[-1]
            
            dom_trend = "declining" if latest_dom < avg_dom else "increasing"
            dom_market = "hot" if latest_dom < avg_dom else "cooling"
            
            sales_trend = "up" if neighborhood_data['Sales Volume'].iloc[-1] > neighborhood_data['Sales Volume'].iloc[-2] else "down"
            
            st.markdown(f"""
            <div style="margin-top: 15px; padding: 15px; border-radius: 5px; background-color: #374151;">
                <h4 style="color: #D1D5DB;">Market Strength Assessment</h4>
                <p style="color: #D1D5DB;">Days on market is <b>{dom_trend}</b>, indicating a <b>{dom_market}</b> market.</p>
                <p style="color: #D1D5DB;">Sales volume is trending <b>{sales_trend}</b> compared to the previous year.</p>
                <p style="color: #D1D5DB;">Property values are <b>{'increasing' if latest_appreciation > 0 else 'decreasing'}</b> at a rate of <b>{latest_appreciation:.1f}%</b> annually.</p>
                <p style="color: #D1D5DB;"><b>Market Risk Assessment:</b> {'Low' if latest_appreciation > 2 and latest_dom < avg_dom else 'Medium' if latest_appreciation > 0 else 'High'}</p>
            </div>
            """, unsafe_allow_html=True)
                        
            # Property value projection
            st.markdown('<div class="sub-header">Property Value Projection</div>', unsafe_allow_html=True)
            
            # Create projection scenarios
            projection_years = 10
            years = list(range(datetime.now().year, datetime.now().year + projection_years + 1))
            
            # Projection scenarios
            pessimistic_growth = max(0, latest_appreciation - 2)
            expected_growth = latest_appreciation
            optimistic_growth = latest_appreciation + 1
            
            projections = pd.DataFrame({
                'Year': years,
                'Pessimistic': [property_value * (1 + pessimistic_growth/100) ** i for i in range(projection_years + 1)],
                'Expected': [property_value * (1 + expected_growth/100) ** i for i in range(projection_years + 1)],
                'Optimistic': [property_value * (1 + optimistic_growth/100) ** i for i in range(projection_years + 1)]
            })
            
            # Create chart
            fig = px.line(projections, x='Year', y=['Pessimistic', 'Expected', 'Optimistic'],
                        title=f'10-Year Property Value Projection',
                        labels={'value': 'Projected Value (€)', 'variable': 'Scenario'},
                        color_discrete_map={
                            'Pessimistic': '#FBBF24',
                            'Expected': '#3B82F6',
                            'Optimistic': '#34D399'
                        })
            fig.update_layout(
                height=300,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#D1D5DB')),
                paper_bgcolor='#1F2937',
                plot_bgcolor='#1F2937',
                font=dict(color='#D1D5DB')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Print summary
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Loan Risk Summary</div>', unsafe_allow_html=True)
    
    # Define risk thresholds
    dti_thresholds = [28, 36, 43]
    ltv_thresholds = [80, 90, 95]
    
    # Calculate risk level for each metric
    dti_level = "Low" if dti_ratio <= dti_thresholds[0] else "Medium" if dti_ratio <= dti_thresholds[1] else "High" if dti_ratio <= dti_thresholds[2] else "Very High"
    ltv_level = "Low" if ltv_ratio <= ltv_thresholds[0] else "Medium" if ltv_ratio <= ltv_thresholds[1] else "High" if ltv_ratio <= ltv_thresholds[2] else "Very High"
    
    # Create risk summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {'#064E3B' if dti_level == 'Low' else '#78350F' if dti_level == 'Medium' else '#7F1D1D'};">
            <h4 style="color: #D1D5DB;">Debt-to-Income Risk</h4>
            <div style="font-size: 1.8rem; font-weight: bold; color: {'#34D399' if dti_level == 'Low' else '#FBBF24' if dti_level == 'Medium' else '#F87171'};">
                {dti_level}
            </div>
            <p style="color: #D1D5DB;">Your DTI ratio is <b>{dti_ratio:.1f}%</b></p>
            <p style="color: #D1D5DB;"><b>Recommendation:</b> {'Your debt-to-income ratio is within ideal limits.' if dti_level == 'Low' else 'Consider reducing other debts before taking on this loan.' if dti_level == 'Medium' else 'This DTI ratio may make loan approval difficult. Consider reducing the loan amount or paying down other debts.'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {'#064E3B' if ltv_level == 'Low' else '#78350F' if ltv_level == 'Medium' else '#7F1D1D'};">
            <h4 style="color: #D1D5DB;">Loan-to-Value Risk</h4>
            <div style="font-size: 1.8rem; font-weight: bold; color: {'#34D399' if ltv_level == 'Low' else '#FBBF24' if ltv_level == 'Medium' else '#F87171'};">
                {ltv_level}
            </div>
            <p style="color: #D1D5DB;">Your LTV ratio is <b>{ltv_ratio:.1f}%</b></p>
            <p style="color: #D1D5DB;"><b>Recommendation:</b> {'Your loan-to-value ratio is within ideal limits.' if ltv_level == 'Low' else 'Consider making a larger down payment to reduce LTV.' if ltv_level == 'Medium' else 'This LTV may require mortgage insurance and result in higher rates. Consider a larger down payment.'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 5px; background-color: {'#064E3B' if risk_category == 'Low' else '#78350F' if risk_category == 'Medium-Low' else '#7F1D1D'};">
            <h4 style="color: #D1D5DB;">Overall Risk Assessment</h4>
            <div style="font-size: 1.8rem; font-weight: bold; color: {'#34D399' if risk_category == 'Low' else '#FBBF24' if risk_category == 'Medium-Low' else '#F87171'};">
                {risk_category}
            </div>
            <p style="color: #D1D5DB;">Your risk score is <b>{risk_score:.1f}</b></p>
            <p style="color: #D1D5DB;"><b>Recommendation:</b> {'This loan appears to be well-suited to your financial situation.' if risk_category == 'Low' else 'Consider adjusting loan terms or improving financial metrics before proceeding.' if risk_category == 'Medium-Low' else 'Consider substantial changes to loan terms or improving financial metrics before proceeding.'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Final recommendation
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Final Recommendation</div>', unsafe_allow_html=True)
    
    # Generate recommendation based on risk metrics
    if risk_score < 25:
        recommendation = "This loan appears to be well-suited to your financial situation. The risk metrics are within acceptable ranges, and the loan terms align with your financial profile."
        action = "Proceed with confidence."
    elif risk_score < 50:
        recommendation = "This loan presents moderate risk. Consider adjustments to improve your financial position or loan terms."
        action = "Consider adjusting loan amount, term, or improving financial metrics before proceeding."
    else:
        recommendation = "This loan presents significant risk. Substantial changes to loan terms or improvements to your financial metrics are recommended before proceeding."
        action = "Consult with a financial advisor to explore alternative options or improvements to your financial situation."
    
    st.markdown(f"""
    <div class="info-box">
        <h4 style="color: #D1D5DB;">Recommendation</h4>
        <p style="color: #D1D5DB;">{recommendation}</p>
        <p style="color: #D1D5DB;"><b>Suggested Action:</b> {action}</p>
        <p style="color: #D1D5DB;"><b>Next Steps:</b> {'Schedule a consultation with a loan officer to discuss this loan opportunity.' if risk_score < 50 else 'Review your options with a financial advisor before proceeding.'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(
    "**Disclaimer:** This tool provides a simulation based on the information provided and general market data. It is intended for educational purposes only and should not be considered financial advice."
    )


if __name__ == "__main__":
    main()