from Components import Component
from random import randrange
import numpy as np
import random
from typing import Dict, List, Type, Tuple
from collections import defaultdict
from gym import Env
from gym.spaces import Box, Dict as SpaceDict, MultiBinary
from gym.spaces import Discrete, MultiDiscrete
from gym.utils import seeding
from itertools import compress
import networkx as nx
np.set_printoptions(suppress=True,
                    precision=3,
                    edgeitems=40,
                    linewidth=300)
import matplotlib.pyplot as plt

# Used for to create histogram of components used
TYPE_LIST = [
    "KeroseneStorage", "HydrogenStorage", "Battery",
    "GasTurbine", "FuelCell", "ElectricMachine",
    "GearBox", "PowerManagement", "Propeller"
]
TYPE_TO_ID = {name: i for i, name in enumerate(TYPE_LIST)}
NUM_TYPES = len(TYPE_LIST)

# Set the maximum number of branches and depth of branches
MAX_BRANCHES = 7
MAX_DEPTH    = 7

class Control_parameters(list):
    class _Slot:
        def __init__(self, value: float = 0.0):
            self.val = float(value)
        def __repr__(self):
            return repr(self.val)
        def __float__(self):
            return self.val

    class _OffsetSlot:
        def __init__(self, base_slot, delta: float):
            self._base = base_slot
            self._delta = float(delta)
        def __repr__(self):
            return repr(self._base.val + self._delta)
        def __float__(self):
            return self._base.val + self._delta

    # Create empty variables depending on the required count
    def __init__(self, count: int):
        super().__init__(Control_parameters._Slot() for _ in range(count))

    # Function to return the variable as a float
    def __getitem__(self, idx):
        return super().__getitem__(idx).val

    # Function to get a mutable variable
    def slot(self, idx: int) -> _Slot:
        return super().__getitem__(idx)

    # Function to modify the variables
    def set(self, idx: int, value: float):
        # update the underlying slot
        self.slot(idx).val = float(value)

    # Function to add an offset to the parameter
    def offset(self, idx: int, delta: float):
        base = self.slot(idx)
        return Control_parameters._OffsetSlot(base, delta)

