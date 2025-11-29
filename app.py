# CI/CD test - deployed via GitHub Actions
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Property Investment Calculator - Analyze Real Estate Deals",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Property Investment Calculator")

# URL parser function
def parse_property_url(url):
    """Extract address from LoopNet or Zillow URLs"""
    if not url:
        return None
    
    try:
        if "loopnet.com/Listing/" in url or "zillow.com/homedetails/" in url:
            parts = url.split("/")
            if len(parts) > 4:
                address_part = parts[4]
                # Replace hyphens with spaces
                address = address_part.replace("-", " ")
                # Add comma before state (last 2 characters)
                if len(address) > 2:
                    address = address[:-2] + ", " + address[-2:]
                return address
    except:
        pass
    
    return None

# Initialize property type in query params
if "property_type" not in st.query_params:
    st.query_params["property_type"] = "Residential"

# Property type selection callback
def update_property_type():
    st.query_params["property_type"] = st.session_state.property_type_radio

property_type = st.radio("Property Type", ["Residential", "Commercial"], 
                        key="property_type_radio",
                        index=0 if st.query_params["property_type"] == "Residential" else 1,
                        horizontal=True,
                        on_change=update_property_type)

# Property type explanation
st.write("**Residential**: 4 units or less  |  **Commercial**: 5 units or more")

# Display parsed address as clickable link if available
if property_type == "Residential" and "property_url" in st.query_params and st.query_params["property_url"]:
    address = parse_property_url(st.query_params["property_url"])
    if address:
        st.markdown(f"**Address:** <a href='{st.query_params['property_url']}' target='_blank'>{address}</a>", unsafe_allow_html=True)
elif property_type == "Commercial" and "comm_property_url" in st.query_params and st.query_params["comm_property_url"]:
    address = parse_property_url(st.query_params["comm_property_url"])
    if address:
        st.markdown(f"**Address:** <a href='{st.query_params['comm_property_url']}' target='_blank'>{address}</a>", unsafe_allow_html=True)

