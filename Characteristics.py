from typing import Dict, Any

# === Component characteristic values with embedded successors ===
CHARACTERISTICS2030: Dict[str, Dict[str, Any]] = {
    'KeroseneStorage': {
        'grav_energy_density': 42.0,      # MJ/kg
        'grav_energy_density_fuel': 43.2, # MJ/kg
        'vol_energy_density': 33.91,      # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine'],
        'multiple': False
    },
    'HydrogenStorage': {
        'grav_energy_density': 9.0,       # MJ/kg
        'grav_energy_density_fuel': 120,  # MJ/kg
        'vol_energy_density': 6.4,        # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine', 'FuelCell'],
        'multiple': True
    },
    'Battery': {
        'grav_energy_density': 391*0.0036,  # MJ/kg
        'vol_energy_density': 600*0.0036,   # MJ/L
        'grav_power_density': 0.469,   # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.89,             # -
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'GasTurbine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 3.77,     # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.3,             # -
        'successors': ['GearBox'],
        'multiple': False
    },
    'FuelCell': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 1.1,    # kW/kg      # 0.8
        'vol_power_density': 0.35,     # kW/L
        'efficiency': 0.55,            # -          # 0.4
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'ElectricMachine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 13.2,    # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.97,            # -
        'successors': ['Propeller', 'PowerManagement'],
        'multiple': False
    },
    'GearBox':  {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.96,             # -
        'successors': ['Propeller', 'ElectricMachine'],
        'multiple': True
    },
    'PowerManagement': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 30,    #kW/kg
        'vol_power_density': 70,     #kW/L
        'efficiency': 0.99,  # -
        'successors': ['ElectricMachine'],
        'multiple': True
    },
    'Propeller': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.8,             # -
        'successors': ['Power'],
        'multiple': False
    },
}

CHARACTERISTICS2040: Dict[str, Dict[str, Any]] = {
    'KeroseneStorage': {
        'grav_energy_density': 42.0,      # MJ/kg
        'grav_energy_density_fuel': 43.2, # MJ/kg
        'vol_energy_density': 33.91,      # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine'],
        'multiple': False
    },
    'HydrogenStorage': {
        'grav_energy_density': 14.4,       # MJ/kg
        'grav_energy_density_fuel': 120,  # MJ/kg
        'vol_energy_density': 7.2,        # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine', 'FuelCell'],
        'multiple': True
    },
    'Battery': {
        'grav_energy_density': 510.0*0.0036,  # MJ/kg
        'vol_energy_density': 883.0*0.0036,   # MJ/L
        'grav_power_density': 0.612,   # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.9,             # -
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'GasTurbine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 3.77,     # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.325,             # -
        'successors': ['GearBox'],
        'multiple': False
    },
    'FuelCell': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 1.32,    # kW/kg      # 0.8
        'vol_power_density': 0.42,     # kW/L
        'efficiency': 0.575,            # -          # 0.4
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'ElectricMachine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 20.4,    # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.975,            # -
        'successors': ['Propeller', 'PowerManagement'],
        'multiple': False
    },
    'GearBox':  {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.96,             # -
        'successors': ['Propeller', 'ElectricMachine'],
        'multiple': True
    },
    'PowerManagement': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 36,    #kW/kg
        'vol_power_density': 84,     #kW/L
        'efficiency': 0.99,  # -
        'successors': ['ElectricMachine'],
        'multiple': True
    },
    'Propeller': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.8,             # -
        'successors': ['Power'],
        'multiple': False
    },
}

CHARACTERISTICS2050: Dict[str, Dict[str, Any]] = {
    'KeroseneStorage': {
        'grav_energy_density': 42.0,      # MJ/kg
        'grav_energy_density_fuel': 43.2, # MJ/kg
        'vol_energy_density': 33.91,      # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine'],
        'multiple': False
    },
    'HydrogenStorage': {
        'grav_energy_density': 15.6,       # MJ/kg
        'grav_energy_density_fuel': 120,  # MJ/kg
        'vol_energy_density': 7.8,        # MJ/L
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 1,
        'successors': ['GasTurbine', 'FuelCell'],
        'multiple': True
    },
    'Battery': {
        'grav_energy_density': 611.0*0.0036,  # MJ/kg
        'vol_energy_density': 938.0*0.0036,   # MJ/L
        'grav_power_density': 0.733,   # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.9,             # -
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'GasTurbine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 3.77,     # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.35,             # -
        'successors': ['GearBox'],
        'multiple': False
    },
    'FuelCell': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 1.43,    # kW/kg      # 0.8
        'vol_power_density': 0.46,     # kW/L
        'efficiency': 0.6,            # -          # 0.4
        'successors': ['PowerManagement'],
        'multiple': False
    },
    'ElectricMachine': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 24.3,    # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.98,            # -
        'successors': ['Propeller', 'PowerManagement'],
        'multiple': False
    },
    'GearBox':  {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.96,             # -
        'successors': ['Propeller', 'ElectricMachine'],
        'multiple': True
    },
    'PowerManagement': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 39,    #kW/kg
        'vol_power_density': 91,     #kW/L
        'efficiency': 0.99,  # -
        'successors': ['ElectricMachine'],
        'multiple': True
    },
    'Propeller': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 0,
        'vol_power_density': 0,
        'efficiency': 0.8,             # -
        'successors': ['Power'],
        'multiple': False
    },
}

