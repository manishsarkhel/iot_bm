import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Game Constants ---
STARTING_CASH = 20.0  # Million USD
QUARTERS_TOTAL = 12
WINNING_VALUATION = 200.0 

# Cost Structures
HOLDING_COST_PER_UNIT = 0.5  # Cost to store spare parts
STOCKOUT_PENALTY = 2.0       # Cost of not having a part when needed
HARDWARE_MARGIN = 0.15       # Slim margin on steel
SERVICE_MARGIN = 0.40        # Margin on labor/contracts
PARTS_MARGIN = 0.60          # High margin on spare parts (The Trap)

# --- State Initialization ---
if 'game_active' not in st.session_state:
    st.session_state.game_active = True
    st.session_state.quarter = 1
    st.session_state.cash = STARTING_CASH
    st.session_state.logs = []
    
    # Core Business Metrics
    st.session_state.installed_base = 1000 # Number of machines in market
    st.session_state.contract_mix = {"Transactional": 100, "Outcome": 0} # % Split
    
    # Hidden Variables (The "Engine")
    st.session_state.data_accuracy = 20.0 # Ability to predict failures
    st.session_state.sales_culture = 50.0 # Ability to sell contracts
    st.session_state.customer_trust = 40.0 # Willingness to sign contracts
    
    # External Factors
    st.session_state.competitor_price = 1.0 # Index (1.0 = Parity)
    
    # History
    st.session_state.history = pd.DataFrame(columns=['Quarter', 'Cash', 'Valuation', 'Rev_Mix'])

# --- Helper Functions ---
def log_event(message, type="info"):
    icon_map = {"info": "ℹ️", "warning": "⚠️", "danger": "🔥", "success": "✅", "money": "💰"}
    icon = icon_map.get(type, "ℹ️")
    st.session_state.logs.insert(0, f"{icon} Q{st.session_state.quarter}: {message}")

def calculate_valuation(rev_stream):
    # Outcome revenue is valued 5x higher by Wall St than One-off Hardware revenue
    val = (rev_stream["Hardware"] * 0.8) + \
          (rev_stream["Parts"] * 1.0) + \
          (rev_stream["Service"] * 5.0)
    return val

# --- Main UI ---
st.set_page_config(page_title="Apex-Orion Advanced Sim", layout="wide")
st.title("🏭 Strategic Pivot: The Principal-Agent Simulator")
st.markdown("""
**Objective:** Maximise Valuation. **Constraint:** Don't run out of Cash.
* **Game Theory:** Moving to 'Outcome' aligns incentives but kills your 'Spare Parts' cash cow.
* **Supply Chain:** 'Lean' inventory saves money but risks stockouts if your Data isn't good.
""")

