from Powertrain_env import Powertrain
from Characteristics import DATA, FLIGHT_CHARACTERISTICS
from Helpers import *

import numpy as np
import random
import math
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import torch
import gym
from gym.spaces import Box, Dict as SpaceDict, MultiBinary
from gym.utils import seeding
from stable_baselines3.common.utils import set_random_seed

# Define maximum size of the matrix and number of control parameters
max_matrix_size = 19
max_action_size = 6

# Seeds for training model
def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    set_random_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

class FlightSimulation(gym.Env):
    def __init__(self, CHARACTERISTICS, CARGO, FP2050):
        # Initialize action space
        self.action_space = Box(low=0, high=1, shape=(max_action_size,))

        # Initialize observation space
        self.observation_space = SpaceDict({
            "M": Box(low=-1, high=1, shape=(max_matrix_size, max_matrix_size), dtype=np.float32),
            "mask": MultiBinary((max_matrix_size, max_matrix_size)),
            "act_mask": MultiBinary(max_action_size),
            "flight_phase": Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32),
            "violation": Box(low=0.0, high=1, shape=(max_action_size,), dtype=np.float32),
        })

        self.CHARACTERISTICS = CHARACTERISTICS
        self.seed_initialised = False
        self.CARGO = CARGO
        self.FP2050 = FP2050

        self.max_power = FLIGHT_CHARACTERISTICS[1]['Power']

        self.flight_duration = 0
        for i in FLIGHT_CHARACTERISTICS:
            self.flight_duration += FLIGHT_CHARACTERISTICS[i]['Duration']

    def to_numeric(self, A):
        """ Function to turn an object into a numerical system. """
        return np.asarray(A, dtype=np.float32)

    def _obs(self):
        """" Function to fit powertrain matrix and action space in a predefined size """

        snap = self.to_numeric(self.A_obj)                 # numeric snapshot of current object state
        n, m = snap.shape
        if n > max_matrix_size or m > max_matrix_size:
            raise ValueError(f"Matrix {n}x{m} exceeds padded obs size {max_matrix_size}x{max_matrix_size}.")

        # Create matrix of maximum size and fit powertrain matrix in it
        M = np.zeros((max_matrix_size, max_matrix_size), dtype=np.float32)
        M[:n, :m] = snap

        # Fill the powertrain matrix with ones to tell the algorithm which cells are relevant
        mask = np.zeros((max_matrix_size, max_matrix_size), dtype=np.int8)
        mask[:n, :m] = 1

        # Fill the used action space with ones
        act_mask = np.zeros(self.action_space.shape[0], dtype=np.int8)
        act_mask[:self.n_active_ctrl] = 1

        flight_phase = np.array([self.flight_phase / 5, FLIGHT_CHARACTERISTICS[self.flight_phase]['Power'] / self.max_power, FLIGHT_CHARACTERISTICS[self.flight_phase]['Duration'] / self.flight_duration])

        # Create empty array that is later filled by how much the raw action differed from the adjusted action
        violation = np.zeros(self.action_space.shape[0], dtype=np.float32)

        obs = {"M": M, "mask": mask, "act_mask": act_mask, "flight_phase": flight_phase, "violation": violation}

        return obs

    def step(self, action):
        """ Step function to loop through every flight phase with an action """
        # Get the power requirement and duration depending on the flight phase
        power, duration = FLIGHT_CHARACTERISTICS[self.flight_phase]['Power'], FLIGHT_CHARACTERISTICS[self.flight_phase]['Duration']

        # Define the control parameters in the matrix
        for i in range(0, len(self.pt.supply_param)):
            self.pt.supply_param.set(i, action[i])
        for i in range(0, len(self.pt.shaft_param)):
            self.pt.shaft_param.set(i, action[i + len(self.pt.supply_param)])

        # Convert the object to a numerical matrix
        A = self.to_numeric(self.A_obj)

        # Ensure b matches A and is zeroed
        if self.b.shape[0] != A.shape[0]:
            self.b = np.zeros(A.shape[0], dtype=np.float32)
        else:
            self.b.fill(0.0)

        # Set the required propulsive power
        self.b[-1] = power

        # Calculation of the powerpath values
        x = np.linalg.solve(A, self.b)
        x = np.where(np.abs(x) < 1, 0.0, x)

        # If a powerpath value is zero, then certain logic has to be applied to reorder the sequence
        self.powerpaths_switched_input = []
        self.powerpaths_switched_output = []

        while (x<0).any():
            # Check if the battery is accidentally charging
            battery_power = x[self.ENERGY_SOURCE_DATA['Battery']['x_position']]
            if len(battery_power) == 0:
                pass
            elif battery_power[0] < 0:
                raise ValueError("Battery is charging")
            # Check if energy is being harvested
            harvesting_paths = []
            for powerpath_id, name in enumerate(self.x_names):
                if name[:-1] == 'Power' and x[powerpath_id] < 0:
                    np.set_printoptions(precision=16, suppress=True)
                    # Calculate the power ratio's of the shafts that are fixed by the supply ratio's
                    shaft_ratios = []
                    for powerpath in self.pt.defined_shafts_powerpaths:
                        shaft_ratios.append(x[powerpath] / power * self.CHARACTERISTICS['Propeller']['efficiency'])
                    # If the sum of the fixed ratio's and the set ratio's is larger than 1, the set ratio's must be reduced
                    while round(sum(shaft_ratios) + sum(action[-len(self.pt.shaft_param):]), 6) > 1:
                        # Calculate the maximum sum of the set ratio's and the value by which the ratio's must be divided
                        max_sum_shaft_param = 1 - sum(shaft_ratios)
                        division = sum(action[len(self.pt.supply_param): len(self.pt.supply_param) + len(
                            self.pt.shaft_param)]) / max_sum_shaft_param
                        # print('Energy Harvesting Step')
                        # self.pt.describe()
                        # print(action, self.actions)
                        # print(sum(shaft_ratios), sum(action[-len(self.pt.shaft_param):]))
                        # print(max_sum_shaft_param, division)
                        # Set the new ratio's
                        action[len(self.pt.supply_param): len(self.pt.supply_param) + len(
                            self.pt.shaft_param)] = [param / division for param in action[
                                                                                       len(self.pt.supply_param): len(
                                                                                           self.pt.supply_param) + len(
                                                                                           self.pt.shaft_param)]]
                        for i in range(0, len(self.pt.shaft_param)):
                            self.pt.shaft_param.set(i, action[i + len(self.pt.supply_param)])
                        A = self.to_numeric(self.A_obj)
                        # Recalculate x
                        x = np.linalg.solve(A, self.b)
                        x = np.where(np.abs(x) < 1, 0.0, x)
                        # Recalculate the fixed shaft ratio's
                        shaft_ratios = []
                        for powerpath in self.pt.defined_shafts_powerpaths:
                            shaft_ratios.append(x[powerpath] / power * self.CHARACTERISTICS['Propeller']['efficiency'])
                    #raise ValueError("Energy Harvesting")
            x = np.where(np.abs(x) < 1, 0.0, x)
            # Loop over all powerpaths in x
            for column1, powerpath in enumerate(x):
                if powerpath < 0:
                    # If two powerpaths are connected in one branch and both negative, their input and output order must be switched.
                    # In the case, one of the negative powerpaths should contain a value below 0 (the component efficiency).
                    # This row must be found and the values between the two powerpaths/columns in this row should be swapped
                    ### as well as the remaining two values in this column.

                    # If more than three powerpaths are negative this process can be repeated until only one path is negative
                    #### in this case, the column can be simply multiplied by -1 to reverse the order.

                    # Find the row of the component where the powerpath is smaller than zero (row with the efficiency)
                    overlapping_row = np.flatnonzero(A[0:len(self.components), column1] < 0)

                    # Find the powerpaths connected to the negative powerpath
                    column2 = np.flatnonzero(A[overlapping_row] != 0)
                    column2 = column2[column2 != column1]

                    # List of powerpaths with negative powers, excluding the harvesting paths
                    neg_power = [i for i, x in enumerate(x) if x < 0]
                    neg_power = list(set(neg_power) - set(harvesting_paths))
                    # If only one second column (powerpath) is found, then the direction of two powerpaths must be switched
                    # This can only be true for GearBox => ElectricalMachine => PowerManagement
                    if len(column2) == 1:
                        # Find the rows in both columns that have non-zero values
                        nonzero_rows_column1 = np.where(~np.isclose(A[:, column1], 0.0, atol=1e-9))[0]
                        nonzero_rows_column2 = np.where(~np.isclose(A[:, column2], 0.0, atol=1e-9))[0]

                        # Find the overlapping rows
                        value_overlapping_row_column1 = A[overlapping_row, column1]
                        value_overlapping_row_column2 = A[overlapping_row, column2]

                        # Find the unique rows
                        unique_row_column1 = list(set(nonzero_rows_column1) - set(nonzero_rows_column2))
                        unique_row_column2 = list(set(nonzero_rows_column2) - set(nonzero_rows_column1))
                        value_unique_row_column1 = A[unique_row_column1, column1]
                        value_unique_row_column2 = A[unique_row_column2, column2]

                        pm_check = np.isclose(value_unique_row_column2[0], -self.CHARACTERISTICS['PowerManagement']['efficiency'], atol=1e-9)
                        em_check = np.isclose(value_overlapping_row_column1[0], -self.CHARACTERISTICS['ElectricMachine']['efficiency'], atol=1e-9)
                        if pm_check == False or em_check == False:
                            self.pt.describe()
                            print(A)
                            print(self.powerpaths)
                            print(x)
                            raise ValueError('Switching not consistent')
                        else:
                            value_unique_row_column2[0] = -self.CHARACTERISTICS['GearBox']['efficiency']

                        #Switch the values
                        A[overlapping_row, column1] = value_overlapping_row_column2
                        A[overlapping_row, column2] = value_overlapping_row_column1
                        A[unique_row_column1, column1] = value_unique_row_column2
                        A[unique_row_column2, column2] = value_unique_row_column1

                        # If second powerpath flows into a powermangement system, it is registered
                        if self.powerpaths[column2[0]][2].name == 'PowerManagement':
                            self.powerpaths_switched_input.append(column2[0])

                        # If three powerpaths are negative, the last powerpath can be multiplied by -1 after the order of the first two is switched
                        ### This will only be the powerpath between two powermanagement systems
                        if len(neg_power) == 3:
                            final_column = list(set(neg_power) - set([column1, column2[0]]))
                            A[:, final_column] *= -1
                            A[:, final_column] = np.where(A[:, final_column] == 0, 0, A[:, final_column])

                            # If the switched powerpath contained a powermanagement system, it is registered if it is an input, output or both
                            if self.powerpaths[final_column[0]][2].name == 'PowerManagement':
                                self.powerpaths_switched_input.append(final_column[0])
                            if self.powerpaths[final_column[0]][1].name == 'PowerManagement':
                                self.powerpaths_switched_output.append(final_column[0])

                    # If multiple connected powerpaths to the negative powerpath are found, multiply the powerpath by -1
                    ### This will only be the powerpath between two powermanagement systems
                    else:
                        A[:, column1] *= -1
                        A[:, column1] = np.where(A[:, column1] == 0, 0, A[:, column1])

                        # If the switched powerpath contained a powermanagement system, it is registered if it is an input, output or both
                        if self.powerpaths[column1][2].name == 'PowerManagement':
                            self.powerpaths_switched_input.append(column1)
                        if self.powerpaths[column1][1].name == 'PowerManagement':
                            self.powerpaths_switched_output.append(column1)
                    break
            x = np.linalg.solve(A, self.b)
            x = np.where(np.abs(x) < 1, 0.0, x)

        # Keep track of the maximum value that has been recorded in each powerpath
        if self.x_max is None:
            self.x_max = x.copy()
        else:
            self.x_max = np.fmax(self.x_max, x)

        self.x.append(x)

        # Calculate the sum of the input powerpaths to the powermanagement system
        self._pms(x)

        # Append the energy requirement of each fuel
        for energy_source in self.ENERGY_SOURCE_DATA:
            for x_position in self.ENERGY_SOURCE_DATA[energy_source]['x_position']:
                energy = x[x_position]*2*duration/10**6
                self.ENERGY_SOURCE_DATA[energy_source]['energy'].append(energy)

        # Append the supply parameter from the action space to the energy source
        for energy_source in self.SUPPLY_POWERPATHS:
            if self.SUPPLY_POWERPATHS[energy_source]['supply_param_number'] != []:
                ratio = round(action[self.SUPPLY_POWERPATHS[energy_source]['supply_param_number']],3)
                self.SUPPLY_POWERPATHS[energy_source]['ratios'].append(ratio)

        self.actions.append(action)

        # Calculate the effective radiative forcing depending on the powerpaths
        self.erf += self._erf(x)

        # Go to the next flight phase
        self.flight_phase += 1

        # If the aircraft has landed
        if self.flight_phase > 4:
            # Compute the component weights of the propulsion system
            component_weight = self._comp_weight()

            # Compute the fuel and storage system weight
            fuel_weight = self._fuel_weight()

            # Choose the most constraining battery requirement and remove the other one from the total weight
            battery_redundant_weight = np.fmin(self.ENERGY_SOURCE_DATA['Battery']['weight'][0], sum(self.COMPONENT_DATA['Battery']['weight']))

            # Add ERF from NOx
            self._erf_nox()

            MTOM = DATA['MTOM']
            # Compute maximum payload
            payload = MTOM - 12543 - fuel_weight - component_weight + battery_redundant_weight

            kerosene_fuel_used = sum(self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy'])/self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density_fuel']
            hydrogen_fuel_used = sum(self.ENERGY_SOURCE_DATA['HydrogenStorage']['energy'])/self.CHARACTERISTICS['HydrogenStorage']['grav_energy_density_fuel']

            fuel_used = kerosene_fuel_used + hydrogen_fuel_used

            if fuel_used < 650:
                payload = payload - (650 - fuel_used)
                MTOM -= (650 - fuel_used)

            # Check the centre of gravity constraint
            if self.CARGO == False:
                if payload > 0:
                    kerosene_fuel_used = 0
                    hydrogen_fuel_used = 0
                    max_MAC = 25
                    min_MAC = 25
                    for i in range(0, self.flight_phase):
                        if i == 0:
                            MAC_for, MAC_aft, moment_arm, kerosene_storage_mass, kerosene_cg, hydrogen_fuel_system_mass, hydrogen_fuel_system_cg = self._cg_constraint(
                                MTOM, payload, kerosene_fuel_used, hydrogen_fuel_used)
                            diff = 0
                        else:
                            try:
                                kerosene_fuel_used += self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy'][i-1] / \
                                                      self.CHARACTERISTICS['KeroseneStorage'][
                                                          'grav_energy_density_fuel']
                            except:
                                pass
                            try:
                                hydrogen_fuel_used += self.ENERGY_SOURCE_DATA['HydrogenStorage']['energy'][i-1] / \
                                                      self.CHARACTERISTICS['HydrogenStorage'][
                                                          'grav_energy_density_fuel']
                            except:
                                pass

                            def fuel_mass_to_cg(mass):
                                cg = (1.711 * 10 ** (-20) * mass ** 6 - 1.64125 * 10 ** (
                                    -16) * mass ** 5 + 6.325 * 10 ** (-13) * mass ** 4
                                      - 1.257 * 10 ** (-9) * mass ** 3 + 1.37463 * 10 ** (-6) * mass ** 2
                                      - 8.1232955 * 10 ** (-4) * mass + 14.672779788)
                                return np.min([cg, 14.6])

                            kerosene_mass_start = sum(self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy']) / self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density_fuel']
                            kerosene_cg_new = fuel_mass_to_cg(kerosene_mass_start - kerosene_fuel_used)

                            new_arm = moment_arm - kerosene_storage_mass * kerosene_cg - hydrogen_fuel_system_mass * hydrogen_fuel_system_cg
                            new_arm = new_arm + (kerosene_storage_mass-kerosene_fuel_used) * kerosene_cg_new + (hydrogen_fuel_system_mass-hydrogen_fuel_used) * hydrogen_fuel_system_cg
                            arm = new_arm / (MTOM - kerosene_fuel_used -hydrogen_fuel_used)
                            diff = MAC_for - (arm - 13.604) / 2.303 * 100

                        if MAC_for - diff > 39:
                            done = True
                            info = {"Supply_Parameters": self.SUPPLY_POWERPATHS}
                            reward = - abs(MAC_for-diff)/39
                            if reward < -5 or reward > -1:
                                self.pt.describe()
                                print(self.actions)
                                print(reward)
                                print(min_MAC, max_MAC)
                                raise ValueError('CG penalty too large or small')
                            return self._obs(), float(reward), bool(done), False, info
                        elif MAC_for-diff < 10:
                            if MAC_aft - diff > 10:
                                pass
                            else:
                                raise ValueError('CG moves into forward infeasible')

            co2_pp_baseline = 8080.78997925 / 6807.853228990148
            nox_pp_baseline = 31660.564192850526
            co2_pp_threshold = co2_pp_baseline * 0.25
            nox_pp_threshold = nox_pp_baseline * 0.1

            # print(self.actions)
            # print(self.x)
            # print(self.ENERGY_SOURCE_DATA)
            # print(self.COMPONENT_DATA)
            # print(payload)
            # print('Payload reduction:', (650 - fuel_used))
            # print(self.co2_emissions, self.nox_emissions, payload)
            co2_dif_threshold = co2_pp_threshold - self.co2_emissions / payload
            nox_dif_threshold = nox_pp_threshold - self.nox_emissions*1000

            # Theoretical reward of a standard ATR-72 flight
            baseline = 7246.232393990147/293.5160354745374

            #Calculate the reward based on the maximum allowable payload and erf, avoid division by zero
            if payload > 0:

                def FP2050():
                    reward = payload / 755.9360369704433
                    if co2_dif_threshold < 0 or nox_dif_threshold < 0:
                        summ = np.min([co2_dif_threshold, 0]) + np.min([nox_dif_threshold / payload, 0])
                        reward = (payload / 755.9360369704433 -1) * np.exp(10*summ)
                    return reward

                if self.FP2050:
                    reward = FP2050()
                else:
                    reward = payload / max(self.erf, 1e-5)
                    reward = (reward - baseline) / baseline
                    reward = 2 * 10 / np.pi * np.arctan(reward / 10)

                if reward <-1 or reward >10:
                    self.pt.describe()
                    print(self.actions)
                    print(payload)
                    print(reward)
                    print(kerosene_fuel_used + hydrogen_fuel_used)
                    print(landing_mass)
                    raise ValueError('Reward out of bounds')
            else:
                reward = payload
                reward = (reward - baseline) / baseline
                reward = 2 * 10 / np.pi * np.arctan(reward / 1000)
                reward = reward - 5

                if reward <-10 or reward >-5:
                    self.pt.describe()
                    print(self.actions)
                    print(payload)
                    print(reward)
                    raise ValueError('Reward out of bounds')

            done = True
            info = {"Supply_Parameters": self.SUPPLY_POWERPATHS}
            # Scale reward for better distribution

        else:
            reward = 0
            done = False
            info = {}
        obs = self._obs()
        return obs, float(reward), bool(done), False, info

    def _pms(self, x):
        """ Function to calculate input power sum of each powermanagement """
        power = []

        # Loop over each powermanagement system
        for id, powermanagement in enumerate(self.pm_connections):
            limit = 15
            # Record the input and output powerpath ids of the powermanagement system
            pm_inputs = powermanagement[0].copy()
            pm_outputs = powermanagement[1].copy()

            # Record the associated power value
            inputs = []
            outputs = []
            for input in pm_inputs:
                inputs.append(x[input])
            for output in pm_outputs:
                outputs.append(x[output])

            # Calculate the difference between the two values
            # If there is a difference, this means that the direction of a powerpath has been switched
            pm_efficiency = self.CHARACTERISTICS['PowerManagement']['efficiency']
            diff = sum(inputs)*pm_efficiency - sum(outputs)
            while_loop_counter = 0
            # If there is a significant difference then a powerpath(s) have switched direction
            while diff > limit or limit < -15:
                # Loop over the powerpaths that were an input to a powermanagement system and have switched direction
                for switched_pm in self.powerpaths_switched_input:
                    # If the switched powerpath is an input to the current powermanagement system
                    if switched_pm in pm_inputs:
                        # Get the index in the list of the switched path
                        index = pm_inputs.index(switched_pm)
                        # Get the value of the path
                        powerpath_value = inputs[index]
                        # Remove the value of the two input lists
                        inputs.remove(powerpath_value)
                        pm_inputs.pop(index)
                        # Append the value to the output list
                        outputs.append(powerpath_value)
                # Loop over the powerpaths that were an output of a powermanagement system and have switched direction
                for switched_pm in self.powerpaths_switched_output:
                    # If the switched powerpath is an output of the current powermanagement system
                    if switched_pm in pm_outputs:
                        # Get the index in the list of the switched path
                        index = pm_outputs.index(switched_pm)
                        # Get the value of the path
                        powerpath_value = outputs[index]
                        # Remove the value of the two output lists
                        outputs.remove(powerpath_value)
                        pm_outputs.pop(index)
                        # Append the value to the input list
                        inputs.append(powerpath_value)
                # Recalculate the difference
                diff = sum(inputs)*pm_efficiency - sum(outputs)
                while_loop_counter+=1
                if while_loop_counter >= 10:
                    self.pt.describe()
                    print(self.powerpaths)
                    print(x)
                    print(pm_efficiency)
                    print(inputs)
                    print(outputs)
                    print(diff)
                    limit += 1
                if while_loop_counter > 20:
                    self.pt.describe()
                    print(self.powerpaths)
                    print(x)
                    print(pm_efficiency)
                    print(inputs)
                    print(outputs)
                    print(diff)
                    raise ValueError('Stuck in while loop trying to balance PowerManagement inputs and outputs')

            # When all the switches have occured, append the sum of the inputs which is used to size each powermanagement system
            power.append(sum(inputs))
        # If the list is empty then simply append all powers
        if self.sum_input_to_pm == []:
            for value in power:
                self.sum_input_to_pm.append(value)
        # If it is not empty then check if the input power of each system is larger, then overwrite
        else:
            for id, value in enumerate(power):
                if value > self.sum_input_to_pm[id]:
                    self.sum_input_to_pm[id] = value

    def _erf(self, x):
        """ Calculate the ERF based on the amount of fuel used during each phase of flight """
        # Caluclate ERF from CO2 and Sulfate
        try:
            kerosene_weight = self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy'][self.flight_phase-1] / \
                                      self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density_fuel']
        except:
            kerosene_weight = 0
        self.co2_emissions += kerosene_weight * FLIGHT_CHARACTERISTICS[self.flight_phase]['EI_CO2']
        kerosene_erf = kerosene_weight * FLIGHT_CHARACTERISTICS[self.flight_phase]['Kerosene_ERF']
        return kerosene_erf #+ hydrogen_erf

    def _erf_nox(self):

        kerosene_power = [0, 0, 0, 0]
        hydrogen_power = [0, 0, 0, 0]

        # Caluclate ERF from NOx
        for path, powerpath in enumerate(self.powerpaths):
            try:
                # Find power from kerosene and hydrogen into the gas turbine
                if powerpath[2].name == 'GasTurbine':
                    if powerpath[1].name == 'KeroseneStorage':
                        for phase_indicator, phase in enumerate(self.x):
                            kerosene_power[phase_indicator] = phase[path] * 2
                    if powerpath[1].name == 'HydrogenStorage':
                        for phase_indicator, phase in enumerate(self.x):
                            hydrogen_power[phase_indicator] = phase[path] * 2
            except:
                pass
        for path, powerpath in enumerate(self.powerpaths):
            if powerpath[1].name == 'GasTurbine':
                # Find the max power
                max_power = self.COMPONENT_DATA['GasTurbine']['power'][0]
                if max_power == 0:
                    break
                for phase_indicator, phase in enumerate(self.x):
                    # Calculate the throttle setting
                    phase_power = phase[path] * 2
                    throttle_setting = phase_power / max_power * 100
                    if throttle_setting <= 100:
                        pass
                    else:
                        self.pt.describe()
                        print(self.actions)
                        print(phase_power)
                        print(max_power)
                        print(throttle_setting)
                        raise ValueError('Throttle not within bounds')
                    # Calculate the corrected NOx EI based on throttle setting, OPR, and corrections
                    EI_nox_cor = nox_emmisions(throttle_setting, phase_indicator + 1)
                    # Calculate the ERF per kg of fuel
                    ERF_nox_fuel = 3.85559 * EI_nox_cor / 1000
                    # Calculate kg of fuel and ERF from NOx
                    try:
                        kerosene_phase_mass = kerosene_power[phase_indicator] * FLIGHT_CHARACTERISTICS[phase_indicator + 1]['Duration'] / 10 ** 6 / self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density_fuel']
                        ERF_kerosene = kerosene_phase_mass * ERF_nox_fuel
                        self.erf += ERF_kerosene
                        self.nox_emissions += kerosene_phase_mass * EI_nox_cor/1000
                    except:
                        pass
                    try:
                        hydrogen_phase_mass = hydrogen_power[phase_indicator] * FLIGHT_CHARACTERISTICS[phase_indicator + 1]['Duration'] / 10 ** 6 / self.CHARACTERISTICS['HydrogenStorage']['grav_energy_density_fuel']
                        ERF_hydrogen = hydrogen_phase_mass * ERF_nox_fuel * 0.76
                        self.erf += ERF_hydrogen
                        self.nox_emissions += hydrogen_phase_mass * EI_nox_cor/1000 * 0.76
                    except:
                        pass

    def _comp_weight(self):
        """" Calculate the weight of each component """
        component_weight = 0
        for position, x_name in enumerate(self.x_names):
            for component in self.COMPONENT_DATA:
                #Loop over each component (except em and pm) and calculate its weight based on the max power)
                if x_name[:-1] == component and not (component == 'ElectricMachine' or component == 'PowerManagement'):
                    self.COMPONENT_DATA[component]['power'].append(self.x_max[position]*2)
                    self.COMPONENT_DATA[component]['weight'].append(self.x_max[position]*2/10**3/self.CHARACTERISTICS[component]['grav_power_density'])
                    component_weight += self.x_max[position]*2/10**3/self.CHARACTERISTICS[component]['grav_power_density']
        # The weights of the em and pm are calculated separately as these are based on the direction of the flow
        for electric_machine in self.em_connections:
            # The maximum power is always the electric machine input power, on which the sizing is based
            max_power = np.maximum(self.x_max[electric_machine[0]], self.x_max[electric_machine[-1]])
            self.COMPONENT_DATA[electric_machine[2].name]['power'].append(max_power*2)
            self.COMPONENT_DATA[electric_machine[2].name]['weight'].append(
                max_power * 2 / 10 ** 3 / self.CHARACTERISTICS[electric_machine[2].name]['grav_power_density'])
            component_weight += max_power * 2 / 10 ** 3 / self.CHARACTERISTICS[electric_machine[2].name]['grav_power_density']
        for power in self.sum_input_to_pm:
            self.COMPONENT_DATA['PowerManagement']['power'].append(power*2)
            self.COMPONENT_DATA['PowerManagement']['weight'].append(power * 2 / 10 ** 3 / self.CHARACTERISTICS['PowerManagement']['grav_power_density'])
            component_weight += power * 2 / 10 ** 3 / self.CHARACTERISTICS['PowerManagement']['grav_power_density']
        return component_weight

    def _fuel_weight(self):
        """ Calculate the weight of the fuel including the storage system. """
        self.ENERGY_SOURCE_DATA['KeroseneStorage']['weight'].append(sum(self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy']) / \
                                  self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density'])
        self.ENERGY_SOURCE_DATA['HydrogenStorage']['weight'].append(sum(self.ENERGY_SOURCE_DATA['HydrogenStorage']['energy']) / \
                                  self.CHARACTERISTICS['HydrogenStorage']['grav_energy_density'])
        self.ENERGY_SOURCE_DATA['Battery']['weight'].append(sum(self.ENERGY_SOURCE_DATA['Battery']['energy']) / self.CHARACTERISTICS['Battery'][
            'grav_energy_density'] / self.CHARACTERISTICS['Battery']['efficiency'])
        return sum(self.ENERGY_SOURCE_DATA['KeroseneStorage']['weight'] + self.ENERGY_SOURCE_DATA['HydrogenStorage']['weight']
                           + self.ENERGY_SOURCE_DATA['Battery']['weight'])

    def _cg_constraint(self, MTOM, payload, kerosene_fuel_used, hydrogen_fuel_used):
        """ Assign all component a position and calculate the corresponding centre of gravity. """

        def fuel_mass_to_cg(mass):
            cg = (1.711 * 10 ** (-20) * mass ** 6 - 1.64125 * 10 ** (-16) * mass ** 5 + 6.325 * 10 ** (-13) * mass ** 4
                  - 1.257 * 10 ** (-9) * mass ** 3 + 1.37463 * 10 ** (-6) * mass ** 2
                  - 8.1232955 * 10 ** (-4) * mass + 14.672779788)
            return np.min([cg, 14.6])

        def wing_fuselage_distribution_forwardcg(component_name, mass, volume_remaining, wing_volume_available,
                                       front_volume_available,
                                       back_volume_available):
            mass_remaining = mass
            # First store components in the front compartment
            if front_volume_available >= volume_remaining:
                front_mass = mass_remaining
                front_volume_available -= volume_remaining
                mass_remaining = 0

                wing_mass = 0
                back_mass = 0
                fuselage_mass = 0
                fuselage_volume = 0
            # If not everything fits, fill it up and continue
            else:
                front_mass = front_volume_available * self.CHARACTERISTICS[component_name]['vol_power_density'] / \
                             self.CHARACTERISTICS[component_name]['grav_power_density']
                mass_remaining -= front_mass
                volume_remaining -= front_volume_available
                front_volume_available = 0
                # Then store remaining components in the wing
                if wing_volume_available >= volume_remaining:
                    wing_mass = mass_remaining
                    wing_volume_available -= volume_remaining
                    mass_remaining = 0

                    back_mass = 0
                    fuselage_mass = 0
                    fuselage_volume = 0
                # If not everything fits, fill it up and continue
                else:
                    wing_mass = wing_volume_available * self.CHARACTERISTICS[component_name]['vol_power_density'] / \
                                self.CHARACTERISTICS[component_name]['grav_power_density']
                    mass_remaining -= wing_mass
                    volume_remaining -= wing_volume_available
                    wing_volume_available = 0
                    # Then store remaining components in the back compartment
                    if back_volume_available >= volume_remaining:
                        back_mass = mass_remaining
                        back_volume_available -= volume_remaining
                        mass_remaining = 0

                        fuselage_mass = 0
                        fuselage_volume = 0
                    # If not everything fits, fill it up and continue
                    else:
                        back_mass = back_volume_available * self.CHARACTERISTICS[component_name]['vol_power_density'] / \
                                    self.CHARACTERISTICS[component_name]['grav_power_density']
                        mass_remaining -= back_mass
                        volume_remaining -= back_volume_available
                        back_volume_available = 0
                        fuselage_mass = mass_remaining
                        fuselage_volume = volume_remaining
            return wing_mass, wing_volume_available, front_mass, front_volume_available, back_mass, back_volume_available, fuselage_mass, fuselage_volume

        def wing_fuselage_distribution_aftcg(component_name, mass, volume_remaining, wing_volume_available,
                                       front_volume_available,
                                       back_volume_available):
            mass_remaining = mass
            # First store components in the back compartment
            if back_volume_available >= volume_remaining:
                back_mass = mass_remaining
                back_volume_available -= volume_remaining
                mass_remaining = 0

                wing_mass = 0
                front_mass = 0
                fuselage_mass = 0
                fuselage_volume = 0
            # If not everything fits, fill it up and continue
            else:
                back_mass = back_volume_available * self.CHARACTERISTICS[component_name]['vol_power_density'] / \
                            self.CHARACTERISTICS[component_name]['grav_power_density']
                mass_remaining -= back_mass
                volume_remaining -= back_volume_available
                back_volume_available = 0
                # Then store components in the wing
                if wing_volume_available >= volume_remaining:
                    wing_mass = mass_remaining
                    wing_volume_available -= volume_remaining
                    mass_remaining = 0

                    front_mass = 0
                    fuselage_mass = 0
                    fuselage_volume = 0
                # If not everything fits, fill it up and continue
                else:
                    wing_mass = wing_volume_available * self.CHARACTERISTICS[component_name]['vol_power_density'] / \
                                self.CHARACTERISTICS[component_name]['grav_power_density']
                    mass_remaining -= wing_mass
                    volume_remaining -= wing_volume_available
                    wing_volume_available = 0
                    # Then store components in the front compartment
                    if front_volume_available >= volume_remaining:
                        front_mass = mass_remaining
                        front_volume_available -= volume_remaining
                        mass_remaining = 0

                        fuselage_mass = 0
                        fuselage_volume = 0
                    # If not everything fits, fill it up and continue
                    else:
                        front_mass = front_volume_available * self.CHARACTERISTICS[component_name][
                            'vol_power_density'] / \
                                     self.CHARACTERISTICS[component_name]['grav_power_density']
                        mass_remaining -= front_mass
                        volume_remaining -= front_volume_available
                        front_volume_available = 0
                        fuselage_mass = mass_remaining
                        fuselage_volume = volume_remaining
            return wing_mass, wing_volume_available, front_mass, front_volume_available, back_mass, back_volume_available, fuselage_mass, fuselage_volume

        def MAC_calculation(wing_volume_available, fuselage_most_aft_point_available, kerosene_fuel_used, hydrogen_fuel_used, front_first = True):
            front_volume_available = DATA['FrontLowerVolume']
            back_volume_available = DATA['BackLowerVolume']

            if front_first == True:
                # First try to store the components in the front compartment, then in the wing and finally in the back compartment
                pm_wing_mass, wing_volume_available, pm_front_mass, front_volume_available, pm_back_mass, back_volume_available, pm_fuselage_mass, pm_fuselage_volume = wing_fuselage_distribution_forwardcg(
                    'PowerManagement', pm_mass, pm_volume, wing_volume_available, front_volume_available,
                    back_volume_available)
                bat_wing_mass, wing_volume_available, bat_front_mass, front_volume_available, bat_back_mass, back_volume_available, bat_fuselage_mass, bat_fuselage_volume = wing_fuselage_distribution_forwardcg(
                    'Battery', battery_mass, battery_volume, wing_volume_available, front_volume_available,
                    back_volume_available)
                fc_wing_mass, wing_volume_available, fc_front_mass, front_volume_available, fc_back_mass, back_volume_available, fc_fuselage_mass, fc_fuselage_volume = wing_fuselage_distribution_forwardcg(
                    'FuelCell', fc_mass, fc_volume, wing_volume_available, front_volume_available, back_volume_available)

            else:
                # Then try to store the components in the wing, then in the back compartment and finally in the front compartment
                pm_wing_mass, wing_volume_available, pm_front_mass, front_volume_available, pm_back_mass, back_volume_available, pm_fuselage_mass, pm_fuselage_volume = wing_fuselage_distribution_aftcg(
                    'PowerManagement', pm_mass, pm_volume, wing_volume_available, front_volume_available,
                    back_volume_available)
                bat_wing_mass, wing_volume_available, bat_front_mass, front_volume_available, bat_back_mass, back_volume_available, bat_fuselage_mass, bat_fuselage_volume = wing_fuselage_distribution_aftcg(
                    'Battery', battery_mass, battery_volume, wing_volume_available, front_volume_available,
                    back_volume_available)
                fc_wing_mass, wing_volume_available, fc_front_mass, front_volume_available, fc_back_mass, back_volume_available, fc_fuselage_mass, fc_fuselage_volume = wing_fuselage_distribution_aftcg(
                    'FuelCell', fc_mass, fc_volume, wing_volume_available, front_volume_available, back_volume_available)

            component_wing_mass = pm_wing_mass + bat_wing_mass + fc_wing_mass
            front_compartment_mass = pm_front_mass + bat_front_mass + fc_front_mass
            back_compartment_mass = pm_back_mass + bat_back_mass + fc_back_mass

            front_volume_used = DATA['FrontLowerVolume'] - front_volume_available
            front_cg = DATA['ForwardFrontLower'] + front_volume_used / 1000 / DATA['FuselageLowerArea'] / 2
            back_volume_used = DATA['BackLowerVolume'] - back_volume_available
            back_cg = DATA['ForwardBackLower'] + back_volume_used / 1000 / DATA['FuselageLowerArea'] / 2

            lower_volume_occupied = DATA['ForwardBackLower'] + back_volume_used / 1000 / DATA['FuselageLowerArea']
            # Calculate the longitudinal length the other components occupy, if this extends beyond the space occupied in the lower compartment
            ### This cannot be fully utilized and the cross-sectional area is reduced
            additional_mass_fuselage = pm_fuselage_mass + bat_fuselage_mass + fc_fuselage_mass
            additional_volume_fuselage = (pm_fuselage_volume + bat_fuselage_volume + fc_fuselage_volume) / 1000
            aft_point_fuselage_volume = fuselage_most_aft_point_available - additional_volume_fuselage / DATA[
                'FuselageCrossSection']
            if aft_point_fuselage_volume < lower_volume_occupied:
                full_volume_available = (fuselage_most_aft_point_available - lower_volume_occupied) * DATA[
                    'FuselageCrossSection']
                cg_full_volume_available = fuselage_most_aft_point_available - (
                            fuselage_most_aft_point_available - lower_volume_occupied) / 2
                top_volume_available = additional_volume_fuselage - full_volume_available
                cg_top_volume_available = lower_volume_occupied - top_volume_available / DATA['FuselageTopArea'] / 2
                additional_volume_fuselage_cg = full_volume_available / additional_volume_fuselage * cg_full_volume_available + top_volume_available / additional_volume_fuselage * cg_top_volume_available
                fuselage_most_aft_point_available -= top_volume_available / DATA['FuselageTopArea']
            else:
                additional_volume_fuselage_cg = fuselage_most_aft_point_available - additional_volume_fuselage / DATA[
                    'FuselageCrossSection'] / 2
                fuselage_most_aft_point_available -= additional_volume_fuselage / DATA['FuselageCrossSection']

            # Calculate the c.g of the payload
            if front_first == True:
                rows = np.floor(payload/102.777778/4)
                payload_cg = (DATA['PayloadStart']*2 + rows*0.7366) / 2
            else:
                payload_cg = (DATA['PayloadStart'] + fuselage_most_aft_point_available - 2.684) / 2

            # Calculate the moment arm
            moment_arm = kerosene_storage_mass * kerosene_cg + hydrogen_fuel_system_mass * hydrogen_fuel_system_cg + engine_mass * engine_cg + em_mass * em_cg + component_wing_mass * \
                         DATA['WingCG'] + front_compartment_mass * front_cg + back_compartment_mass * back_cg + additional_mass_fuselage * additional_volume_fuselage_cg + payload * payload_cg + \
                         DATA['OEW-PropSystemMass'] * DATA['OEW-PropSystemArm']

            # Calculate the aircraft c.g and its percentage of the MAC
            arm = moment_arm / (MTOM)
            Percentage_of_MAC = (arm - 13.604) / 2.303 * 100

            # print('Kerosene:', kerosene_storage_mass-kerosene_fuel_used, kerosene_cg)
            # print('Hydrogen:', hydrogen_fuel_system_mass-hydrogen_fuel_used, hydrogen_fuel_system_cg)
            # print('Engines:', engine_mass, engine_cg)
            # print('Battery:', battery_mass)
            # print('PM:', pm_mass)
            # print('FC:', fc_mass)
            # print('EM:', em_mass, em_cg)
            # print("Wing mass:", component_wing_mass)
            # print('Front:', front_compartment_mass, front_cg)
            # print('Back:', back_compartment_mass, back_cg)
            # print('Payload:', payload, payload_cg)

            return Percentage_of_MAC, component_wing_mass, front_compartment_mass, back_compartment_mass, front_cg, back_cg, payload_cg, moment_arm, kerosene_storage_mass, kerosene_cg, hydrogen_fuel_system_mass, hydrogen_fuel_system_cg

        # Calculate mass of the fuel itself to determine the c.g of the system and calculate volume to know how much of the wing is occupied
        kerosene_mass = sum(self.ENERGY_SOURCE_DATA['KeroseneStorage']['energy']) / self.CHARACTERISTICS['KeroseneStorage']['grav_energy_density_fuel']
        kerosene_storage_mass = self.ENERGY_SOURCE_DATA['KeroseneStorage']['weight'][0]
        kerosene_cg = fuel_mass_to_cg(kerosene_mass - kerosene_fuel_used)
        kerosene_volume = (kerosene_mass)/DATA['FuelDensity']

        wing_volume_available_after_kerosene = DATA['WingVolumeAvailable'] - kerosene_volume

        engine_mass = sum(self.COMPONENT_DATA['GasTurbine']['weight'])
        engine_cg = DATA['EngineCG']

        em_mass = sum(self.COMPONENT_DATA['ElectricMachine']['weight'])
        em_cg = DATA['EMCG']

        # Calculate mass and volume of hydrogen storage including the fuel
        hydrogen_fuel_system_mass = sum(self.ENERGY_SOURCE_DATA['HydrogenStorage']['weight'])
        hydrogen_fuel_system_volume = hydrogen_fuel_system_mass * self.CHARACTERISTICS['HydrogenStorage'][
            'grav_energy_density'] / self.CHARACTERISTICS['HydrogenStorage']['vol_energy_density']

        # Calculate longitudinal length of the storage system, its c.g and the point where it ends
        hydrogen_fuel_system_occupied_length = hydrogen_fuel_system_volume / 1000 / DATA['FuselageCrossSection']
        hydrogen_fuel_system_cg = DATA['AftMostPoint'] - hydrogen_fuel_system_occupied_length / 2
        fuselage_most_aft_point_available_after_hydrogen = DATA['AftMostPoint'] - hydrogen_fuel_system_occupied_length

        # Calculate mass and volume of the fuel cells, powermanagement systems and batteries
        fc_mass = sum(self.COMPONENT_DATA['FuelCell']['weight'])
        fc_volume = fc_mass * self.CHARACTERISTICS['FuelCell']['grav_power_density'] / self.CHARACTERISTICS['FuelCell'][
            'vol_power_density']

        battery_mass = np.fmax(self.ENERGY_SOURCE_DATA['Battery']['weight'][0],
                               sum(self.COMPONENT_DATA['Battery']['weight']))
        battery_volume = battery_mass * self.CHARACTERISTICS['Battery']['grav_power_density'] / \
                         self.CHARACTERISTICS['Battery']['vol_energy_density']

        pm_mass = sum(self.COMPONENT_DATA['PowerManagement']['weight'])
        pm_volume = pm_mass * self.CHARACTERISTICS['PowerManagement']['grav_power_density'] / \
                    self.CHARACTERISTICS['PowerManagement']['vol_power_density']

        # Calculate the c.g as a percentage of the MAC
        Percentage_of_MAC_for, component_wing_mass_for, front_compartment_mass_for, back_compartment_mass_for, front_cg_for, back_cg_for, payload_cg_for, moment_arm_for, kerosene_storage_mass_for, kerosene_cg_for, hydrogen_fuel_system_mass_for, hydrogen_fuel_system_cg_for = MAC_calculation(wing_volume_available_after_kerosene, fuselage_most_aft_point_available_after_hydrogen, kerosene_fuel_used, hydrogen_fuel_used)

        Percentage_of_MAC_aft, component_wing_mass_aft, front_compartment_mass_aft, back_compartment_mass_aft, front_cg_aft, back_cg_aft, payload_cg_aft, moment_arm_aft, kerosene_storage_mass_aft, kerosene_cg_aft, hydrogen_fuel_system_mass_aft, hydrogen_fuel_system_cg_aft = MAC_calculation(wing_volume_available_after_kerosene, fuselage_most_aft_point_available_after_hydrogen, kerosene_fuel_used, hydrogen_fuel_used, front_first = False)

        # If after the redistribution the c.g is still to far forward, raise an error as this should not happen
        if Percentage_of_MAC_aft < 10:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            self.pt.describe()
            print(self.actions)
            print(self.ENERGY_SOURCE_DATA)
            print(self.COMPONENT_DATA)
            print(self.SUPPLY_POWERPATHS)
            print(payload)
            print(kerosene_fuel_used, hydrogen_fuel_used)
            print(Percentage_of_MAC, component_wing_mass, front_compartment_mass, back_compartment_mass, front_cg, back_cg, payload_cg)
            print(Percentage_of_MAC_for, component_wing_mass_for, front_compartment_mass_for, back_compartment_mass_for, front_cg_for, back_cg_for, payload_cg_for)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            raise ValueError('Infeasible design after redistribution')

        # # If after the redistribution the c.g is to far aft, it is possible to have the c.g within allowable margins
        # if old_percentage < Percentage_of_MAC and Percentage_of_MAC > 10:
        #     valid_design_exists = True
        #
        # if Percentage_of_MAC > 10 and Percentage_of_MAC < 39:
        #     valid_design_exists = True

        return Percentage_of_MAC_for, Percentage_of_MAC_aft, moment_arm_for, kerosene_storage_mass_for, kerosene_cg_for, hydrogen_fuel_system_mass_for, hydrogen_fuel_system_cg_for

    def reset(self, *, seed=None, options=None):
        """ Reset all parameters """

        if seed is not None and self.seed_initialised == False:
            self.seed_initialised = True
            print('Setting RNG with seed:', seed)
            self.np_random, _ = seeding.np_random(seed)
            self.action_space.seed(int(seed))

        pt_seed = self.np_random.integers(0,10**9)
        pt = Powertrain()
        pt_obs = pt.reset(seed=pt_seed)
        pt_done = False
        while not pt_done:
            pt_action = pt.action_space.sample()
            obs, reward, pt_done, info = pt.step(pt_action)
        powerpaths, A_obj, components = pt.matrix()

        if (len(pt.supply_param) + len(pt.shaft_param) > self.action_space.shape[0]):
            pt.describe()
            raise ValueError('Number of control parameters is larger than the action space')

        if A_obj.shape[0] > self.observation_space['M'].shape[0]:
            pt.describe()
            raise ValueError('Matrix size larger than observation space')

        self.pt = pt
        self.powerpaths = powerpaths
        self.components = components
        self.em_connections = em_connections(self.powerpaths)
        self.pm_connections = pm_connections(self.powerpaths)
        self.A_obj = A_obj.copy()
        self.snapshot = self.to_numeric(self.A_obj)
        self.flight_phase = 1
        self.b = np.zeros(self.pt.connections, dtype=np.float32)
        self.x_max = None
        self.erf = 0
        self.invalid_count = 0
        self.sum_input_to_pm = []
        self.actions = []
        self.x = []
        self.co2_emissions = 0
        self.nox_emissions = 0

        self.n_active_ctrl = len(self.pt.supply_param) + len(self.pt.shaft_param)

        # Get the names of each powerpath
        self.x_names = x_vector_names(self.powerpaths)

        # Initialize empty dictionary to store energy source data
        self.ENERGY_SOURCE_DATA = {
            "KeroseneStorage": {
                'x_position': [],
                'energy': [],
                'weight': [],
            },
            "HydrogenStorage": {
                'x_position': [],
                'energy': [],
                'weight': [],
            },
            "Battery": {
                'x_position': [],
                'energy': [],
                'weight': [],
            }
        }

        # Initialize empty dictionary to store component power data
        self.COMPONENT_DATA = {
            "GasTurbine": {
                'power': [],
                'weight': [],
            },
            "Battery": {
                'power': [],
                'weight': [],
            },
            "FuelCell": {
                'power': [],
                'weight': [],
            },
            "ElectricMachine": {
                'power': [],
                'weight': [],
            },
            "PowerManagement": {
                'power': [],
                'weight': [],
            }
        }

        # Define the x position of each energy source in the dictionary
        for i, name in enumerate(self.x_names):
            for energy_source in self.pt.energy_sources:
                if name[:-1] == energy_source[1].name:
                    self.ENERGY_SOURCE_DATA[energy_source[1].name]['x_position'].append(i)
                    break

        # Initialize empty dictionary to store supply parameter data
        self.SUPPLY_POWERPATHS = {
            "HydrogenCombustion": {
                'supply_param_number': [],
                'ratios': [],
                'OnlyEnergySource': False,
            },
            "HydrogenFuelCell": {
                'supply_param_number': [],
                'ratios': [],
                'OnlyEnergySource': False,
            },
            "Battery": {
                'supply_param_number': [],
                'ratios': [],
                'OnlyEnergySource': False,
            }
        }
        self._supply_paths(self.snapshot)
        return self._obs(), {}

    def _supply_paths(self, A):
        """ Determine the powerpaths associated with each supply parameter """
        A = A.copy()
        # Loop over the number of supply parameters
        if len(self.pt.supply_param) == 0:
            for energy_source in self.ENERGY_SOURCE_DATA:
                if self.ENERGY_SOURCE_DATA[energy_source]['x_position'] != []:
                    if self.pt.branches[0][1].name == 'FuelCell':
                        self.SUPPLY_POWERPATHS['HydrogenFuelCell']['OnlyEnergySource'] = True
                    elif self.pt.branches[0][1].name == 'GasTurbine':
                        self.SUPPLY_POWERPATHS['HydrogenCombustion']['OnlyEnergySource'] = True
                    elif self.pt.branches[0][1].name == 'PowerManagement':
                        self.SUPPLY_POWERPATHS['Battery']['OnlyEnergySource'] = True
        else:
            for i in range(0, len(self.pt.supply_param)):
                # Find the powerpath associated with each supply parameter
                supply_path = np.flatnonzero(A[i+len(self.components)] < 0)[0]
                if supply_path in self.ENERGY_SOURCE_DATA['HydrogenStorage']['x_position']:
                    if self.powerpaths[supply_path][2].name == 'GasTurbine':
                        self.SUPPLY_POWERPATHS['HydrogenCombustion']['supply_param_number'] = i
                    elif self.powerpaths[supply_path][2].name == 'FuelCell':
                        self.SUPPLY_POWERPATHS['HydrogenFuelCell']['supply_param_number'] = i
                # Check if batteries are an energy source
                if len(self.ENERGY_SOURCE_DATA['Battery']['x_position']) > 0:
                    if self.ENERGY_SOURCE_DATA['Battery']['x_position'] == supply_path:
                        self.SUPPLY_POWERPATHS['Battery']['supply_param_number'] = i
        return

