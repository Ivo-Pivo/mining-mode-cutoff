import streamlit as st

st.set_page_config(page_title="Mining mode cutoff calculator", layout="centered")

st.title("Bitcoin mining mode cut-off calculator")

st.markdown(
"""
This app calculates **electricity price cut-off points** (øre/kWh) for switching
between mining modes, based on marginal profitability. It's developed as a collaborative effort on forum.bitcoinsnakk.no
"""
)

# -----------------------------
# Inputs: Miner modes
# -----------------------------
st.header("Miner modes")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Eco")
    eco_power = st.number_input("Power (W)", value=830.0)
    eco_hash = st.number_input("Hashrate (TH/s)", value=53.0)

with col2:
    st.subheader("Standard")
    std_power = st.number_input("Power (W) ", value=1381.0)
    std_hash = st.number_input("Hashrate (TH/s) ", value=82.0)

with col3:
    st.subheader("Super")
    sup_power = st.number_input("Power (W)", value=1674.0)
    sup_hash = st.number_input("Hashrate (TH/s)", value=90.0)

# -----------------------------
# Inputs: Network & market
# -----------------------------
st.header("Network & market parameters")

network_hashrate = st.number_input(
    "Network total hashrate (TH/s)",
    value=1_040_000_000.0,
    format="%.0f",
)

block_reward = st.number_input(
    "Block reward (BTC per 10 min)",
    value=3.14,
)

btc_price = st.number_input(
    "BTC price (NOK/BTC)",
    value=933_000.0,
    format="%.0f",
)

# -----------------------------
# Calculations
# -----------------------------

#HC = 1/R
th_per_nok = network_hashrate * 600 / (block_reward * btc_price)

# Efficiency per mode
def th_per_kwh(hashrate, power_w):
    return hashrate * 3600 / (power_w/1000)

def j_per_th(hashrate, power_w):
    return (power_w / hashrate)

eco_eff = th_per_kwh(eco_hash, eco_power)
std_eff = th_per_kwh(std_hash, std_power)
sup_eff = th_per_kwh(sup_hash, sup_power)

# Incremental efficiencies
delta_eff_eco_std = th_per_kwh((std_hash - eco_hash), (std_power - eco_power))
delta_eff_std_sup = th_per_kwh((sup_hash - std_hash), (sup_power - std_power))

eco_jth = j_per_th(eco_hash, eco_power)
std_jth = j_per_th(std_hash, std_power)
sup_jth = j_per_th(sup_hash, sup_power)

# Cut-off prices (øre/kWh)
eco_cutoff = 100 * eco_eff / th_per_nok
#eco_std_cutoff = 100 * nok_per_hour_per_th * delta_eff_eco_std
eco_std_cutoff = 100 * delta_eff_eco_std / th_per_nok
#std_sup_cutoff = 100 * nok_per_hour_per_th * delta_eff_std_sup
std_sup_cutoff = 100 * delta_eff_std_sup / th_per_nok

# -----------------------------
# Outputs
# -----------------------------
st.header("Results")

st.subheader("Mode efficiencies")
st.table({
    "TH/kWh": {
        "Eco": round(eco_eff, -2),
        "Standard": round(std_eff, -2),
        "Super": round(sup_eff, -2),
    },
    "J/TH": {
        "Eco": round(eco_jth, 1),
        "Standard": round(std_jth, 1),
        "Super": round(sup_jth, 1),
    }
})

st.subheader("Electricity price cut-off points")

st.metric(
    "Eco break-even price",
    f"{eco_cutoff:.2f} øre/kWh",
)

st.metric(
    "Switch Eco → Standard below",
    f"{eco_std_cutoff:.2f} øre/kWh",
)

st.metric(
    "Switch Standard → Super below",
    f"{std_sup_cutoff:.2f} øre/kWh",
)

st.caption(
    "Cut-off points are based on marginal profitability per hour."
)

# -----------------------------
# Profit calculation at user-specified electricity price
# -----------------------------
st.header("Profit simulation")

elec_price = st.slider(
    "Electricity price (øre/kWh)", 
    min_value=0, 
    max_value=200, 
    value=100,
)

# Convert øre/kWh to NOK/kWh
elec_price_nok = elec_price / 100

# Profit per hour = (hashrate * 3600 (TH/kWh) / th_per_nok) - (electricity cost per kWh * kWh / h)
def profit_per_hour(th_per_nok, power_w, elec_price_nok, hashrate):
        power_kwh_per_hour = power_w / 1000
        return (hashrate * 3600 / th_per_nok) - (elec_price_nok * power_w * 0.001)

# Or simpler: Revenue per hour per kWh = eff_th_per_kwh / th_per_nok
# Profit = revenue per hour - electricity cost per hour
eco_profit = profit_per_hour(th_per_nok, eco_power, elec_price_nok, eco_hash)
std_profit = profit_per_hour(th_per_nok, std_power, elec_price_nok, std_hash)
sup_profit = profit_per_hour(th_per_nok, sup_power, elec_price_nok, sup_hash)

st.metric("Eco profit per hour", f"{eco_profit:.2f} NOK")
st.metric("Standard profit per hour", f"{std_profit:.2f} NOK")
st.metric("Super profit per hour", f"{sup_profit:.2f} NOK")
