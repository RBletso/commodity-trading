import numpy as np
import pandas as pd

# ----------------------------------------
# CORE HELPER FUNCTIONS
# ----------------------------------------

def fuel_cost_per_mwh(fuel_price, heat_rate):
    """
    Convert a fuel price (gas or coal) into cost per MWh of electricity.
    
    fuel_price: €/MWh_th
    heat_rate: MMBtu/MWh_el (higher = worse efficiency)
    """
    return fuel_price * heat_rate


def carbon_cost_per_mwh(carbon_price, emission_factor):
    """
    Convert carbon allowance price into cost per MWh of electricity.
    
    carbon_price: €/tCO2
    emission_factor: tonnes CO2 per MWh_el
    """
    return carbon_price * emission_factor


# ----------------------------------------
# SPARK SPREAD (GAS)
# ----------------------------------------

def spark_spread(power_price, gas_price, heat_rate, carbon_price=None, emission_factor=None):
    """
    Dirty or Clean Spark Spread depending on whether carbon inputs are provided.
    
    power_price: €/MWh_el
    gas_price: €/MWh_th (TTF is already in this unit)
    heat_rate: MMBtu/MWh_el
    carbon_price: €/tCO2 (optional)
    emission_factor: tCO2/MWh_el (optional)
    """

    fuel_cost = fuel_cost_per_mwh(gas_price, heat_rate)

    if carbon_price is None:
        return power_price - fuel_cost

    carbon_cost = carbon_cost_per_mwh(carbon_price, emission_factor)
    return power_price - fuel_cost - carbon_cost


def clean_spark_spread(power_price, gas_price, heat_rate, carbon_price, emission_factor):
    """
    Clean Spark Spread (always includes carbon).
    """
    return spark_spread(power_price, gas_price, heat_rate,
                        carbon_price=carbon_price,
                        emission_factor=emission_factor)


# ----------------------------------------
# DARK SPREAD (COAL)
# ----------------------------------------

DEFAULT_COAL_EMISSION_FACTOR = 0.9   # tonnes CO2 per MWh_el (typical coal plant)


def dark_spread(power_price, coal_price, coal_heat_rate, carbon_price=None, emission_factor=DEFAULT_COAL_EMISSION_FACTOR):
    """
    Dirty or Clean Dark Spread.
    
    coal_price: €/MWh_th (synthetic or real coal input)
    coal_heat_rate: MMBtu/MWh_el (coal less efficient: ~9–12)
    carbon_price: €/tCO2
    emission_factor: tCO2/MWh_el (coal ~0.9)
    """

    fuel_cost = fuel_cost_per_mwh(coal_price, coal_heat_rate)

    if carbon_price is None:
        return power_price - fuel_cost

    carbon_cost = carbon_cost_per_mwh(carbon_price, emission_factor)
    return power_price - fuel_cost - carbon_cost


def clean_dark_spread(power_price, coal_price, coal_heat_rate, carbon_price, emission_factor=DEFAULT_COAL_EMISSION_FACTOR):
    """
    Clean Dark Spread (coal with carbon cost).
    """
    return dark_spread(power_price, coal_price, coal_heat_rate,
                       carbon_price=carbon_price,
                       emission_factor=emission_factor)


# ----------------------------------------
# DATAFRAME HELPERS FOR CURVES
# ----------------------------------------

def add_spark_columns(df, heat_rate, carbon_price=None, emission_factor=None):
    """
    Add spark spread columns to a DataFrame with:
    df['Gas']
    df['Power']

    Produces:
        Fuel_Cost
        Carbon_Cost
        Spark
        Clean_Spark
    """
    df["Fuel_Cost"] = df["Gas"] * heat_rate

    if carbon_price is not None:
        df["Carbon_Cost"] = carbon_cost_per_mwh(carbon_price, emission_factor)
    else:
        df["Carbon_Cost"] = 0

    df["Spark"] = df["Power"] - df["Fuel_Cost"] - df["Carbon_Cost"]

    return df


def add_dark_columns(df, coal_heat_rate, carbon_price=None, emission_factor=DEFAULT_COAL_EMISSION_FACTOR):
    """
    Add dark spread columns to a DataFrame with:
    df['Coal']
    df['Power']

    Produces:
        Coal_Fuel_Cost
        Coal_Carbon_Cost
        Dark
        Clean_Dark
    """

    df["Coal_Fuel_Cost"] = df["Coal"] * coal_heat_rate

    if carbon_price is not None:
        df["Coal_Carbon_Cost"] = carbon_cost_per_mwh(carbon_price, emission_factor)
    else:
        df["Coal_Carbon_Cost"] = 0

    df["Dark"] = df["Power"] - df["Coal_Fuel_Cost"] - df["Coal_Carbon_Cost"]

    return df