class Powertrain(Env):
    """ Powertrain builder that assembles a sequence of components based on semantic successors defined in CHARACTERISTICS. """
    def __init__(self):
        # Action space
        self.action_space = MultiDiscrete([2, 2, 2])
        self.observation_space = SpaceDict({
            "idx": MultiBinary((MAX_DEPTH, MAX_BRANCHES, len(TYPE_LIST))),
            "decision_type": MultiBinary(5),
            "bit_width": Discrete(4),
        })

        self.np_random = None
        return

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        if hasattr(self.action_space, "seed"): self.action_space.seed(seed)
        return [seed]

    def reset(self, *, seed=None, options=None):
        """ Reset all variables and provide observation space"""

        if seed is not None:
            self.seed(int(seed))

        # Branch counter
        self.current_branch = 0

        # While loop termination
        self.end = False

        # List of closed branches, boolean to determine if new branch should be found and, boolean for finding a new branch
        self.closed_branches = []
        self.shafts = []
        self.just_closed = False
        self.finding_branch = True

        # Boolean to determine a random powermanagement system
        self.pm_choice_made = False

        # Create dictionary in which the branches and components are stored
        self.branches: Dict[int, List[Component]] = defaultdict(list)

        # Create dictionary in which the gas turbine components are stored
        self.tracking_gasturbines: Dict[Type[Component], Tuple[int, Component]] = {}

        # Create dictionary in which the gas turbine components are stored
        self.tracking_powermanagements: Dict[Type[Component], List[Tuple[int, Component]]] = defaultdict(list)

        # Initialize boolean for branching
        self.new_branch = False

        # Count the number of propulsive lines
        self.prop_lines = 0

        # Keep track of the branches that have been merged together
        self.merged_branches = []

        # Reset the observation
        self.idx = np.zeros((MAX_BRANCHES, MAX_DEPTH), dtype=np.int32)
        self.mask = np.zeros((MAX_BRANCHES, MAX_DEPTH), dtype=np.int8)
        #self.type_hist = np.zeros((NUM_TYPES,), dtype=np.float32)
        self.decision_type = 0

        return self._obs()

    def _obs(self):
        """ Converts the current branches into a mathematical representation for the agent """
        for i in range(min(len(self.branches), MAX_BRANCHES)):
            comps = self.branches[i]
            for j in range(min(len(comps), MAX_DEPTH)):
                name = getattr(comps[j], "name", type(comps[j]).__name__)
                self.idx[i, j] = TYPE_TO_ID.get(name, -1) + 1
                self.mask[i, j] = 1

        decision_type_classes = [-1, 0, 1, 2, 3]
        decision_type_index = decision_type_classes.index(int(self.decision_type))
        decision_type_onehot = np.eye(len(decision_type_classes), dtype=np.float32)[decision_type_index]

        # === after you computed type_hist and decision_type_onehot ===
        idx_oh = np.zeros((MAX_BRANCHES, MAX_DEPTH, NUM_TYPES), dtype=np.float32)

        valid = (self.idx > 0)  # cells that contain a real component
        if np.any(valid):
            r, c = np.where(valid)  # row/col indices of valid cells
            ids = (self.idx[valid] - 1).astype(np.int64)  # class indices 0..NUM_TYPES-1
            idx_oh[r, c, ids] = 1.0  # set the one-hot “1” at those positions

        # Determine the action size dependent on which decision has to be made
        if self.decision_type == -1:
            self.bit_width = 0
        elif self.decision_type == 0:  # Pick energy sources
            self.bit_width = 3
        elif self.decision_type == 1:  # Choose to remove propulsive branch of PM under certain circumstances
            self.bit_width = 1
        elif self.decision_type == 2:  # Choose number of EM's connected to one PM
            self.bit_width = self.action_space.shape[0]
        elif self.decision_type == 3:  # Pick one or multiple successors where relevant
            self.bit_width = 2
        else:
            raise ValueError(f"unknown decision_type={self.decision_type}")

        # Put into observation space dictionary
        obs = {
            "idx": idx_oh,
            "decision_type": decision_type_onehot,
            "bit_width": self.bit_width,
        }
        return obs

    def step(self, action):
        """ Function that adds the next component with logic or a choice made by the agent. """
        # Ensure at least one energy source is chosen before continuing
        while not self.branches:
            # Decision type associated with choosing energy sources
            if self.decision_type == 0:
                # Rest decision type
                self.decision_type = -1

                # Choose the energy source(s) from the available options
                action = [1, 0, 0]
                energy_sources = ['KeroseneStorage', 'HydrogenStorage', 'Battery']
                starting_components = list(compress(energy_sources, action[:self.bit_width]))

                self.energy_source = 'NO Hydrogen'
                # if sum(action) == 1:
                #     self.n_energy_sources = 1
                #     if action[0] == 1:
                #         self.energy_source = 'Kerosene'
                #     if action[1] == 1:
                #         self.energy_source = 'Hydrogen'
                #     elif action[2] == 1:
                #         self.energy_source = 'Batteries'
                # elif sum(action) == 2:
                #     self.n_energy_sources = 2
                #     if action[0] == 1 and action[1] == 1:
                #         self.energy_source = 'Kerosene and Hydrogen'
                #     elif action[0] == 1 and action[2] == 1:
                #         self.energy_source = 'Kerosene and Batteries'
                #     elif action[1] == 1 and action[2] == 1:
                #         self.energy_source = 'Hydrogen and Batteries'
                # elif sum(action) == 3:
                #     self.n_energy_sources = 3
                #     self.energy_source = 'Kerosene, Hydrogen, and Batteries'
                # Loop to assign energy sources to a branch
                for i in range(0, len(starting_components)):
                    comp = Component.name_registry[starting_components[i]]
                    self._next_id = i
                    comp.id = self._next_id

                    # Append each energy source to a new branch
                    self.branches[i].append(comp())
            # If the branches are empty, notify the agent that a decision of type 0 must be made
            else:
                self.decision_type = 0
                obs = self._obs()
                return obs, 0, False, {}

        # Loop until all branches are closed
        while self.end == False:
            # Loop until branch is found that is not closed
            while self.finding_branch == True:
                if self.current_branch not in self.closed_branches:
                    self.finding_branch = False
                else:
                    self.current_branch += 1
            # If a certain decision must be made, head directly to that function and skip the rest
            if self.decision_type == 1:
                self.powermanagements(self.merged_pm, self.branch_of_merged_pm, action)
            else:
                # Determine available options from last component in the current branch
                opts, action_required = self.options(self.current_branch, action)
                # Check if an action is required and notify the agent
                if action_required == True:
                    return opts, 0, False, {}

                ############################# Determine the available options
                options = [c.__name__ for c in opts]

                # Extend the powertrain with available options
                obs, action_required = self.extend(options, self.current_branch, action)

                # Check if an action is required and notify the agent
                if action_required == True:
                    return obs, 0, False, {}

            # Evaluate all existing branches to determine if they should be closed or not
            for j in range(0, len(self.branches)):
                # If branch is not closed yet
                if j not in self.closed_branches:
                    # Close the branch if a merge occured
                    if self.branch_close == True:
                        if j in self.merged_branches:
                            self.closed_branches.append(j)
                            self.just_closed = True
                            # if all existing branches are closed, end loop
                            if len(self.closed_branches) == len(self.branches):
                                self.end = True
                    # Close the branch if the last component is a propeller
                    if self.branches[j][-1].name == 'Propeller':
                        self.closed_branches.append(j)
                        self.shafts.append(j)
                        self.just_closed = True
                        # if all existing branches are closed, end loop
                        if len(self.closed_branches) == len(self.branches):
                            self.end = True
                if self.just_closed == True:
                    # Reset boolean to find a new branch if a branch has been closed
                    self.finding_branch = True
                    self.just_closed = False
        return self._obs(), 0, True, {}

    def merge_gasturbines(self, comp: Component, branch_id: int = 0):
        """ If a component exists already, merge current branch into branch of component. """

        # Get the class of the component and check if it exists already
        cls = type(comp)
        existing = self.tracking_gasturbines.get(cls)

        # If not, add it
        if existing is None:
            self.tracking_gasturbines[cls] = (branch_id, comp)
            return

        # If one exist, take that object and add it to the branch
        branch, existing_inst = existing
        self.branches[branch_id].append(existing_inst)
        self.merged_branches.append(branch_id)

        # Close boolean to close branches, merged boolean to avoid appending component twice
        self.branch_close = True
        self.merged = True

        # Reset component id due to merge
        self._next_id -= 1
        return

    def powermanagements(self, comp: Component, branch_id: int = 0, action: int=0):
        """ PowerManagement can either have an input and output, be connected or merge with another PM. """

        cls = type(comp)

        # Check if it is the first powermanagement component, if true append it to the list, and end function
        existing = self.tracking_powermanagements.get(cls)
        if existing is None:
            self.tracking_powermanagements[cls].append([branch_id, comp])
            return False, False

        # Option to choose between seperate or merging powermanagement systems
        # decision = randrange(2)
        # if self.decision_type == 1:
        #     decision = 1

        decision = 1

        # Option to not merge powermanagement systems, but keep them seperate and not connect them either
        if decision == 0:
            # Only append new component to dictionary
            self.tracking_powermanagements[cls].append([branch_id, comp])
            return None, False
        elif decision == 1:
            # Check if a pm has already been chosen to merge with
            if self.pm_choice_made == False:
                self.pm_choice = randrange(len(existing))
            orig_branch_id, choice_inst = existing[self.pm_choice]

            # If component has not already been merged
            if self.decision_type != 1:
                # Append merged component to current branch and save branch id
                self.branches[branch_id].append(choice_inst)
                self.merged_branches.append(branch_id)

            # Option to remove electric motor and propeller from the powermanagement if it connected in parallel
            ### with the gas turbine and only one propulsive line is added to the powermanagement system
            if self.decision_type == 1:
                self.decision_type = -1
                #action = np.array([0, 0, 0])
                parallel_option = action[:self.bit_width]
                # Set the variable to true as there is a propeller connected to the gas turbine shaft
                if parallel_option == 0:
                    parallel_possible = True
                else:
                    parallel_possible = False
                # Remove the electric motor and propeller from the original branch
                if parallel_possible:
                    del self.branches[orig_branch_id][-1]
                    del self.branches[orig_branch_id][-1]
                    self.prop_lines -= 1
                    self.pm_choice_made = False
            # Check if the powermanagement system has a propulsive line
            elif self.branches[orig_branch_id][-1].name == 'Propeller' and self.add_n_motors == 0:
                # Find branch that branches out from the gear box
                for gb_branch_id, gb_branch in enumerate(self.branches.values()):
                    component = gb_branch[0]
                    if component.name == 'GearBox':
                        # Check if the gear box is connected to a different propeller
                        for id, branch in enumerate(self.branches.values()):
                            if id != orig_branch_id and id != gb_branch_id:
                                for component_2 in branch:
                                    if component_2.id == component.id and self.branches[id][-1].name == 'Propeller':
                                        self.decision_type = 1
                                        obs = self._obs()

                                        self.merged_pm = comp
                                        self.branch_of_merged_pm = branch_id
                                        self.pm_choice_made = True
                                        return obs, True

            # close boolean to close branches, merged boolean to avoid appending component twice
            self.branch_close = True
            self.merged = True

            # Reset component id due to merge
            self._next_id -= 1

            return None, False

    def add(self, comp_cls, branch_id: int = 0, action: int=0):
        """Instantiate and append a component to the powertrain."""

        # Add new id to component
        self._next_id += 1
        comp = comp_cls()
        comp.id = self._next_id

        # Reset boolean for merging when one component has multiple successors
        self.merged = False

        # Append branched component to the new branch
        if self.new_branch == True:
            self.branches[branch_id].append(self.branched_component)
            self.new_branch = False
        # Merge components if necessary
        if comp.name == 'GasTurbine':
            self.merge_gasturbines(comp, branch_id)
        # Ignore, connect or merge with other PowerManagements
        if comp.name == 'PowerManagement':
            obs, action_required = self.powermanagements(comp, branch_id, action)
            if action_required:
                return obs, True
        # If no merge occured for this component, append it to the current branch. Avoids appending component twice
        if self.merged == False:
            self.branches[branch_id].append(comp)
            if comp.name == 'Propeller':
                self.prop_lines+=1
        return comp, False

    def current(self, branch_id: int = 0):
        """Return the most recently added component."""
        return self.branches[branch_id][-1]

    def options(self, branch_id: int = 0, action: int = 0):
        """Return possible successor components for last component in the current branch."""

        # Get available successors from each component
        curr_cls = type(self.current(branch_id))
        successors = Component.get_successors(curr_cls)
        # Ensure the electrical machine has a mechanical and electrical connection
        if curr_cls().name == 'ElectricMachine':
            predecessor = type(self.branches[branch_id][-2])
            if predecessor == Component.name_registry['PowerManagement']:
                # Removes the powermanagement if mechanical connection is required
                successors.remove(predecessor)
            if predecessor == Component.name_registry['GearBox']:
                # Removes the gearbox and propeller if electrical connection is required
                successors.remove(Component.name_registry['Propeller'])
        # Multiple electric machines as output to a powermanagement system
        elif curr_cls().name == 'PowerManagement':
            # Choice of how many motors should be added to the pm
            if self.decision_type == 2:
                self.decision_type = -1
                action = [1, 0, 0]
                self.add_n_motors = sum(action[:self.bit_width]) - 1
            # Notify the agent that a decision of type 2 must be made
            elif self.decision_type == -1:
                self.decision_type = 2
                obs = self._obs()
                return obs, True
            else:
                # Not used at the moment, but may be necessary with different settings
                self.add_n_motors = 0
            # Add the motors to the pm
            for i in range(self.add_n_motors):
                successors.append(Component.get_successors(curr_cls)[0])
        # If multiple successors possible, choose a random amount
        elif len(successors) > 1:
            # Choose successor(s) if multiple are available
            if self.decision_type == 3:
                self.decision_type = -1
                #action = [1, 1, 0]
                if successors[1]().name == 'FuelCell':
                    action = [1, 1, 0]
                else:
                    action = [1, 0, 0]
                successors = list(compress(successors, action[:self.bit_width]))
                for i in range(0, len(successors)):
                    if successors[i]().name == 'FuelCell':
                        self.energy_source = 'FC'
                    elif successors[i]().name == 'GasTurbine':
                        self.energy_source = 'NO FC'
            # notify the agent that a decision of type 3 must be made
            elif self.decision_type == -1:
                self.decision_type = 3
                obs = self._obs()
                return obs, True
        return successors, False

    def extend(self, choice, branch_id: int = 0, action: int = 0):
        """Add one or multiple chosen successor components to the same or new branches"""

        # Normalize choice to list
        choices = choice if isinstance(choice, list) else [choice]

        # Reset boolean for closing a brancg
        self.branch_close = False

        # Add each choice to the same or new branch
        added = []
        for i, c in enumerate(choices, (branch_id)):
            # If multiple choices, component that branches will be saved.
            if len(choices) > 1:
                # If first component of the multiple choices
                if len(added) == 0:
                    # Save branched component
                    self.branched_component = self.current(branch_id)
                    self.branched_component.id = self.current(branch_id).id
                else:
                    # Loop to create a non-existing branch
                    while len(self.branches[i]) != 0:
                        i+=1
                    self.new_branch = True
            # Function to add component to the branch
            comp, action_required = self.add(Component.name_registry[c], i, action)
            if action_required:
                return comp, True
            added.append(comp)
        return False, False

    def describe(self):
        """Return a human-readable representation of the powertrain sequence."""

        for i in range(0, len(self.branches)):
            lines = []
            for comp in self.branches[i]:
                lines.append(f"{comp.id} {comp.name}")
            print(" -> ".join(lines))
        return

    def describe_noprint(self):
        """Return a human-readable representation of the powertrain sequence."""

        out = []
        for i in range(0, len(self.branches)):
            lines = []
            for comp in self.branches[i]:
                lines.append(f"{comp.id} {comp.name}")
            out.append(" -> ".join(lines))
        return "\n".join(out)

    def primary_paths(self):
        """Function to define the primary energy source and shaft powerpaths"""

        # Define the primary energy source (used for matrix construction)
        primary_supply_defined = False
        for source in self.energy_sources:
            # If kerosene is used, this is the primary source
            if source[1].name == 'KeroseneStorage':
                self.primary_source = source[1]
                primary_supply_defined = True
                break
            # if batteries are used and is kerosene not, this is the primary source
            elif source[1].name == 'Battery':
                self.primary_source = source[1]
                primary_supply_defined = True

        # If neither kerosene or batteries are present, hydrogen is the primary source
        if primary_supply_defined == False:
            for source in self.energy_sources:
                if source[1].name == 'HydrogenStorage':
                    self.primary_source = source[1]

        # Define the primary shaft (used for matrix construction)
        primary_shaft_defined = False
        for branch_id, branch in enumerate(self.branches.values()):
            # Only loop over the branches that end with a propeller
            if branch[-1].name == 'Propeller':
                for component in branch:
                    # If a gas turbine is in that branch this will be the primary shaft
                    if component.name == 'GasTurbine':
                        self.primary_shaft = branch[-1]
                        primary_shaft_defined = True
                        break
                    # If a fuel cell, but no gas turbine is in that branch this will be the primary shaft
                    elif component.name == 'FuelCell':
                        self.primary_shaft = branch[-1]
                        primary_shaft_defined = True
                if primary_shaft_defined == True:
                    break

        # If neither a gas turbine or fuel cell are present, the first shaft is chosen
        if primary_shaft_defined == False:
            for branch_id, branch in enumerate(self.branches.values()):
                if branch[-1].name == 'Propeller':
                    self.primary_shaft = branch[-1]
        return

    def shaft_ratios(self, powerpaths):
        """" Function to with shaft powerpaths should have a shaft ratio defined"""

        # Use graph theory to determine the different separate components once energy sources are removed
        G = nx.Graph()

        # Add every component as a node with id, type, name
        for branch in self.branches.values():
            for comp in branch:
                G.add_node(comp.id, type = comp.type, name = comp.name)
            # Add connections between each component
            G.add_edges_from((u.id, v.id) for u, v in zip(branch, branch[1:]))

        def powertrain_graph_id(G: nx.Graph, digest_size: int = 32) -> str:
            """ Function used to asign unique ID to each graph """

            from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash as wl_hash
            H = G.copy()
            # Combine your node attributes into a single stable label
            for n, data in H.nodes(data=True):
                t = str(data.get("type", "?"))
                nm = str(data.get("name", "?"))
                data["label"] = f"{t}|{nm}"
            return wl_hash(H, node_attr="label", edge_attr=None, digest_size=digest_size)

        self.graph_id = powertrain_graph_id(G)

        # Plot the architecture
        # labels = {n: G.nodes[n]['name'] for n in G.nodes}
        # plt.figure(figsize=(11, 9))
        # nx.draw(G, labels=labels, with_labels=True, node_size=500, font_size=15)
        # plt.show()

        # Remove the energy_source components
        energy_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get('type') == 'energy_source']
        G.remove_nodes_from(energy_nodes)

        # Find the remaining shaft powerpaths and remove the primary powerpath from the list
        shaft_powerpaths = [[next(G.neighbors(pid)), pid] for pid, attrs in G.nodes(data=True) if attrs.get('name') == 'Propeller']

        # If too many shaft powerpaths are found. Ensure that in each connected component there is one less powerpath
        # defined compared to the number of shafts
        self.defined_shafts_powerpaths = []
        if len(shaft_powerpaths) != len(self.shaft_param):
            to_remove = []
            for cc in nx.connected_components(G):
                # Find the shaft powerpaths
                shafts_in_cc = [s for s in shaft_powerpaths if s[1] in cc]
                if len(shafts_in_cc) == 1:
                    for i, powerpath in enumerate(powerpaths):
                        try:
                            if powerpath[1].id == shafts_in_cc[0][0] and powerpath[2].id == shafts_in_cc[0][1]:
                                self.defined_shafts_powerpaths.append(i)
                        except:
                            pass
                primary = False
                # Loop through all shaft powerpaths
                # If the primary shaft is included, append it to the list and continue to the next component
                for powerpath in shafts_in_cc:
                    if self.primary_shaft.id in powerpath:
                        to_remove.append(powerpath)
                        primary = True
                        break
                # If the primary shaft has not been removed, remove a different branch
                if primary == False:
                    for powerpath in shafts_in_cc:
                        # Otherwise append the next shaft powerpath
                        to_remove.append(powerpath)
                        break
            # Remove the appended shafts
            for shaft in to_remove:
                shaft_powerpaths.remove(shaft)

        # Final check to determine if shaft ratio's are correctly defined
        if len(shaft_powerpaths) != len(self.shaft_param):
            labels = {n: G.nodes[n]['name'] for n in G.nodes}
            plt.figure(figsize=(11, 9))
            nx.draw(G, labels=labels, with_labels=True, node_size=500, font_size=15)
            plt.show()
            raise Exception("The number shaft powerpaths that will be assigned a shaft parameter does match the number of shaft parameters")

        return shaft_powerpaths

    def matrix(self):
        """ Function to build a solveable matrix from architecture previously built.
        Uses default values of 0.1 for all control parameters. """

        # Count number of connections in the architecture and add the propulsive lines
        self.connections = 0
        for branch in self.branches.values():
            self.connections += len(branch) - 1
        self.connections+= self.prop_lines

        # Define empty matrices
        A_obj = np.empty((self.connections, self.connections), dtype=object)
        A_obj[:, :] = 0.0

        # List for appending input and output component to each powerpath
        powerpaths = []

        # List for appending each component
        self.components = []

        # List for appending each energy source
        self.energy_sources = []

        # Append components and powerpaths
        first_iteration = True

        # Loop over each component
        for id in range(0,self._next_id+1):
            # Components may occur more than once due to branching
            unique_component = True
            # Loop over each branch
            for branch_id, branch in enumerate(self.branches.values()):
                new_branch = True
                # Loop over each component in the branch
                for component_id, component in enumerate(branch):
                    # Only need to append powerpaths once
                    if first_iteration == True:
                        # Last component in the branch
                        if component_id == len(branch)-1:
                            # If last component is the propeller append the powerpath after the propeller
                            if component.name == 'Propeller':
                                powerpaths.append([branch_id, component])
                        else:
                            # For each powerpath instance define the branch id, component and consecutive component
                            powerpaths.append([branch_id, component, branch[component_id+1]])
                    # Find all components to use in the matrix
                    if component.id == id and unique_component == True:
                        # Skip over energy sources as these are not included in the matrix
                        if component.type != 'energy_source':
                            unique_component = False
                            # Append component
                            self.components.append([branch_id, component])
                        else:
                            # Append energy source
                            self.energy_sources.append([branch_id, component])
            first_iteration = False

        # Initialize the supply and shaft parameters
        self.supply_param = Control_parameters(len(self.energy_sources)-1)
        self.shaft_param = Control_parameters(self.connections - len(self.components) - len(self.supply_param) - 1)

        # Set an initial value to each supply parameter
        for i in range(0, len(self.supply_param)):
            self.supply_param.set(i, 0.1)

        # Set an initial value to each shaft parameter
        for i in range(0, len(self.shaft_param)):
            self.shaft_param.set(i, 0.1)

        # Define the primary energy source and shaft powerpaths
        self.primary_paths()

        # Build the component rows of the matrix
        for row, comp in enumerate(self.components):
            for column, powerpath in enumerate(powerpaths):
                try:
                    # If the powerpath output is equal to the component: The matrix entry is the negative efficiency of the component
                    if powerpath[2].id == comp[1].id:
                        A_obj[row, column] = -comp[1].efficiency
                    # If the powerpath input is equal to the component: The matrix entry is 1
                    elif powerpath[1].id == comp[1].id:
                        A_obj[row, column] = 1
                except:
                    # If the powerpath is the one after the propeller: The matrix entry is 1
                    if powerpath[1].id == comp[1].id:
                        A_obj[row, column] = 1

        # Build the supply ratio rows of the matrix
        supply_column = []

        # Loop over the number of rows where the supply parameters need to be defined
        for row in range(len(self.components), len(self.components)+len(self.supply_param)):
            primary_source = False
            supply = False
            for column, powerpath in enumerate(powerpaths):
                # Ratio's only occur if the input component of a powerpath is an energy source
                if powerpath[1].type == 'energy_source':
                    # If the ratio has already been defined for that powerpath then only define the ratio
                    if column in supply_column:
                        A_obj[row, column] = self.supply_param.slot(row - len(self.components))
                    # If the powerpath is the primary source then only define ratio
                    elif powerpath[1].id == self.primary_source.id and primary_source == False:
                        A_obj[row, column] = self.supply_param.slot(row - len(self.components))
                        # When hydrogen is the primary energy source, it may output two powerpaths (GasTurbine and FuelCell)
                        # This boolean ensures that only one powerpath can be the primary one
                        primary_source = True
                    # If a ratio has already been defined in this row, then only define the ratio
                    elif supply == True:
                        A_obj[row, column] = self.supply_param.slot(row - len(self.components))
                    # If all of the above are false, then define the ratio minus 1. This supply parameter then defines
                    # the power of this powerpath over the total power of all the powerpaths from an energy source
                    else:
                        A_obj[row, column] = (self.supply_param.offset(row - len(self.components), -1))
                        supply = True
                        supply_column.append(column)

        # Function that defines which powerpaths should have a shaft ratio defined
        shaft_powerpaths = self.shaft_ratios(powerpaths)

        # Build the shaft ratio rows of the matrix
        shaft_column = []
        # Loop over the number of rows where the shaft parameters need to be defined
        for row in range(len(self.components)+len(self.supply_param), len(self.components)+len(self.shaft_param)+len(self.supply_param)):
            shaft = False
            # Loop over each powerpath in each row
            for column, powerpath in enumerate(powerpaths):
                try:
                    # The shaft powerpath always end in a propeller
                    if powerpath[2].name == 'Propeller':
                        # If the ratio has already been defined for that powerpath then only define the ratio
                        if column in shaft_column:
                            A_obj[row, column] = self.shaft_param.slot(row - len(self.components) - len(self.supply_param))
                        # If the powerpath is the primary shaft then only define ratio
                        elif powerpath[2].id == self.primary_shaft.id:
                            A_obj[row, column] = self.shaft_param.slot(row - len(self.components) - len(self.supply_param))
                            shaft_column.append(column)
                        # If a ratio has already been defined in this row, then only define the ratio
                        elif shaft == True:
                            A_obj[row, column] = self.shaft_param.slot(row - len(self.components) - len(self.supply_param))
                        # If powerpath needs to be defined, then define the ratio minus 1. This supply parameter then defines
                        # the power of this shaft powerpath over the total power of all the shaft powerpaths
                        elif [powerpath[1].id, powerpath[2].id] in shaft_powerpaths:
                            A_obj[row, column] = (self.shaft_param.offset(row - len(self.components) - len(self.supply_param), -1))
                            shaft_column.append(column)
                            shaft = True
                        # If the above are false, the ratio will never have to be defined for this powerpath, then only define the ratio
                        else:
                            A_obj[row, column] = self.shaft_param.slot(row - len(self.components) - len(self.supply_param))
                            shaft_column.append(column)
                except:
                    pass

        # Build the power equation row of the matrix
        for column, powerpath in enumerate(powerpaths):
            if len(powerpath) == 2:
                A_obj[self.connections-1, column] = 1
        return powerpaths, A_obj, self.components