class ActionFeasibilityWrapper(gym.ActionWrapper):
    """Ensure feasibility of action space"""
    def __init__(self, env):
        super().__init__(env)

    def reset(self, *args, **kwargs):
        self.penalties = []
        return self.env.reset(*args, **kwargs)

    def step(self, action):
        action = action[:self.env.n_active_ctrl]
        action_raw = action.copy()

        # If the sum of the parameters is too high (invalid design space) divide such that they are in the feasible space
        supply_sum = sum(action[:len(self.env.pt.supply_param)])
        shaft_sum = sum(action[len(self.env.pt.supply_param): len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)])

        if supply_sum > 1:
            action[:len(self.env.pt.supply_param)] = [param / supply_sum for param in action[:len(self.env.pt.supply_param)]]
        if shaft_sum > 1:
            action[len(self.env.pt.supply_param) : len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)] = [param / shaft_sum for param in
                    action[len(self.env.pt.supply_param) : len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)]]

        # Get the power requirement and duration depending on the flight phase
        power, duration = FLIGHT_CHARACTERISTICS[self.env.flight_phase]['Power'], FLIGHT_CHARACTERISTICS[self.env.flight_phase]['Duration']

        # Define the control parameters in the matrix
        for i in range(0, len(self.env.pt.supply_param)):
            self.env.pt.supply_param.set(i, action[i])
        for i in range(0, len(self.env.pt.shaft_param)):
            self.env.pt.shaft_param.set(i, action[i + len(self.env.pt.supply_param)])

        # Convert the object to a numerical matrix
        A = self.env.to_numeric(self.env.A_obj)

        # Ensure b matches A and is zeroed
        if self.env.b.shape[0] != A.shape[0]:
            self.env.b = np.zeros(A.shape[0], dtype=np.float32)
        else:
            self.env.b.fill(0.0)

        # Set the required propulsive power
        self.env.b[-1] = power

        # Calculation of the powerpath values
        x = np.linalg.solve(A, self.env.b)
        x = np.where(np.abs(x) < 1, 0.0, x)

        #Loop to scale the shaft parameters such that energy harvesting is not possible
        if (x < 0).any():
            if len(self.env.pt.shaft_param) > 0:
                # Calculate the power ratio's of the shafts that are fixed by the supply ratio's
                shaft_ratios = []
                for powerpath in self.env.pt.defined_shafts_powerpaths:
                    shaft_ratios.append(x[powerpath]/power * self.env.CHARACTERISTICS['Propeller']['efficiency'])
                # If the sum of the fixed ratio's and the set ratio's is larger than 1, the set ratio's must be reduced
                while round(sum(shaft_ratios) + sum(action[-len(self.env.pt.shaft_param):]),6) > 1:
                    np.set_printoptions(precision=16, suppress=True)
                    # Calculate the maximum sum of the set ratio's and the value by which the ratio's must be divided
                    max_sum_shaft_param = 1 - sum(shaft_ratios)
                    division = sum(action[len(self.env.pt.supply_param) : len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)])/max_sum_shaft_param
                    rounding = 6
                    division = math.ceil(division*10**rounding)/10**6
                    # print('Energy Harvesting Feasibility')
                    # self.env.pt.describe()
                    # print(action)
                    # print(sum(shaft_ratios), sum(action[-len(self.env.pt.shaft_param):]))
                    # print(max_sum_shaft_param, division)
                    # Set the new ratio's
                    action[len(self.env.pt.supply_param) : len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)] = [param / division for param in action[len(self.env.pt.supply_param) : len(self.env.pt.supply_param) + len(self.env.pt.shaft_param)]]
                    for i in range(0, len(self.env.pt.shaft_param)):
                        self.env.pt.shaft_param.set(i, action[i + len(self.env.pt.supply_param)])
                    A = self.env.to_numeric(self.env.A_obj)
                    # Recalculate x
                    x = np.linalg.solve(A, self.env.b)
                    x = np.where(np.abs(x) < 1, 0.0, x)
                    # Recalculate the fixed shaft ratio's
                    shaft_ratios = []
                    for powerpath in self.env.pt.defined_shafts_powerpaths:
                        shaft_ratios.append(x[powerpath] / power * self.env.CHARACTERISTICS['Propeller']['efficiency'])

        penalty = np.zeros((self.env.action_space.shape[0],), dtype=np.float32)
        penalty[:self.env.n_active_ctrl] = np.abs(action_raw - action)

        obs, reward, done, _, info = self.env.step(action)

        obs["violation"] = penalty
        reward -= sum(penalty)

        return obs, reward, done, False, info