# Dictionary containing flight data
FLIGHT_CHARACTERISTICS: Dict[int, Dict[str, Any]] = {
    1: {
        'Name': 'Take-off',
        'Power': 2.95*10**6/2,   # W
        'Duration': 30,       # seconds
        'Kerosene_ERF': 0.1134 - 0.0234, #mW/m^2 per kg of fuel used
        #'Hydrogen_ERF': 0.0044,  # mW/m^2 per kg of fuel used
        'EI_CO2': 3.16, # kg/kg
        #'EI_NOx': 16.73, # g/kg
        'Temperature': 288.15, # K
        'Pressure': 101325, #Pa
        'HumidityCorrection': -0.0618368, #Humidity correction
    },
    2: {
        'Name': 'Climb',
        'Power': 2.47 * 10 ** 6/2,  # W
        'Duration': 21*60,  # seconds
        'Kerosene_ERF': 0.1134 - 0.0234, #mW/m^2 per kg of fuel used
        #'Hydrogen_ERF': 0.0035,  # mW/m^2 per kg of fuel used
        'EI_CO2': 3.16,  # kg/kg
        #'EI_NOx': 13.29,  # g/kg
        'Temperature': 264.38,  # K
        'Pressure': 64437.5,  # Pa
        'HumidityCorrection': 0.093639,  # Humidity correction
    },
    3: {
        'Name': 'Cruise',
        'Power': 2.02 * 10 ** 6/2,  # W
        'Duration': 146*60,  # seconds
        'Kerosene_ERF': 0.1134 - 0.0234, #mW/m^2 per kg of fuel used
        #'Hydrogen_ERF': 0.0023,  # mW/m^2 per kg of fuel used
        'EI_CO2': 3.16,  # kg/kg
        #'EI_NOx': 8.765,  # g/kg
        'Temperature': 240.6,  # K
        'Pressure': 39272.1,  # Pa
        'HumidityCorrection': 0.117302,  # Humidity correction
    },
    4: {
        'Name': 'Descent',
        'Power': 0.874 * 10 ** 6/2,  # W
        'Duration': 6*60,  # seconds
        'Kerosene_ERF': 0.1134 - 0.0234, #mW/m^2 per kg of fuel used
        #'Hydrogen_ERF': 0.0017,  # mW/m^2 per kg of fuel used
        'EI_CO2': 3.16,  # kg/kg
        #'EI_NOx': 6.345,  # g/kg
        'Temperature': 264.38,  # K
        'Pressure': 64437.5,  # Pa
        'HumidityCorrection': 0.093639,  # Humidity correction
    },
    5: {
        'Name': 'Completed',
        'Power': 0,  # W
        'Duration': 0,  # seconds
    }
}

DATA = {
    'FuelDensity': 0.785,    #kg/L
    'WingVolumeAvailable': 5000/0.785,  #L
    'EngineCG': 13.1, #-
    'EMCG': 13.1, #-
    'WingCG': 14.7, #-
    'FuselageCrossSection': 5.19, #m^2
    'FuselageTopArea': 4.1, #m^2
    'FuselageLowerArea': 1.09, #m^2
    'PayloadStart': 8.494, #m
    'AftMostPoint': 23.7, #m
    'ForwardFrontLower': 5.7, #m
    'AftFrontLower': 11.0, #m
    'FrontLowerVolume': 1.09*(11-5.7)*1000, #L
    'ForwardBackLower': 18, #m
    'AftBackLower': 21, #m
    'BackLowerVolume': 1.09*(21-18)*1000, #L
    'OEW-PropSystemMass': 12543, #kg
    'OEW-PropSystemArm': 13.91, #kg
}