def combinations(step_size):
    from collections import Counter
    unique_ids = set()
    counts_by_k = Counter()  # How many uniques per control-parameter count k

    for i in range(0, 10000):
        #print('#################### seed:', i, '####################')
        env = Powertrain()
        env.action_space.seed(i)
        random.seed(i)
        obs = env.reset()
        done = False

        while not done:
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
        _, _, _ = env.matrix()

        gid = env.graph_id
        if gid not in unique_ids:
            unique_ids.add(gid)

            # Count control parameters for this unique architecture
            n_c = len(env.supply_param) + len(env.shaft_param)
            counts_by_k[n_c] += 1

        env.close()

    print('Number of unique architectures:', len(unique_ids))
    for k in range(0, len(counts_by_k)):
        print(f'k={k}: {counts_by_k[k]}')

    # Total control-setting combinations at 0.1 resolution (11 values per parameter)
    total_combos = sum(((1/step_size+1) ** k) * c for k, c in counts_by_k.items())
    print('Total control-setting combinations (at 0.1 steps):', total_combos)

def unique_architectures():
    unique_ids = set()
    unique_architectures = []
    unique_actions = []
    energy_sources = []
    max_controls = 0
    max_size = 0
    i = -1
    j = 1
    new_architectures = [4,5,13,14,19,21,23,26,28,42,55,61,66,70,71,76,78,82,87,88,124,160,174,184,243,264]
    unique_configurations = [0, 1, 2, 4, 5, 8, 9, 10, 12, 13, 14, 15, 18, 19, 21, 23, 26, 28, 29, 34, 41, 42, 43, 45,
                             48, 55, 61, 62, 64, 66, 68, 70, 71, 73, 76, 78, 82, 87, 88, 98, 124, 155, 160, 174, 184,
                             243, 257, 264]
    borgia_configurations = [0, 1, 2, 8, 9, 10, 12, 15, 18, 29, 34, 41, 43, 45,
                             48, 62, 64, 68, 73, 98, 155, 257]

    # while len(unique_architectures) < 1:
    #     i += 1
    for i in range(0,3000):
        actions = []
        #print('#################### seed:', i, '####################')
        env = Powertrain()
        env.action_space.seed(i)
        #random.seed(i)
        obs = env.reset()
        done = False

        while not done:
            action = env.action_space.sample()
            actions.append(action)
            obs, reward, done, info = env.step(action)
        powerpaths, matrix, components = env.matrix()

        gid = env.graph_id
        if gid not in unique_ids: # and (len(env.supply_param) + len(env.shaft_param)) > 0:# and env.n_energy_sources == 1:
            print('###################', j)
            j+=1
            env.describe()
            #print(env.energy_source)
            unique_ids.add(gid)
            unique_architectures.append([powerpaths, matrix, components])
            unique_actions.append(actions)
            energy_sources.append(env.energy_source)
            #plt.show()
            #input('Press Enter')
        if matrix.shape[0] > max_size:
            max_size=matrix.shape[0]
        if len(env.supply_param) + len(env.shaft_param) > max_controls:
            max_controls = len(env.supply_param) + len(env.shaft_param)
        env.close()
    #print(i)
    #print(unique_architectures)
    print(len(unique_architectures))
    return unique_actions, energy_sources

def test(n_seeds):
    max_matrix_size = 0
    max_action_size = 0
    for i in range(0, n_seeds):
        #print('#################### seed:', i, '####################')
        env = Powertrain()
        env.action_space.seed(i)

        obs = env.reset()
        done = False

        while not done:
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
        _, matrix, _ = env.matrix()
        if matrix.shape[0] > max_matrix_size:
            max_matrix_size = matrix.shape[0]
        if len(env.shaft_param) + len(env.supply_param) > max_action_size:
            max_action_size = len(env.shaft_param) + len(env.supply_param)

if __name__ == '__main__':
    #combinations(0.1)
    from Characteristics import CHARACTERISTICS2030 as CHARACTERISTICS
    Component.set_characteristics(CHARACTERISTICS)
    unique_actions, energy_sources = unique_architectures()


