import pytest

from gdm.distribution.components import MatrixImpedanceBranch, DistributionBus
from gdm.distribution.components.distribution_feeder import DistributionFeeder
from gdm.distribution.components.distribution_substation import DistributionSubstation
from gdm.distribution.equipment.matrix_impedance_branch_equipment import (
    MatrixImpedanceBranchEquipment,
)
from gdm.quantities import Voltage, Distance
from gdm.quantities import ResistancePULength, ReactancePULength, CapacitancePULength, Current
from gdm.distribution.enums import Phase, VoltageTypes


def _make_bus(name: str, phases: list[Phase], voltage_v: float = 400.0) -> DistributionBus:
    return DistributionBus(
        name=name,
        voltage_type=VoltageTypes.LINE_TO_LINE,
        phases=phases,
        rated_voltage=Voltage(voltage_v, "volt"),
        substation=DistributionSubstation.example(),
        feeder=DistributionFeeder.example(),
    )


def _two_phase_equipment() -> MatrixImpedanceBranchEquipment:
    """2×2 matrix equipment for two-phase [A, B] branches."""
    return MatrixImpedanceBranchEquipment(
        name="2-phase-equipment",
        r_matrix=ResistancePULength([[0.0882, 0.0312], [0.0312, 0.0902]], "ohm/mi"),
        x_matrix=ReactancePULength([[0.2074, 0.0935], [0.0935, 0.2008]], "ohm/mi"),
        c_matrix=CapacitancePULength([[2.903, -0.679], [-0.679, 3.159]], "nanofarad/mi"),
        ampacity=Current(90, "ampere"),
    )


def test_wrong_number_of_buses():
    branch = MatrixImpedanceBranch.example()
    with pytest.raises(ValueError):
        MatrixImpedanceBranch(
            name=branch.name,
            buses=branch.buses + [DistributionBus.example()],
            length=branch.length,
            phases=branch.phases,
            equipment=branch.equipment,
        )


def test_wrong_phase_connection():
    branch = MatrixImpedanceBranch.example()
    with pytest.raises(ValueError):
        MatrixImpedanceBranch(
            name=branch.name,
            buses=branch.buses,
            length=branch.length,
            phases=[Phase.S1, Phase.A, Phase.B],
            equipment=branch.equipment,
        )


def test_same_from_and_to_bus():
    branch = MatrixImpedanceBranch.example()
    with pytest.raises(ValueError):
        MatrixImpedanceBranch(
            name=branch.name,
            buses=[branch.buses[0], branch.buses[0]],
            length=branch.length,
            phases=branch.phases,
            equipment=branch.equipment,
        )


def test_duplicate_phases():
    branch = MatrixImpedanceBranch.example()
    with pytest.raises(ValueError):
        MatrixImpedanceBranch(
            name=branch.name,
            buses=branch.buses,
            length=branch.length,
            phases=[Phase.A, Phase.A, Phase.B],
            equipment=branch.equipment,
        )


def test_connecting_buses_with_different_voltage():
    branch = MatrixImpedanceBranch.example()
    bus1, bus2 = branch.buses
    bus1.rated_voltage = Voltage(12.7, "kilovolts")
    bus2.rated_voltage = Voltage(12.8, "kilovolts")
    with pytest.raises(ValueError):
        MatrixImpedanceBranch(
            name=branch.name,
            buses=[bus1, bus2],
            length=branch.length,
            phases=branch.phases,
            equipment=branch.equipment,
        )


# ---------------------------------------------------------------------------
# Phase count validation tests
# ---------------------------------------------------------------------------


def test_branch_phase_count_matches_both_buses():
    """Branch with same phase count as both buses is valid."""
    branch = MatrixImpedanceBranch.example()
    # The example has 3 phases on branch and both buses — just confirm it validates.
    assert len(branch.phases) == 3


def test_branch_phase_count_matches_one_bus_valid():
    """Branch phase count matching one bus (different count on the other) should be valid."""
    bus1 = _make_bus("bus-ab-1", [Phase.A, Phase.B])
    bus2 = _make_bus("bus-abc-2", [Phase.A, Phase.B, Phase.C])
    branch = MatrixImpedanceBranch(
        name="branch-ab",
        buses=[bus1, bus2],
        length=Distance(100, "meter"),
        phases=[Phase.A, Phase.B],
        substation=DistributionSubstation.example(),
        feeder=DistributionFeeder.example(),
        equipment=_two_phase_equipment(),
    )
    assert len(branch.phases) == 2


def test_branch_phase_count_matches_no_bus_invalid():
    """Branch phase count differing from every connected bus must be rejected."""
    bus1 = _make_bus("bus-abc-1", [Phase.A, Phase.B, Phase.C])
    bus2 = _make_bus("bus-abc-2", [Phase.A, Phase.B, Phase.C])
    with pytest.raises(ValueError, match="Number of branch phases"):
        MatrixImpedanceBranch(
            name="branch-ab-count-mismatch",
            buses=[bus1, bus2],
            length=Distance(100, "meter"),
            phases=[Phase.A, Phase.B],
            substation=DistributionSubstation.example(),
            feeder=DistributionFeeder.example(),
            equipment=_two_phase_equipment(),
        )