# Sidebar
with st.sidebar:
    st.header(f"QUARTER {st.session_state.quarter} / {QUARTERS_TOTAL}")
    
    cash_color = "normal"
    if st.session_state.cash < 5.0: cash_color = "off"
    st.metric("Cash Reserves", f"${st.session_state.cash:.1f}M", delta_color=cash_color)
    
    # Show Contract Mix
    df_mix = pd.DataFrame([st.session_state.contract_mix])
    st.write("### Contract Mix (The Game)")
    st.bar_chart(df_mix.T)
    
    st.divider()
    st.write("### 📊 Operational Health")
    st.progress(st.session_state.data_accuracy/100, text="Data Accuracy (Prediction)")
    st.progress(st.session_state.sales_culture/100, text="Sales Culture (Hunter vs Farmer)")
    st.progress(st.session_state.customer_trust/100, text="Customer Trust (Principal)")
    
    if st.button("Restart Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Game Over Check ---
if st.session_state.cash < 0:
    st.error("💔 BANKRUPTCY! You fell into the 'Swallow the Fish' cash trough.")
    st.stop()

if st.session_state.quarter > QUARTERS_TOTAL:
    st.success("🏁 Simulation Complete!")
    # Recalculate final valuation
    # (Placeholder logic for simplicity of display, real logic in loop)
    st.balloons()
    st.stop()

# --- Decision Dashboard ---
col1, col2 = st.columns([1.5, 1])

with col1:
    with st.form("turn_form"):
        st.subheader("1. Resource Allocation ($M)")
        c1, c2, c3 = st.columns(3)
        with c1:
            invest_iot = st.number_input("IoT R&D", 0.0, 5.0, 0.0, step=0.5, help="Improves Data Accuracy. Reduces Inventory Risk.")
        with c2:
            invest_train = st.number_input("Sales Training", 0.0, 5.0, 0.0, step=0.5, help="Improves Sales Culture. Allows shifting to Outcome contracts.")
        with c3:
            invest_brand = st.number_input("Brand/Trust", 0.0, 5.0, 0.0, step=0.5, help="Improves Trust. Protects against Competitor Price Cuts.")

        st.divider()
        st.subheader("2. Strategic Moves")
        
        # Game Theory Move
        st.markdown("**Contract Strategy (Principal-Agent):**")
        contract_target = st.slider("Target % of Clients on 'Outcome-Based' Contracts", 0, 100, st.session_state.contract_mix["Outcome"], help="Moving here creates recurring revenue but kills spare parts sales.")
        
        # Supply Chain Move
        st.markdown("**Inventory Strategy (Supply Chain):**")
        inventory_strat = st.select_slider("Spare Parts Inventory Level", options=["Lean (JIT)", "Balanced", "Hoard (Safe)"], value="Balanced")
        
        submit = st.form_submit_button("👉 Execute Quarter")

with col2:
    st.subheader("Market News")
    for log in st.session_state.logs[:5]:
        st.write(log)

# --- Simulation Logic ---
if submit:
    # 0. Expenses
    total_spend = invest_iot + invest_train + invest_brand
    fixed_burn = 2.0
    st.session_state.cash -= (total_spend + fixed_burn)
    
    # 1. Update Capabilities
    st.session_state.data_accuracy += (invest_iot * 5)
    st.session_state.sales_culture += (invest_train * 4)
    st.session_state.customer_trust += (invest_brand * 3)
    
    # Competitor Move (The "SeoulHydra" Threat)
    st.session_state.competitor_price -= 0.02 # Gets cheaper every quarter
    if st.session_state.competitor_price < 0.8:
        log_event("Competitor prices are now 20% lower than yours!", "warning")

    # 2. Contract Negotiation (Can we actually move clients?)
    # We can only shift clients if Sales Culture + Trust are high enough
    desired_shift = contract_target - st.session_state.contract_mix["Outcome"]
    max_possible_shift = (st.session_state.sales_culture + st.session_state.customer_trust) / 10
    
    actual_shift = min(desired_shift, max_possible_shift)
    if desired_shift > 0 and actual_shift < desired_shift:
        log_event("Sales team struggled to close Outcome contracts. Culture too low.", "warning")
    
    st.session_state.contract_mix["Outcome"] += actual_shift
    st.session_state.contract_mix["Transactional"] = 100 - st.session_state.contract_mix["Outcome"]

    # 3. The "Event" (Random Breakdowns)
    # The better your IoT Data, the fewer CATASTROPHIC breakdowns
    base_breakdown_rate = 0.10 # 10% of machines break
    preventable_rate = (st.session_state.data_accuracy / 100) * 0.8 # up to 80% preventable
    actual_breakdowns = base_breakdown_rate * (1 - preventable_rate)
    
    num_broken = st.session_state.installed_base * actual_breakdowns
    
    # 4. Supply Chain Impact (The Bullwhip)
    # Did we have the parts?
    if inventory_strat == "Hoard (Safe)":
        holding_cost = 3.0
        stockout_chance = 0.0
    elif inventory_strat == "Balanced":
        holding_cost = 1.5
        stockout_chance = 0.1 - (st.session_state.data_accuracy/200) # Data helps reduce risk
    else: # Lean
        holding_cost = 0.5
        # If data is low, Lean is suicide
        stockout_chance = 0.4 - (st.session_state.data_accuracy/200)
    
    stockout_chance = max(0, stockout_chance)
    is_stockout = np.random.random() < stockout_chance
    
    sc_penalty = 0
    if is_stockout:
        sc_penalty = 3.0
        st.session_state.customer_trust -= 10
        log_event("Supply Chain Failure! Stockout on critical parts.", "danger")
    
    st.session_state.cash -= holding_cost
    st.session_state.cash -= sc_penalty

    # 5. Revenue Calculation (The Payoff Matrix)
    
    # Stream A: Transactional Clients (Adversarial)
    # We make money when they break (Parts) + New Hardware Sales
    # But Hardware sales decline if Competitor is cheaper and Trust is low
    hardware_demand = 20 * st.session_state.competitor_price * (st.session_state.customer_trust / 50)
    rev_hardware = hardware_demand * 1.0 # $1M per unit
    
    # Parts Revenue (The Trap): Only from Transactional Clients
    # Breakdown count * % Transactional
    parts_demand = num_broken * (st.session_state.contract_mix["Transactional"] / 100)
    rev_parts = parts_demand * 0.2 # $200k per part
    
    if invest_iot > 2.0 and rev_parts < 1.0:
        log_event("Cannibalization! IoT prevented failures, killing Parts revenue.", "money")

    # Stream B: Outcome Clients (Cooperative)
    # We make fixed fees, but pay for repairs
    num_outcome_clients = st.session_state.installed_base * (st.session_state.contract_mix["Outcome"]/100)
    rev_service = num_outcome_clients * 0.05 # Recurring fee
    
    # Cost of Service (We pay for the parts/labor now!)
    cost_service = (num_broken * (st.session_state.contract_mix["Outcome"]/100)) * 0.15
    
    # 6. Total Cash Flow
    gross_profit = (rev_hardware * HARDWARE_MARGIN) + \
                   (rev_parts * PARTS_MARGIN) + \
                   (rev_service) - cost_service
                   
    st.session_state.cash += gross_profit
    
    # Valuation
    current_val = calculate_valuation({"Hardware": rev_hardware, "Parts": rev_parts, "Service": rev_service})
    
    # Logging
    if st.session_state.cash < 5.0:
        log_event("Cash critical! The J-Curve is hitting hard.", "danger")
    
    # Store History
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([{
        "Quarter": st.session_state.quarter,
        "Cash": st.session_state.cash,
        "Valuation": current_val,
        "Rev_Mix": f"{st.session_state.contract_mix['Outcome']}% Outcome"
    }])], ignore_index=True)
    
    st.session_state.quarter += 1
    st.rerun()
