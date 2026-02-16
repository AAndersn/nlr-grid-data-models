"""Pytest configuration and fixtures."""

import pytest
from gdm.distribution import DistributionSystem
from gdm.distribution.components import DistributionBus, DistributionFeeder, DistributionSubstation
from gdm.distribution.enums import VoltageTypes
from gdm.quantities import Voltage


@pytest.fixture
def simple_system():
    """Create a simple test distribution system."""
    system = DistributionSystem(name="test_system", auto_add_composed_components=True)

    # Create substation and feeder
    feeder = DistributionFeeder(name="feeder1")
    substation = DistributionSubstation(name="sub1", feeders=[feeder])
    substation.feeders.append(feeder)

    # Create buses
    bus1 = DistributionBus(
        name="bus1",
        phases=["A", "B", "C"],
        voltage_type=VoltageTypes.LINE_TO_LINE,
        rated_voltage=Voltage(12.47, "kV"),
        substation=substation,
        feeder=feeder,
    )
    bus2 = DistributionBus(
        name="bus2",
        phases=["A", "B", "C"],
        voltage_type=VoltageTypes.LINE_TO_LINE,
        rated_voltage=Voltage(12.47, "kV"),
        substation=substation,
        feeder=feeder,
    )

    # Add components to system
    system.add_component(substation)
    system.add_component(bus1)
    system.add_component(bus2)

    return system


@pytest.fixture
def multi_substation_system():
    """Create a system with multiple substations."""
    system = DistributionSystem(name="multi_sub_system", auto_add_composed_components=True)

    # Create two substations with feeders
    for sub_idx in range(1, 3):
        substation = DistributionSubstation(name=f"sub{sub_idx}", feeders=[])

        for feeder_idx in range(1, 3):
            feeder = DistributionFeeder(name=f"feeder{sub_idx}_{feeder_idx}")
            substation.feeders.append(feeder)

            # Create buses for this feeder
            for bus_idx in range(1, 4):
                bus = DistributionBus(
                    name=f"bus_{sub_idx}_{feeder_idx}_{bus_idx}",
                    phases=["A", "B", "C"],
                    voltage_type=VoltageTypes.LINE_TO_LINE,
                    rated_voltage=Voltage(12.47, "kV"),
                    substation=substation,
                    feeder=feeder,
                )
                system.add_component(bus)

        # Don't add substation explicitly - it's auto-added when buses are added

    return system
