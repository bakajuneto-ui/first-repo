"""
Input validation helpers.
"""

from utils.exceptions import ValidationError

# NOTE: 'teachers' no longer includes subject_code/section — those moved
# to the teacher_assignments join table and are managed via
# assign_subject_to_teacher() / unassign_subject_from_teacher(), not by
# updating the teachers row directly.
ALLOWED_UPDATE_COLUMNS = {
    "students": {"name", "username", "password", "roll_number",
                 "section", "year", "semester", "email"},
    "teachers": {"name", "username", "password", "email"},
    "subjects": {"name", "code", "semester", "max_marks"},
}


def validate_update_payload(table: str, updates: dict) -> dict:
    allowed = ALLOWED_UPDATE_COLUMNS.get(table)
    if allowed is None:
        raise ValidationError(f"Unknown table '{table}' for update validation.")
    unknown = set(updates) - allowed
    if unknown:
        raise ValidationError(
            f"Cannot update column(s) {sorted(unknown)} on '{table}'. "
            f"Allowed: {sorted(allowed)}"
        )
    return dict(updates)


def validate_marks(marks_obtained: float, max_marks: int) -> None:
    if marks_obtained is None:
        raise ValidationError("Marks value is required.")
    try:
        marks_obtained = float(marks_obtained)
    except (TypeError, ValueError):
        raise ValidationError(f"Marks must be numeric, got {marks_obtained!r}.")
    if not (0 <= marks_obtained <= max_marks):
        raise ValidationError(f"Marks must be between 0 and {max_marks}.")


def validate_section(section: str) -> None:
    if section not in {"A", "B", "C", "D"}:
        raise ValidationError(f"Section must be one of A/B/C/D, got {section!r}.")


def validate_semester(semester: int) -> None:
    if semester not in {1, 2, 3, 4}:
        raise ValidationError(f"Semester must be 1-4, got {semester!r}.")