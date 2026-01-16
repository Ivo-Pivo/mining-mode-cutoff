import streamlit as st

st.set_page_config(page_title="Mining mode cutoff calculator", layout="centered")

st.title("Bitcoin mining mode cut-off calculator")

st.markdown(
"""
This app calculates **electricity price cut-off points** (Norwegian øre/kWh) for switching
between mining modes, based on marginal profitability. The default values are for an Avalon Q miner, 
and the network/market default parameters are roughly valid as of 2026-01-14 and not automatically updated.

Developed as a collaborative effort on forum.bitcoinsnakk.no
"""
)

# -----------------------------
# Inputs: Miner modes
# -----------------------------
st.header("Miner modes")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Eco")
    eco_power = st.number_input("Power (W)", value=830, step=5, format="%d")
    eco_hash = st.number_input("Hashrate (TH/s)", value=53, step=1, format="%d")

with col2:
    st.subheader("Standard")
    std_power = st.number_input("Power (W)", value=1380, step=5, format="%d")
    std_hash = st.number_input("Hashrate (TH/s)", value=82, step=1, format="%d")

with col3:
    st.subheader("Super")
    sup_power = st.number_input("Power (W)", value=1675, step=5, format="%d")
    sup_hash = st.number_input("Hashrate (TH/s)", value=90, step=1, format="%d")

# -----------------------------
# Inputs: Network & market
# -----------------------------
st.header("Network & market parameters")

st.markdown(
"""
For calculating profits. Assumes mining in a pool with no fees.
"""
)

network_hashrate = st.number_input(
    "Network total hashrate (TH/s)",
    value=1_020_000_000.0,
    format="%.0f",
)

block_reward = st.number_input(
    "Block reward (BTC per 10 min)",
    value=3.14,
)

btc_price = st.number_input(
    "BTC price (NOK/BTC)",
    value=956_000.0,
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

eco_jth = j_per_th(eco_hash, eco_power)
std_jth = j_per_th(std_hash, std_power)
sup_jth = j_per_th(sup_hash, sup_power)

# Incremental efficiencies
delta_eff_eco_std = th_per_kwh((std_hash - eco_hash), (std_power - eco_power))
delta_eff_std_sup = th_per_kwh((sup_hash - std_hash), (sup_power - std_power))

# Cut-off prices (øre/kWh)
eco_cutoff = 100 * eco_eff / th_per_nok
eco_std_cutoff = 100 * delta_eff_eco_std / th_per_nok
std_sup_cutoff = 100 * delta_eff_std_sup / th_per_nok

# -----------------------------
# Outputs
# -----------------------------
st.header("Results")

st.subheader("Mode efficiencies")
st.table({
    "TH/kWh": {
        "Eco": f"{round(eco_eff,-2):,.0f}",
        "Standard": f"{round(std_eff,-2):,.0f}",
        "Super": f"{round(sup_eff,-2):,.0f}",
    },
    "J/TH": {
        "Eco": f"{round(eco_jth, 1):,.1f}",
        "Standard": f"{round(std_jth, 1):,.1f}",
        "Super": f"{round(sup_jth, 1):,.1f}",
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

slider_max = int(round(eco_cutoff * 1.2))
slider_value = int(round(slider_max * 0.5))

elec_price = st.slider(
    "Electricity price (øre/kWh)", 
    min_value=0, 
    max_value=slider_max, 
    value=slider_value,
)

# Convert øre/kWh to NOK/kWh
elec_price_nok = elec_price / 100

# Profit per hour = hashing revenue - electricity cost [NOK/h]
# Hashing revenue = hashrate (TH/h) / th_per_nok [NOK/h]
def profit_per_hour(th_per_nok, power_w, elec_price_nok, hashrate):
        return (hashrate * 3600 / th_per_nok) - (elec_price_nok * power_w * 0.001)

# -----------------------------
# Profit plot
# -----------------------------

import numpy as np
import matplotlib.pyplot as plt
# Price range for plotting (øre/kWh)
price_range = np.linspace(0, slider_max, 200)
price_range_nok = price_range / 100

eco_profit_curve = 100 * profit_per_hour(th_per_nok, eco_power, price_range_nok, eco_hash)
std_profit_curve = 100 * profit_per_hour(th_per_nok, std_power, price_range_nok, std_hash)
sup_profit_curve = 100 * profit_per_hour(th_per_nok, sup_power, price_range_nok, sup_hash)

st.subheader("Profit vs electricity price")

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(price_range, eco_profit_curve, label="Eco", linewidth=2)
ax.plot(price_range, std_profit_curve, label="Standard", linewidth=2)
ax.plot(price_range, sup_profit_curve, label="Super", linewidth=2)


# Vertical marker line for current electricity price
ax.axvline(
    elec_price,
    linestyle="--",
    linewidth=2,
    color="black",
    label=f"Selected price ({elec_price:.0f} øre/kWh)",
)

# Horizontal break-even line
ax.axhline(
    0,
    linestyle="--",
    linewidth=2,
    color="red",
    alpha=0.7,
    label="Break-even (0 NOK/h)",
)

# Trim bottom off
min_profit = eco_profit_curve.min()
ax.set_ylim(bottom=min(0, min_profit))

ax.set_xlabel("Electricity price (øre/kWh)")
ax.set_ylabel("Profit (øre/hour)")
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# -----------------------------
# Mode profit per hour
# -----------------------------


eco_profit = profit_per_hour(th_per_nok, eco_power, elec_price_nok, eco_hash)
std_profit = profit_per_hour(th_per_nok, std_power, elec_price_nok, std_hash)
sup_profit = profit_per_hour(th_per_nok, sup_power, elec_price_nok, sup_hash)

eco_year_profit = eco_profit * 24 * 365
std_year_profit = std_profit * 24 * 365
sup_year_profit = sup_profit * 24 * 365

st.metric("Eco profit", f"{eco_profit:.2f} NOK/h, {eco_year_profit:.0f} NOK/year")
st.metric("Standard profit", f"{std_profit:.2f} NOK/h, {std_year_profit:.0f} NOK/year")
st.metric("Super profit", f"{sup_profit:.2f} NOK/h, {sup_year_profit:.0f} NOK/year")

#cut_off_efficiency
if elec_price_nok > 0:
    cut_off_efficiency = 3600000 / (elec_price_nok * th_per_nok)
    efficiency_label = f"{cut_off_efficiency:.1f} J/TH"
else:
    cut_off_efficiency = None
    efficiency_label = "∞ J/TH"

st.metric("Efficiency breakeven point", efficiency_label)

# -----------------------------
# Payback time, free electricity
# -----------------------------

st.subheader("Payback time - Free electricity")

purchase_price = st.number_input("Purchase price (NOK)", value=19100, step=100, format="%d")

eco_rev = profit_per_hour(th_per_nok, eco_power, 0, eco_hash)
std_rev = profit_per_hour(th_per_nok, std_power, 0, std_hash)
sup_rev = profit_per_hour(th_per_nok, sup_power, 0, sup_hash)

eco_PB = purchase_price / (eco_rev * 24 * 365)
std_PB = purchase_price / (std_rev * 24 * 365)
sup_PB = purchase_price / (sup_rev * 24 * 365)

st.metric("Eco payback time", f"{eco_PB:.2f} years")
st.metric("Standard payback time", f"{std_PB:.2f} years")
st.metric("Super payback time", f"{sup_PB:.2f} years")
