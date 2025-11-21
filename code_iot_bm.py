import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Game Constants & Difficulty Settings ---
STARTING_CASH = 15.0  # Million USD
QUARTERS_TOTAL = 12
WINNING_VALUATION = 150.0 

# Business Model Dynamics
# Margin: Profitability %
# Lag: Quarters before revenue starts flowing
# Cannibalization: How much $1 of this revenue reduces Traditional Hardware revenue
MODELS = {
    "Traditional": {"margin": 0.15, "cannibalization": 0.0},
    "Service":     {"margin": 0.35, "cannibalization": 0.3}, # Apex Concept: Reducing spare parts sales
    "Process":     {"margin": 0.55, "cannibalization": 0.1},
    "Cloud":       {"margin": 0.85, "cannibalization": 0.0} 
}

# --- State Initialization ---
if 'game_active' not in st.session_state:
    st.session_state.game_active = True
    st.session_state.quarter = 1
    st.session_state.cash = STARTING_CASH
    st.session_state.valuation = 0
    st.session_state.logs = []
    
    # Metrics
    st.session_state.revenue = {"Traditional": 12.0, "Service": 0.0, "Process": 0.0, "Cloud": 0.0}
    st.session_state.metrics = {
        "Tech_Maturity": 10.0,  # Quality of the product
        "Sales_Morale": 80.0,   # Ability to sell (Apex Concept)
        "Customer_Trust": 40.0  # Willingness to buy digital (Orion Concept)
    }
    
    # History for Charts
    st.session_state.history = pd.DataFrame(columns=['Quarter', 'Cash', 'Valuation', 'Revenue'])

# --- Helper Functions ---
def log_event(message, type="info"):
    icon = "ℹ️"
    if type == "warning": icon = "⚠️"
    if type == "danger": icon = "🔥"
    if type == "success": icon = "✅"
    st.session_state.logs.insert(0, f"{icon} Q{st.session_state.quarter}: {message}")

def calculate_valuation():
    # Valuation Multipliers based on revenue quality
    # Hardware = 1x, Service = 3x, SaaS/Cloud = 10x
    val = (st.session_state.revenue["Traditional"] * 1.0) + \
          (st.session_state.revenue["Service"] * 3.0) + \
          (st.session_state.revenue["Process"] * 6.0) + \
          (st.session_state.revenue["Cloud"] * 10.0)
    return val

# --- Main UI ---
st.set_page_config(page_title="Apex-Orion Strategy Sim", layout="wide")
st.title("🏭 Industrial IoT Strategy Simulator")
st.markdown("### Challenge: Survive the 'Swallow the Fish' Curve")
st.caption("Based on Apex Precision & Orion Logistics Case Studies")

