"""
Unit tests for utils/validators.py.

These need no database and no network — pure function tests. Run with:
    pytest tests/test_validators.py -v
"""
import pytest
from utils.validators import (
    validate_update_payload, validate_marks,
    validate_section, validate_semester
)
from utils.exceptions import ValidationError


class TestValidateUpdatePayload:
    def test_allows_whitelisted_columns(self):
        result = validate_update_payload("students", {"name": "Aarav", "section": "B"})
        assert result == {"name": "Aarav", "section": "B"}

    def test_rejects_unknown_column(self):
        with pytest.raises(ValidationError, match="student_id"):
            validate_update_payload("students", {"student_id": "STU999"})

    def test_rejects_unknown_table(self):
        with pytest.raises(ValidationError, match="Unknown table"):
            validate_update_payload("marks", {"marks_obtained": 90})

    def test_empty_updates_ok(self):
        assert validate_update_payload("teachers", {}) == {}

    def test_does_not_mutate_input(self):
        original = {"name": "X"}
        validate_update_payload("students", original)
        assert original == {"name": "X"}  # unchanged


class TestValidateMarks:
    def test_valid_marks_pass(self):
        validate_marks(87.5, 100)  # should not raise

    def test_marks_above_max_rejected(self):
        with pytest.raises(ValidationError, match="between 0 and 100"):
            validate_marks(150, 100)

    def test_negative_marks_rejected(self):
        with pytest.raises(ValidationError):
            validate_marks(-5, 100)

    def test_non_numeric_rejected(self):
        with pytest.raises(ValidationError, match="numeric"):
            validate_marks("abc", 100)

    def test_none_rejected(self):
        with pytest.raises(ValidationError, match="required"):
            validate_marks(None, 100)

    def test_boundary_zero_and_max_allowed(self):
        validate_marks(0, 100)
        validate_marks(100, 100)


class TestValidateSection:
    @pytest.mark.parametrize("section", ["A", "B", "C", "D"])
    def test_valid_sections(self, section):
        validate_section(section)  # should not raise

    def test_invalid_section_rejected(self):
        with pytest.raises(ValidationError):
            validate_section("E")


class TestValidateSemester:
    @pytest.mark.parametrize("sem", [1, 2, 3, 4])
    def test_valid_semesters(self, sem):
        validate_semester(sem)

    def test_invalid_semester_rejected(self):
        with pytest.raises(ValidationError):
            validate_semester(5)