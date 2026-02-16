"""Builder functions for mock distribution systems used in MCP tests."""

from gdm.distribution import DistributionSystem
from gdm.distribution.components import (
    DistributionBus,
    DistributionFeeder,
    DistributionSubstation,
)
from gdm.distribution.enums import VoltageTypes
from gdm.quantities import Voltage


def build_simple_system() -> DistributionSystem:
    """Build a simple distribution system with one substation, one feeder, and two buses.

    Total components: 4 (substation, feeder, bus1, bus2)
    """
    system = DistributionSystem(name="test_system", auto_add_composed_components=True)

    feeder = DistributionFeeder(name="feeder1")
    substation = DistributionSubstation(name="sub1", feeders=[feeder])

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

    system.add_component(substation)
    system.add_component(bus1)
    system.add_component(bus2)

    return system


def build_multi_substation_system() -> DistributionSystem:
    """Build a system with multiple substations and feeders.

    Structure: 2 substations x 2 feeders x 3 buses = 12 buses + 4 feeders + 2 substations = 18 components
    """
    system = DistributionSystem(name="multi_sub_system", auto_add_composed_components=True)

    for sub_idx in range(1, 3):
        feeders = []
        for feeder_idx in range(1, 3):
            feeders.append(DistributionFeeder(name=f"feeder{sub_idx}_{feeder_idx}"))

        substation = DistributionSubstation(name=f"sub{sub_idx}", feeders=feeders)

        for feeder in feeders:
            for bus_idx in range(1, 4):
                bus = DistributionBus(
                    name=f"bus_{sub_idx}_{feeders.index(feeder) + 1}_{bus_idx}",
                    phases=["A", "B", "C"],
                    voltage_type=VoltageTypes.LINE_TO_LINE,
                    rated_voltage=Voltage(12.47, "kV"),
                    substation=substation,
                    feeder=feeder,
                )
                system.add_component(bus)

    return system
