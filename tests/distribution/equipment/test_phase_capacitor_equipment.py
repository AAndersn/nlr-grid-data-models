from gdm.distribution.equipment import PhaseCapacitorEquipment
from gdm.quantities import Reactance, ReactivePower, Resistance


def test_phase_capacitor_aggregate_all_zero_impedance_returns_zero():
    capacitors = [
        PhaseCapacitorEquipment(
            name="cap_1",
            rated_reactive_power=ReactivePower(100, "kvar"),
            resistance=Resistance(0, "ohm"),
            reactance=Reactance(0, "ohm"),
            num_banks=1,
            num_banks_on=1,
        ),
        PhaseCapacitorEquipment(
            name="cap_2",
            rated_reactive_power=ReactivePower(50, "kvar"),
            resistance=Resistance(0, "ohm"),
            reactance=Reactance(0, "ohm"),
            num_banks=1,
            num_banks_on=1,
        ),
    ]

    aggregated = PhaseCapacitorEquipment.aggregate(capacitors, "cap_total")

    assert aggregated.resistance.to("ohm").magnitude == 0
    assert aggregated.reactance.to("ohm").magnitude == 0
    assert aggregated.rated_reactive_power.to("kvar").magnitude == 150
