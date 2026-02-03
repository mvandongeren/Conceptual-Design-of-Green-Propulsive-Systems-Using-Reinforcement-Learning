from dataclasses import dataclass
from typing import ClassVar, Dict, List, Type, Any

"""
CHARACTERISTICS: Dict[str, Dict[str, Any]] = {
    'KeroseneStorage': {
        'grav_energy_density': 42.0,      # MJ/kg
        'grav_energy_density_fuel': 43.2, # MJ/kg
        'vol_energy_density': 34.56,      # MJ/L
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
        'grav_power_density': 4.0,     # kW/kg
        'vol_power_density': 0,
        'efficiency': 0.3,             # -
        'successors': ['GearBox'],
        'multiple': False
    },
    'FuelCell': {
        'grav_energy_density': 0,
        'vol_energy_density': 0,
        'grav_power_density': 1.25,    # kW/kg      # 0.8
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
"""

@dataclass
class Component:
    """
    Base dataclass for all components.
    Registers subclasses by semantic type, assigns characteristics and successors.
    """
    # Registry mapping semantic type to list of subclasses
    registry: ClassVar[Dict[str, List[Type['Component']]]] = {}
    # Registry mapping class name to class for successor lookup
    name_registry: ClassVar[Dict[str, Type['Component']]] = {}
    _characteristics: ClassVar[Dict] = {}

    @classmethod
    def set_characteristics(cls, char_dict: Dict[str, Dict[str, Any]]):
        cls._characteristics = char_dict
        # automatically assign to all subclasses
        for sub_cls in cls.name_registry.values():
            data = cls._characteristics.get(sub_cls.__name__, {})
            sub_cls._spec_keys = []
            for key, val in data.items():
                if key == "successors":
                    continue
                setattr(sub_cls, key, val)
                sub_cls._spec_keys.append(key)
            sub_cls._successor_names = data.get("successors", [])
            sub_cls.multiple = data.get("multiple", False)

    def __init_subclass__(cls, type: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register semantic type
        if type:
            cls.type = type
            Component.registry.setdefault(type, []).append(cls)
        # Map name to class
        Component.name_registry[cls.__name__] = cls
        # defer attribute assignment
        cls._spec_keys = []
        cls._successor_names = []
        cls.multiple = False
        # Load data
        data = cls._characteristics.get(cls.__name__, {})
        # Assign spec keys and class attributes
        cls._spec_keys = []
        for key, val in data.items():
            if key == 'successors':
                continue
            setattr(cls, key, val)
            cls._spec_keys.append(key)
        # Store successor names for later resolution
        cls._successor_names = data.get('successors', [])
        cls.multiple = data.get('multiple', False)

    @classmethod
    def get_components_by_type(cls, type: str) -> List[Type['Component']]:
        """Return all component classes of a given type."""
        return cls.registry.get(type, [])

    @classmethod
    def get_successors(cls, comp_cls: Type['Component']) -> List[Type['Component']]:
        """Return concrete component classes that can follow comp_cls by resolving names."""
        names = getattr(comp_cls, '_successor_names', [])
        return [cls.name_registry[name] for name in names if name in cls.name_registry]

    def info(self) -> str:
        """Return a human-readable summary of the component's specs."""
        parts = [f"{key}={getattr(self, key)}" for key in self.__class__._spec_keys]
        return f"{self.__class__.__name__}: " + ", ".join(parts)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def type(self) -> str:
        return getattr(self.__class__, "type", None)

    @property
    def efficiency(self) -> str:
        return getattr(self.__class__, "efficiency", None)

# Concrete component subclasses
@dataclass
class KeroseneStorage(Component, type='energy_source'):
    """Hydrocarbon fuel tank."""
    pass

@dataclass
class HydrogenStorage(Component, type='energy_source'):
    """Cryogenic hydrogen tank."""
    pass

@dataclass
class Battery(Component, type='energy_source'):
    """Electrochemical energy storage."""
    pass

@dataclass
class GasTurbine(Component, type='energy_to_work'):
    """Gas turbine engine."""
    pass

@dataclass
class FuelCell(Component, type='energy_to_work'):
    """Hydrogen PEM Fuel Cell."""
    pass

@dataclass
class ElectricMachine(Component, type='converter'):
    """Electric motor or generator."""
    pass

@dataclass
class GearBox(Component, type='converter'):
    """Gearbox to manage RPM of gas turbine and electric generator."""
    pass

@dataclass
class PowerManagement(Component, type='converter'):
    """Power management and distribution unit."""
    pass

@dataclass
class Propeller(Component, type='thrust_producer'):
    """Propeller to produce thrust."""
    pass