if property_type == "Residential":
    # Initialize query params with defaults if not present
    if "purchase_price" not in st.query_params:
        st.query_params["purchase_price"] = "650000"
    if "down_payment" not in st.query_params:
        st.query_params["down_payment"] = "20"
    if "interest_rate" not in st.query_params:
        st.query_params["interest_rate"] = "6.5"
    if "loan_years" not in st.query_params:
        st.query_params["loan_years"] = "15"
    if "monthly_rent" not in st.query_params:
        st.query_params["monthly_rent"] = "5000"
    if "state" not in st.query_params:
        st.query_params["state"] = "CA"
    if "property_url" not in st.query_params:
        st.query_params["property_url"] = ""

    # Residential input callbacks
    def update_purchase_price():
        st.query_params["purchase_price"] = str(st.session_state.purchase_price_input)
    
    def update_down_payment():
        st.query_params["down_payment"] = str(st.session_state.down_payment_input)
    
    def update_interest_rate():
        st.query_params["interest_rate"] = str(st.session_state.interest_rate_input)
    
    def update_loan_years():
        st.query_params["loan_years"] = str(st.session_state.loan_years_input)
    
    def update_monthly_rent():
        st.query_params["monthly_rent"] = str(st.session_state.monthly_rent_input)
    
    def update_state():
        st.query_params["state"] = st.session_state.state_input
    
    def update_property_url():
        st.query_params["property_url"] = st.session_state.property_url_input

    # Sidebar inputs
    with st.sidebar:
        st.header("Property Details")
        purchase_price = st.number_input("Purchase Price", 
                                       value=int(st.query_params["purchase_price"]), 
                                       step=None, format="%d",
                                       key="purchase_price_input",
                                       on_change=update_purchase_price)
        
        # Display formatted purchase price
        st.write(f"**Purchase Price:** ${purchase_price:,.0f}")
        # Down Payment
        down_payment_value = st.number_input("Down Payment %", 
                                           value=int(st.query_params["down_payment"]), 
                                           min_value=0, max_value=100, step=1,
                                           key="down_payment_input",
                                           on_change=update_down_payment)
        
        down_payment_pct = down_payment_value / 100
        
        # Calculate and display the actual down payment amount
        amount_down = purchase_price * down_payment_pct
        st.metric("Down Payment Amount", f"${amount_down:,.2f}")
        
        # Interest Rate
        interest_rate_value = st.number_input("Interest Rate %", 
                                            value=float(st.query_params["interest_rate"]), 
                                            min_value=0.0, max_value=10.0, step=0.1,
                                            key="interest_rate_input",
                                            on_change=update_interest_rate)
        
        interest_rate = interest_rate_value / 100
        loan_years = st.selectbox("Loan Term (Years)", [15, 30], 
                                index=0 if st.query_params["loan_years"] == "15" else 1,
                                key="loan_years_input",
                                on_change=update_loan_years)
            
        monthly_rent = st.number_input("Expected Monthly Rent", 
                                     value=int(st.query_params["monthly_rent"]), 
                                     step=100,
                                     key="monthly_rent_input",
                                     on_change=update_monthly_rent)
        
        st.header("Location")
        states = ["AZ", "CA", "IN", "NV", "TX", "MI"]
        state = st.selectbox("State", states, 
                           index=states.index(st.query_params["state"]),
                           key="state_input",
                           on_change=update_state)
        
        TAX_RATES = {
            "AZ": 0.0062,
            "CA": 0.0125,
            "IN": 0.0137,
            "NV": 0.0065,
            "TX": 0.0170,
            "MI": 0.0321
        }
        
        # Display the tax rate for the selected state (converted to a percentage)
        selected_tax_rate = TAX_RATES[state]
        st.metric("Tax Rate", f"{selected_tax_rate * 100:.2f}%")
        
        st.header("Property URL")
        property_url = st.text_input("Property Listing URL", 
                                   value=st.query_params["property_url"],
                                   placeholder="https://www.zillow.com/...",
                                   help="Link to property listing (Zillow, Realtor.com, etc.)",
                                   key="property_url_input",
                                   on_change=update_property_url)
        
        if property_url.strip():
            try:
                st.link_button("View Property Listing", property_url)
            except AttributeError:
                # Fallback for older Streamlit versions
                st.markdown(f'''
                <a href="{property_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    background-color: #ff4b4b;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    border: 1px solid transparent;
                    text-align: center;
                    font-weight: 400;
                    font-size: 14px;
                    cursor: pointer;
                ">View Property Listing</a>
                ''', unsafe_allow_html=True)

    # Calculations
    loan_amount = purchase_price * (1 - down_payment_pct)
    monthly_rate = interest_rate / 12
    num_payments = loan_years * 12
    
    # Monthly Principal & Interest Payment
    monthly_pi = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    # Other monthly costs
    monthly_insurance = (purchase_price * 0.01) / 12
    monthly_tax = (purchase_price * TAX_RATES[state]) / 12
    pm_fee = monthly_rent * 0.10
    maintenance = 250
    
    total_monthly = monthly_pi + monthly_insurance + monthly_tax + pm_fee + maintenance
    
    # Cash flow analysis
    occupancy_rates = [0.75, 0.90, 1.0]
    cash_flows = []
    annual_returns = []
    
    for rate in occupancy_rates:
        monthly_income = monthly_rent * rate
        cash_flow = monthly_income - total_monthly
        annual_return = (cash_flow * 12) / (purchase_price * down_payment_pct) * 100
        cash_flows.append(cash_flow)
        annual_returns.append(annual_return)

    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Monthly Expenses")
        expenses_df = pd.DataFrame({
            "Expense": ["Principal & Interest", "Insurance", "Property Tax", "Property Management", "Maintenance"],
            "Amount": [monthly_pi, monthly_insurance, monthly_tax, pm_fee, maintenance]
        })
        st.dataframe(expenses_df.style.format({"Amount": "${:,.2f}"}), hide_index=True)
    
    with col2:
        st.header("Investment Returns")
        returns_df = pd.DataFrame({
            "Scenario": ["75% Occupancy", "90% Occupancy", "100% Occupancy"],
            "Monthly Cash Flow": cash_flows,
            "Annual ROI": annual_returns
        })
        
        def color_negative_red(val):
            color = 'red' if val < 0 else 'green'
            return f'color: {color}'
        
        st.dataframe(
            returns_df.style
            .format({
                "Monthly Cash Flow": "${:,.2f}", 
                "Annual ROI": "{:.1f}%"
            })
            .map(color_negative_red, subset=["Monthly Cash Flow", "Annual ROI"]),
            hide_index=True
        )
    
    # Investment status
    st.header("Investment Status")
    if cash_flows[0] > 0:  # Profitable at 75% occupancy
        st.success("✅ Good Investment: Profitable even at 75% occupancy")
    else:
        st.error("❌ High Risk: Not profitable at 75% occupancy")
    
    # Amortization Schedule
    st.header("Amortization Schedule")
    schedule = []
    balance = loan_amount
    
    for payment in range(1, 13):  # First year only
        interest_payment = balance * monthly_rate
        principal_payment = monthly_pi - interest_payment
        balance = balance - principal_payment
        
        schedule.append({
            "Payment": payment,
            "Principal": principal_payment,
            "Interest": interest_payment,
            "Balance": balance
        })
    
    schedule_df = pd.DataFrame(schedule)
    st.dataframe(
        schedule_df.style.format({
            "Principal": "${:,.2f}",
            "Interest": "${:,.2f}",
            "Balance": "${:,.2f}"
        }),
        hide_index=True
    )
    
    # Balance Over Time chart
    fig = px.line(
        schedule_df, 
        x="Payment", 
        y="Balance",
        title="Loan Balance Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

elif property_type == "Commercial":
    # Commercial property logic
    
    # Initialize commercial query params with Excel defaults
    if "comm_state" not in st.query_params:
        st.query_params["comm_state"] = "CA"
    if "comm_purchase_price" not in st.query_params:
        st.query_params["comm_purchase_price"] = "1970000"
    if "comm_down_payment" not in st.query_params:
        st.query_params["comm_down_payment"] = "30"
    if "comm_annual_gross_rents" not in st.query_params:
        st.query_params["comm_annual_gross_rents"] = "152195"
    if "comm_annual_noi_listing" not in st.query_params:
        st.query_params["comm_annual_noi_listing"] = "106548"
    if "comm_vacancy_rate" not in st.query_params:
        st.query_params["comm_vacancy_rate"] = "3"
    if "comm_other_expenses" not in st.query_params:
        st.query_params["comm_other_expenses"] = "5000"
    if "comm_loan_years" not in st.query_params:
        st.query_params["comm_loan_years"] = "25"
    if "comm_interest_rate" not in st.query_params:
        st.query_params["comm_interest_rate"] = "6.5"
    if "comm_property_url" not in st.query_params:
        st.query_params["comm_property_url"] = ""
    
    # Commercial tax and insurance rates
    COMMERCIAL_TAX_RATES = {
        "AZ": 0.0062,
        "CA": 0.0125,
        "IN": 0.0137,
        "NV": 0.0065,
        "TX": 0.0170,
        "MI": 0.0321
    }
    
    COMMERCIAL_INSURANCE_RATES = {
        "AZ": 0.005,
        "CA": 0.0125,
        "IN": 0.005,
        "NV": 0.005,
        "TX": 0.005,
        "MI": 0.005
    }
    
    # Commercial input callbacks
    def update_comm_purchase_price():
        st.query_params["comm_purchase_price"] = str(st.session_state.comm_purchase_price_input)
    
    def update_comm_down_payment():
        st.query_params["comm_down_payment"] = str(st.session_state.comm_down_payment_input)
    
    def update_comm_gross_rents():
        st.query_params["comm_annual_gross_rents"] = str(st.session_state.comm_gross_rents_input)
    
    def update_comm_noi_listing():
        st.query_params["comm_annual_noi_listing"] = str(st.session_state.comm_noi_input)
    
    def update_comm_vacancy_rate():
        st.query_params["comm_vacancy_rate"] = str(st.session_state.comm_vacancy_input)
    
    def update_comm_other_expenses():
        st.query_params["comm_other_expenses"] = str(st.session_state.comm_expenses_input)
    
    def update_comm_interest_rate():
        st.query_params["comm_interest_rate"] = str(st.session_state.comm_interest_input)
    
    def update_comm_loan_years():
        st.query_params["comm_loan_years"] = str(st.session_state.comm_loan_years_input)
    
    def update_comm_state():
        st.query_params["comm_state"] = st.session_state.comm_state_input
    
    def update_comm_property_url():
        st.query_params["comm_property_url"] = st.session_state.comm_property_url_input

    # Commercial sidebar inputs
    with st.sidebar:
        st.header("Commercial Property Details")
        
        # Purchase Price
        comm_purchase_price = st.number_input("Purchase Price", 
                                             value=int(st.query_params["comm_purchase_price"]), 
                                             step=None, format="%d", 
                                             help="Purchase Price or Amount we want to offer",
                                             key="comm_purchase_price_input",
                                             on_change=update_comm_purchase_price)
        
        st.write(f"**Purchase Price:** ${comm_purchase_price:,.0f}")
        
        # Down Payment %
        comm_down_payment_pct = st.number_input("% Down Payment", 
                                               value=int(st.query_params["comm_down_payment"]), 
                                               min_value=0, max_value=100, step=1, 
                                               help="Standard % down is 25% for Non-owner occupied Resi loans. 30%+ may be required for hard money but the interest will be much higher.\n\nFor commercial loans of 5 units or more, the minimum down should be 30% down is a more safe bet, with 65% LTV more ideal for commercial lenders.\n\nTo evaluate whether more money down makes this a good deal or not, 1st try 100%. If the cash flow is not positive with 100% down, then it does not make sense at all at this price, with this rent, or with this overhead.",
                                               key="comm_down_payment_input",
                                               on_change=update_comm_down_payment)
        
        # Calculate Amount Down with color coding 
        amount_down = comm_purchase_price * (comm_down_payment_pct / 100)
        amount_down_help = "Conditional formatting is:\n≤ $500,000 = green\n>$500,000 and ≤ $750,000 = yellow\n>$750,000 = red\n\nThese are based on the parameters currently in place for raising debt free capital. This could mean liquidating other assets or getting other investors involved."
        
        # Display Amount Down with color coding only (no visible explanation text)
        if amount_down <= 500000:
            st.markdown(f"**Amount Down:** :green[${amount_down:,.0f}]")
        elif amount_down <= 750000:
            st.markdown(f"**Amount Down:** :orange[${amount_down:,.0f}]")
        else:
            st.markdown(f"**Amount Down:** :red[${amount_down:,.0f}]")
        
        # Closing Costs (calculated as 3% of purchase price, matching Excel formula J3=H3*0.03)
        closing_costs = comm_purchase_price * 0.03
        st.metric("Estimated Closing Costs", f"${closing_costs:,.0f}", help="Estimated closing costs @ 3% of purchase price")
        
        
        # Annual Gross Rents
        comm_annual_gross_rents = st.number_input("Annual Gross Rents", 
                                                 value=int(st.query_params["comm_annual_gross_rents"]), 
                                                 step=1000, 
                                                 help="Typically provided in the listing on LoopNet, etc.",
                                                 key="comm_gross_rents_input",
                                                 on_change=update_comm_gross_rents)
        
        # Annual NOI from Listing
        comm_annual_noi_listing = st.number_input("Annual NOI from Listing", 
                                                 value=int(st.query_params["comm_annual_noi_listing"]), 
                                                 step=1000,
                                                 key="comm_noi_input",
                                                 on_change=update_comm_noi_listing)
        
        # Vacancy Rate
        comm_vacancy_rate = st.number_input("Vacancy Rate %", 
                                           value=int(st.query_params["comm_vacancy_rate"]), 
                                           min_value=0, max_value=50, step=1,
                                           key="comm_vacancy_input",
                                           on_change=update_comm_vacancy_rate)
        
        # All Other Operating Expenses
        comm_other_expenses = st.number_input("All Other Operating Expenses", 
                                             value=int(st.query_params["comm_other_expenses"]), 
                                             step=500,
                                             key="comm_expenses_input",
                                             on_change=update_comm_other_expenses)
        
        st.header("Loan Details")
        # Interest Rate
        comm_interest_rate_value = st.number_input("Interest Rate %", 
                                                  value=float(st.query_params["comm_interest_rate"]), 
                                                  min_value=0.0, max_value=20.0, step=0.1,
                                                  key="comm_interest_input",
                                                  on_change=update_comm_interest_rate)
        
        # Loan Period
        loan_years_options = list(range(1, 31))  # 1 to 30 years
        comm_loan_years = st.selectbox("Loan Period (Years)", loan_years_options, 
                                     index=loan_years_options.index(int(st.query_params["comm_loan_years"])),
                                     key="comm_loan_years_input",
                                     on_change=update_comm_loan_years)
        
        st.header("Location")
        states = ["AZ", "CA", "IN", "NV", "TX", "MI"]
        comm_state = st.selectbox("State", states, 
                                index=states.index(st.query_params["comm_state"]),
                                key="comm_state_input",
                                on_change=update_comm_state)
        
        st.header("Lookup Rates")
        selected_tax_rate = COMMERCIAL_TAX_RATES[comm_state]
        selected_insurance_rate = COMMERCIAL_INSURANCE_RATES[comm_state]
        st.metric("Tax Rate", f"{selected_tax_rate * 100:.2f}%")
        st.metric("Insurance Rate", f"{selected_insurance_rate * 100:.1f}%")
        
        st.header("Property URL")
        comm_property_url = st.text_input("Property Listing URL", 
                                        value=st.query_params["comm_property_url"],
                                        placeholder="https://www.loopnet.com/...",
                                        help="Link to property listing (LoopNet, Crexi, etc.)",
                                        key="comm_property_url_input",
                                        on_change=update_comm_property_url)
        
        if comm_property_url.strip():
            try:
                st.link_button("View Property Listing", comm_property_url)
            except AttributeError:
                # Fallback for older Streamlit versions
                st.markdown(f'''
                <a href="{comm_property_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    background-color: #ff4b4b;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    border: 1px solid transparent;
                    text-align: center;
                    font-weight: 400;
                    font-size: 14px;
                    cursor: pointer;
                ">View Property Listing</a>
                ''', unsafe_allow_html=True)
    
    # Commercial calculations based on Excel formulas
    
    # Annual operating expenses
    annual_insurance = comm_purchase_price * selected_insurance_rate
    annual_property_tax = comm_purchase_price * selected_tax_rate
    annual_pm_fee = comm_annual_gross_rents * 0.04  # 4% of gross rents
    
    # NOI Estimated calculation: (K4*(1-L5))-SUM(J8:J11)
    # Excel formula: =(K4*(1-L5))-SUM(J8:J11) where J8:J11 are ONLY operating expenses (not debt service)
    total_operating_expenses = annual_insurance + annual_property_tax + annual_pm_fee + comm_other_expenses
    noi_estimated = (comm_annual_gross_rents * (1 - comm_vacancy_rate/100)) - total_operating_expenses
    
    # Commercial loan calculations (user-defined years and rate)
    comm_loan_amount = comm_purchase_price - amount_down
    comm_annual_interest_rate = comm_interest_rate_value / 100
    comm_monthly_rate = comm_annual_interest_rate / 12
    comm_num_payments = comm_loan_years * 12
    
    # Annual debt service
    monthly_payment = comm_loan_amount * (comm_monthly_rate * (1 + comm_monthly_rate) ** comm_num_payments) / ((1 + comm_monthly_rate) ** comm_num_payments - 1)
    annual_debt_service = monthly_payment * 12
    
    # Cash flow calculation: NOI - Annual Debt Service
    annual_cash_flow = noi_estimated - annual_debt_service
    
    # Closing costs (3% of purchase price)
    closing_costs = comm_purchase_price * 0.03
    
    # Total cash down
    total_cash_down = amount_down + closing_costs
    
    # Cash-on-cash return calculation
    cash_on_cash_return = (annual_cash_flow / total_cash_down) * 100 if total_cash_down > 0 else 0
    
    # Display commercial results
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Operating Expenses")
        expenses_df = pd.DataFrame({
            "Expense": ["Purchase Loan P&I", "Property Insurance Insurance", "Property Taxes", "PM Fee", "All Other Operating Expenses"],
            "Monthly Amount": [monthly_payment, annual_insurance/12, annual_property_tax/12, annual_pm_fee/12, comm_other_expenses/12],
            "Annual Amount": [annual_debt_service, annual_insurance, annual_property_tax, annual_pm_fee, comm_other_expenses]
        })
        st.dataframe(expenses_df.style.format({"Monthly Amount": "${:,.2f}", "Annual Amount": "${:,.0f}"}), hide_index=True)
        
        with st.expander("📋 Expense Notes"):
            st.write("**Property Insurance Insurance**: Rough estimate based on industry average. Double check this value for the specific property and zip code.")
            st.write("**PM Fee**: Prop Mgmt Fees on commercial properties are generally 3-4% of gross rents received/collected, with a minimum typically established.")
        
        st.metric("Total Annual Operating Expenses", f"${annual_insurance + annual_property_tax + annual_pm_fee + comm_other_expenses:,.0f}")
    
    with col2:
        st.header("Investment Analysis")
        # Create Cash Down string with color
        if total_cash_down <= 500000:
            cash_down_display = f"${total_cash_down:,.0f}"
        elif total_cash_down <= 750000:
            cash_down_display = f"${total_cash_down:,.0f}"
        else:
            cash_down_display = f"${total_cash_down:,.0f}"
            
        analysis_df = pd.DataFrame({
            "Metric": ["Annual Gross Rents", "Adjusted Gross Income", "Annual NOI (Estimated)", "Annual Debt Service", "Annual Cash Flow", "Cash-on-Cash Return", "Cash Down"],
            "Amount": [
                f"${comm_annual_gross_rents:,.0f}",
                f"${comm_annual_gross_rents * (1 - comm_vacancy_rate/100):,.0f}",
                f"${noi_estimated:,.0f}",
                f"${annual_debt_service:,.0f}",
                f"${annual_cash_flow:,.0f}",
                f"{cash_on_cash_return:.1f}%",
                cash_down_display
            ]
        })
        st.dataframe(analysis_df, hide_index=True)
    
    # Deal evaluation
    st.header("Deal Evaluation")
    if annual_cash_flow > 0:
        st.success("✅ GOOD DEAL: Positive annual cash flow")
    else:
        st.error("❌ BAD DEAL: Negative annual cash flow")
    
    # Investment summary
    st.header("Investment Summary")
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.metric("Purchase Price", f"${comm_purchase_price:,.0f}")
        st.metric("Down Payment", f"${amount_down:,.0f} ({comm_down_payment_pct}%)")
        st.metric("Closing Costs", f"${closing_costs:,.0f}", help="closing costs @ 3%")
        st.metric("Total Cash Investment", f"${total_cash_down:,.0f}")
    
    with summary_col2:
        st.metric("Loan Amount", f"${comm_loan_amount:,.0f}")
        st.metric("Monthly Payment", f"${monthly_payment:,.0f}")
        st.metric("Annual NOI (Estimated)", f"${noi_estimated:,.0f}")
        
        # Color-coded cash flow metric
        if annual_cash_flow > 0:
            st.metric("Annual Cash Flow", f"${annual_cash_flow:,.0f}", delta="Positive cash flow", delta_color="normal")
        else:
            st.metric("Annual Cash Flow", f"${annual_cash_flow:,.0f}", delta="Negative cash flow", delta_color="inverse")
