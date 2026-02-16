"""Suggestion generator for validation error fixes."""

from gdm.mcp.schemas import (
    ConfidenceLevel,
    ErrorType,
    FixStrategy,
    FixSuggestion,
    ValidationReport,
)


def suggest_fixes(report: ValidationReport) -> list[FixSuggestion]:
    """
    Generate fix suggestions for validation issues.

    Args:
        report: ValidationReport with identified issues

    Returns:
        List of FixSuggestion objects
    """
    suggestions = []

    for issue in report.issues:
        if issue.error_type == ErrorType.PHASE_MISMATCH:
            suggestion = _suggest_phase_fix(issue)
        elif issue.error_type == ErrorType.MATRIX_DIMENSION:
            suggestion = _suggest_matrix_fix(issue)
        elif issue.error_type == ErrorType.ARRAY_LENGTH:
            suggestion = _suggest_array_fix(issue)
        elif issue.error_type == ErrorType.MISSING_REFERENCE:
            suggestion = _suggest_reference_fix(issue)
        else:
            # For other error types, suggest manual review
            suggestion = FixSuggestion(
                issue=issue,
                strategy=FixStrategy.REMOVE_INVALID,
                description="Manual review required for this error type",
                confidence=ConfidenceLevel.LOW,
                risk_level="high",
            )

        if suggestion:
            suggestions.append(suggestion)

    return suggestions


def _suggest_phase_fix(issue) -> FixSuggestion:
    """Suggest fix for phase mismatch issues."""
    # Align component phases to expected (bus) phases
    return FixSuggestion(
        issue=issue,
        strategy=FixStrategy.ALIGN_PHASES,
        description=f"Align component phases to match expected phases: {issue.expected_value}",
        parameters={
            "new_phases": issue.expected_value,
            "old_phases": issue.current_value,
        },
        confidence=ConfidenceLevel.HIGH,
        risk_level="low",
    )


def _suggest_matrix_fix(issue) -> FixSuggestion:
    """Suggest fix for matrix dimension issues."""
    # Parse expected dimensions
    expected = str(issue.expected_value).replace("x", "x")
    current = str(issue.current_value).replace("x", "x")

    return FixSuggestion(
        issue=issue,
        strategy=FixStrategy.RESIZE_MATRIX,
        description=f"Resize matrix from {current} to {expected}. Will pad with zeros or truncate as needed.",
        parameters={
            "expected_dimensions": issue.expected_value,
            "current_dimensions": issue.current_value,
        },
        confidence=ConfidenceLevel.MEDIUM,
        risk_level="medium",
    )


def _suggest_array_fix(issue) -> FixSuggestion:
    """Suggest fix for array length issues."""
    return FixSuggestion(
        issue=issue,
        strategy=FixStrategy.ADJUST_ARRAY_LENGTH,
        description=f"Adjust array length from {issue.current_value} to {issue.expected_value}. Will pad with defaults or truncate.",
        parameters={
            "expected_length": issue.expected_value,
            "current_length": issue.current_value,
        },
        confidence=ConfidenceLevel.MEDIUM,
        risk_level="medium",
    )


def _suggest_reference_fix(issue) -> FixSuggestion:
    """Suggest fix for missing reference issues."""
    return FixSuggestion(
        issue=issue,
        strategy=FixStrategy.SET_DEFAULT,
        description="Set reference to None or default value. Manual review recommended.",
        parameters={},
        confidence=ConfidenceLevel.LOW,
        risk_level="high",
    )
