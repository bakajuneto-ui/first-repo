"""
Custom exception hierarchy for MCA Score Analyzer.

Why this exists: raw oracledb.DatabaseError leaking up to a Streamlit page
means every caller has to know Oracle internals to handle failure. These
wrap that away so pages can catch one thing (AppError) and show a message,
while lower layers can still distinguish *why* it failed.
"""


class AppError(Exception):
    """Base class for all application-raised errors."""


class ValidationError(AppError):
    """Raised when input data fails a business rule before it reaches the DB.

    e.g. marks outside [0, max_marks], duplicate username, unknown column
    in an update payload.
    """


class NotFoundError(AppError):
    """Raised when a lookup by id/username finds no matching row."""


class DuplicateError(AppError):
    """Raised when a uniqueness constraint would be violated
    (username, roll number, subject code, etc.)."""


class DatabaseUnavailableError(AppError):
    """Raised when the Oracle pool cannot be reached at all.

    Kept distinct from ValidationError/NotFoundError because the caller's
    response should be different: retry / show a connection banner, not
    a form error.
    """