# Sidebar Stats
with st.sidebar:
    st.header(f"QUARTER {st.session_state.quarter} / {QUARTERS_TOTAL}")
    
    cash_color = "normal"
    if st.session_state.cash < 3.0: cash_color = "off" # Red
    st.metric("Cash Reserves", f"${st.session_state.cash:.1f}M", delta_color=cash_color)
    
    current_val = calculate_valuation()
    st.metric("Company Valuation", f"${current_val:.1f}M")
    
    st.divider()
    st.write("### 📊 Organization Health")
    st.progress(st.session_state.metrics["Tech_Maturity"]/100, text="Tech Maturity (Product)")
    st.progress(st.session_state.metrics["Sales_Morale"]/100, text="Sales Morale (Culture)")
    st.progress(st.session_state.metrics["Customer_Trust"]/100, text="Customer Trust (Brand)")
    
    st.divider()
    if st.button("Restart Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Game Over Check ---
if st.session_state.cash < 0:
    st.error("💔 BANKRUPTCY! You ran out of cash. The Board has fired you.")
    st.stop()

if st.session_state.quarter > QUARTERS_TOTAL:
    st.success("🏁 Simulation Complete!")
    final_score = calculate_valuation()
    st.metric("FINAL SCORE", f"${final_score:.1f}M")
    if final_score > WINNING_VALUATION:
        st.balloons()
        st.markdown("### 🏆 GRADE: A (Visionary)")
        st.write("You successfully navigated the transition, balancing cash flow with high-growth innovation.")
    elif final_score > 80:
        st.markdown("### 🥈 GRADE: B (Survivor)")
        st.write("You survived, but failed to unlock exponential value.")
    else:
        st.markdown("### 🥉 GRADE: C (Stagnant)")
        st.write("You protected the core but missed the digital revolution.")
    st.stop()

# --- Decision Dashboard ---
col1, col2 = st.columns([1.5, 1])

with col1:
    with st.form("turn_form"):
        st.subheader("Quarterly Decisions")
        st.info("Budget Limit: Spending > $2.5M per quarter burns into Cash Reserves.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            spend_rd = st.number_input("R&D Investment ($M)", 0.0, 5.0, 0.5, step=0.5, help="Improves Tech Maturity. Enables Cloud/Process models.")
        with c2:
            spend_change = st.number_input("Change Mgmt ($M)", 0.0, 5.0, 0.5, step=0.5, help="Training & Incentives. Improves Sales Morale.")
        with c3:
            spend_marketing = st.number_input("Go-To-Market ($M)", 0.0, 5.0, 0.5, step=0.5, help="Pilots & Branding. Improves Customer Trust.")
        
        st.divider()
        
        st.markdown("**Strategic Priority (Select One):**")
        strategy = st.radio("Focus:", [
            "Defend Core (Hardware)",
            "Launch Service (Predictive Maint)", 
            "Launch Process (Optimization)", 
            "Launch Cloud (Platform)"
        ], horizontal=True)
        
        submit = st.form_submit_button("👉 Execute Quarter")

with col2:
    st.subheader("Event Log")
    for log in st.session_state.logs[:4]:
        st.write(log)
    
    st.subheader("Revenue Mix")
    rev_df = pd.DataFrame.from_dict(st.session_state.revenue, orient='index', columns=['Revenue'])
    st.bar_chart(rev_df)

# --- Game Logic Engine ---
if submit:
    # 1. Financials
    total_spend = spend_rd + spend_change + spend_marketing
    burn_rate = 1.0 # Fixed Ops Cost
    
    # 2. Update Organizational Metrics (The "Soft" Skills)
    # R&D increases Tech, but decays slightly
    st.session_state.metrics["Tech_Maturity"] += (spend_rd * 4) - 1
    
    # Change Mgmt increases Morale. If you spend 0, Morale tanks (Apex Scenario)
    if spend_change < 0.5:
        st.session_state.metrics["Sales_Morale"] -= 10
        log_event("Sales team demoralized due to lack of training!", "warning")
    else:
        st.session_state.metrics["Sales_Morale"] += (spend_change * 3)
        
    # Marketing increases Trust
    st.session_state.metrics["Customer_Trust"] += (spend_marketing * 3) - 0.5
    
    # Cap metrics at 100
    for k in st.session_state.metrics:
        st.session_state.metrics[k] = max(0, min(100, st.session_state.metrics[k]))

    # 3. Calculate Revenue Impact based on Strategy
    
    # Multipliers based on Org Health
    tech_factor = st.session_state.metrics["Tech_Maturity"] / 100
    sales_factor = st.session_state.metrics["Sales_Morale"] / 100
    trust_factor = st.session_state.metrics["Customer_Trust"] / 100
    
    # BASE DECLINE of Traditional Hardware (Commoditization)
    st.session_state.revenue["Traditional"] *= 0.95 
    
    if strategy == "Defend Core (Hardware)":
        st.session_state.revenue["Traditional"] *= 1.03 # Mitigate decline
        
    elif strategy == "Launch Service (Predictive Maint)":
        # Low Tech requirement, High Sales requirement
        growth = 1.5 * sales_factor
        st.session_state.revenue["Service"] += growth
        # Cannibalization Effect (Apex)
        st.session_state.revenue["Traditional"] -= (growth * MODELS["Service"]["cannibalization"])
        log_event("Service contracts growing. Spare parts revenue declining.", "info")

    elif strategy == "Launch Process (Optimization)":
        # Needs Trust and Tech
        if trust_factor > 0.5:
            growth = 1.2 * tech_factor * trust_factor
            st.session_state.revenue["Process"] += growth
        else:
            log_event("Process Launch Failed! Trust too low.", "danger")
            
    elif strategy == "Launch Cloud (Platform)":
        # Needs High Tech & High Trust
        if tech_factor > 0.7 and trust_factor > 0.7:
            # Exponential Growth (J-Curve kicker)
            existing = st.session_state.revenue["Cloud"]
            growth = 1.0 + (existing * 0.4) # 40% QoQ growth
            st.session_state.revenue["Cloud"] += growth
            log_event("Cloud Platform scaling!", "success")
        else:
            log_event("Cloud Launch Disaster! Product buggy or no trust.", "danger")
            st.session_state.metrics["Customer_Trust"] -= 10
            st.session_state.cash -= 2.0 # Penalty for failed launch cleanup

    # 4. Cash Flow Calculation
    gross_profit = 0
    for model, amt in st.session_state.revenue.items():
        gross_profit += amt * MODELS[model]["margin"]
    
    net_change = gross_profit - total_spend - burn_rate
    st.session_state.cash += net_change
    
    # 5. Random Events (Chaos Monkey)
    rng = np.random.random()
    if st.session_state.quarter == 4 and rng > 0.3:
        log_event("Competitor slashes hardware prices by 20%. Core revenue hit.", "warning")
        st.session_state.revenue["Traditional"] *= 0.8
    elif st.session_state.quarter == 8 and st.session_state.metrics["Tech_Maturity"] < 50:
        log_event("Major sensor failure at client site! Trust tanks.", "danger")
        st.session_state.metrics["Customer_Trust"] -= 20
        st.session_state.cash -= 1.0

    # 6. Update History & Turn
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([{
        "Quarter": st.session_state.quarter,
        "Cash": st.session_state.cash,
        "Valuation": calculate_valuation(),
        "Revenue": sum(st.session_state.revenue.values())
    }])], ignore_index=True)
    
    st.session_state.quarter += 1
    st.rerun()
