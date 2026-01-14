import streamlit as st

st.set_page_config(page_title="Mining mode cutoff calculator", layout="centered")

st.title("Bitcoin mining mode cut-off calculator")

st.markdown(
"""
This app calculates **electricity price cut-off points** (øre/kWh) for switching
between mining modes, based on marginal profitability.
"""
)

# -----------------------------
# Inputs: Miner modes
# -----------------------------
st.header("Miner modes")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Eco")
    eco_power = st.number_input("Power (W)", value=1200.0)
    eco_hash = st.number_input("Hashrate (TH/s)", value=40.0)

with col2:
    st.subheader("Standard")
    std_power = st.number_input("Power (W) ", value=2000.0)
    std_hash = st.number_input("Hashrate (TH/s) ", value=70.0)

with col3:
    st.subheader("Super")
    sup_power = st.number_input("Power (W)", value=3000.0)
    sup_hash = st.number_input("Hashrate (TH/s)", value=100.0)

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
BLOCKS_PER_DAY = 144

# Revenue per TH per hour
btc_per_day = BLOCKS_PER_DAY * block_reward
btc_per_day_per_th = btc_per_day / network_hashrate
nok_per_day_per_th = btc_per_day_per_th * btc_price
nok_per_hour_per_th = nok_per_day_per_th / 24

# Efficiency per mode
def th_per_kwh(hashrate, power_w):
    return hashrate / (power_w / 1000)

def j_per_th(hashrate, power_w):
    return (power_w / hashrate) * 3600

eco_eff = th_per_kwh(eco_hash, eco_power)
std_eff = th_per_kwh(std_hash, std_power)
sup_eff = th_per_kwh(sup_hash, sup_power)

eco_jth = j_per_th(eco_hash, eco_power)
std_jth = j_per_th(std_hash, std_power)
sup_jth = j_per_th(sup_hash, sup_power)

# Incremental efficiencies
delta_eff_eco_std = (std_hash - eco_hash) / ((std_power - eco_power) / 1000)
delta_eff_std_sup = (sup_hash - std_hash) / ((sup_power - std_power) / 1000)

# Cut-off prices (øre/kWh)
eco_cutoff = 100 * nok_per_hour_per_th * eco_eff
eco_std_cutoff = 100 * nok_per_hour_per_th * delta_eff_eco_std
std_sup_cutoff = 100 * nok_per_hour_per_th * delta_eff_std_sup

# -----------------------------
# Outputs
# -----------------------------
st.header("Results")

st.subheader("Revenue baseline")
st.write(f"**Revenue:** {nok_per_hour_per_th:.8f} NOK / TH / hour")

st.subheader("Mode efficiencies")
st.table({
    "TH/kWh": {
        "Eco": round(eco_eff, 2),
        "Standard": round(std_eff, 2),
        "Super": round(sup_eff, 2),
    },
    "J/TH": {
        "Eco": round(eco_jth, 0),
        "Standard": round(std_jth, 0),
        "Super": round(sup_jth, 0),
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
