import numpy as np
# Function to name each powerpath by its starting component and add an integer behind it
def x_vector_names(powerpaths):
    x_names = []
    counts = {}
    for powerpath in powerpaths:
        try:
            if (powerpath[1].name == 'GearBox' or powerpath[1].name == 'ElectricMachine')  and powerpath[2].name == 'Propeller':
                base = 'Propeller'
            elif powerpath[1].name == 'Propeller':
                base = 'Power'
            else:
                base = powerpath[1].name
        except:
            pass
        n = counts.get(base, 1)
        x_names.append(f"{base}{n}")
        counts[base] = n + 1
    return x_names

# Function to create a list that includes the input and output component of each electrical machine and their powerpath identifiers
def em_connections(powerpaths):
    connections = []
    # Loop through all powerpaths
    for id, powerpath in enumerate(powerpaths):
        # Find the powerpath where the power flows from the electrical machine
        if powerpath[1].name == 'ElectricMachine':
            em = []
            # Append the electric machine, the connected component, and the powerpath identifier
            em.append(powerpath[1])
            em.append(powerpath[2])
            em.append(id)
            # Search for the input component to the electric machine
            for input_id, input_pp in enumerate(powerpaths):
                try:
                    if input_pp[2].id == powerpath[1].id:
                        # Append the powerpath id and the input component to the list
                        em.insert(0, input_pp[1])
                        em.insert(0, input_id)
                except:
                    pass
            # Append each set to the whole list
            connections.append(em)
    return connections

# Function to create two lists where the input and outputs paths of each powermanagement system are stored
def pm_connections(powerpaths):
    outer = []
    ids = []
    # Loop through all powerpaths
    for id, powerpath in enumerate(powerpaths):
        inputs = []
        outputs = []
        try:
            # Find each powermanagement system
            if powerpath[2].name == 'PowerManagement' and powerpath[2].id not in ids:
                ids.append(powerpath[2].id)
                for powerpath_id, component in enumerate(powerpaths):
                    try:
                        # Append the powerpath identifier depending on if it is an input or output path to the powermanagement system
                        if component[2].id == powerpath[2].id:
                            inputs.append(powerpath_id)
                        elif component[1].id == powerpath[2].id:
                            outputs.append(powerpath_id)
                    except:
                        pass
                outer.append([inputs, outputs])
        except:
            pass
    return outer

# Function to randomly sample component characteristics in a normal distribution
def randomize_characteristics(base_chars: dict, sd_frac: float = 0.1):
    """
    Return a randomly sampled dictionary based on the mean of the initial value.
    Efficiency is clipped to [0,1], others to ≥0.
    """
    rng = np.random.default_rng()
    out = copy.deepcopy(base_chars)

    KEYS = (
        "grav_energy_density", "vol_energy_density",
        "grav_power_density", "vol_power_density",
        "efficiency",
    )

    for comp, params in out.items():
        for k in KEYS:
            mu = float(params[k])
            if mu == 0.0:
                continue
            val = float(rng.normal(mu, abs(mu) * sd_frac))
            if k == "efficiency":
                if comp == 'KeroseneStorage' or comp == 'HydrogenStorage':
                    val = 1
                else:
                    val = float(np.clip(val, 0.01, 1.0))
            else:
                val = max(val, 0.01)
            params[k] = val
    return out

def nox_emmisions(Throttle_setting, flight_phase):
    from Characteristics import FLIGHT_CHARACTERISTICS
    OPR = 14
    fuel_flow = np.exp(0.04459*Throttle_setting-4.098)
    P = FLIGHT_CHARACTERISTICS[flight_phase]['Pressure']
    T = FLIGHT_CHARACTERISTICS[flight_phase]['Temperature']
    HC = FLIGHT_CHARACTERISTICS[flight_phase]['HumidityCorrection']
    if round(Throttle_setting,0) <= 25:
        a = 0.1605
        b = 0.2412
        c = -0.00165
        d = -8.818
        e = 37.14
        f = -0.2268
        EI_NOx = a + b*OPR + c*OPR**2 + d*fuel_flow + e*fuel_flow**2 + f*OPR*fuel_flow
        EI_NOx_cor = EI_NOx * ((P/101325)**0.51 / (T/288.15)**1.65 ) * np.exp(HC)
    elif round(Throttle_setting,0) <=57.5:
        a = 0.3699
        b = 0.547
        c = -0.007445
        d = -6.914
        e = 6.782
        f = 0.1138
        EI_NOx = a + b * OPR + c * OPR ** 2 + d * fuel_flow + e * fuel_flow ** 2 + f * OPR * fuel_flow
        EI_NOx_cor = EI_NOx * ((P / 101325) ** 0.51 / (T / 288.15) ** 1.65) * np.exp(HC)
    elif round(Throttle_setting,0) <=92.5:
        a = 7.194
        b = 0.5609
        c = -0.01059
        d = -3.223
        e = 0.2889
        f = 0.2591
        EI_NOx = a + b * OPR + c * OPR ** 2 + d * fuel_flow + e * fuel_flow ** 2 + f * OPR * fuel_flow
        EI_NOx_cor = EI_NOx * ((P / 101325) ** 0.51 / (T / 288.15) ** 1.65) * np.exp(HC)
    elif round(Throttle_setting,0) <=100:
        a = 13.37
        b = 0.09144
        c = 0.00003617
        d = -1.075
        e = -0.6473
        f = 0.2994
        EI_NOx = a + b * OPR + c * OPR ** 2 + d * fuel_flow + e * fuel_flow ** 2 + f * OPR * fuel_flow
        EI_NOx_cor = EI_NOx * ((P / 101325) ** 0.51 / (T / 288.15) ** 1.65) * np.exp(HC)
    else:
        print(Throttle_setting)
        raise ValueError('Throttle setting > 100%')
    return EI_NOx_cor