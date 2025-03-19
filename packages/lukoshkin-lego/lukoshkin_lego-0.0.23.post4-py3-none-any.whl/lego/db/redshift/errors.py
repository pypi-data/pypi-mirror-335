"""
Exceptions raised during Redshift query execution with the RedshiftData API.


Currently relies on definitions used in psycopg2.errors and includes only:
- SyntaxError
- AmbiguousColumn
- UndefinedColumn
- GroupingError
- InternalError
"""

import re


class RedshiftQueryAbortedError(Exception):
    """Raise when a Redshift query was aborted"""


class RedshiftDataError(Exception):
    """Base class for RedshiftData errors"""

    error_patterns = [
        (
            "UndefinedColumn",
            re.compile(r'column "(.*?)" does not exist'),
            "pattern",
        ),
        (
            "AmbiguousColumn",
            re.compile(r'column reference "(.*?)" is ambiguous'),
            "pattern",
        ),
        ("SyntaxError", "syntax error at or near", "occurrence"),
        ("GroupingError", "in the GROUP BY clause", "occurrence"),
        ("InternalError", "internal error", "occurrence"),
    ]

    def __init__(self, desc: dict):
        self.desc = desc
        self.message = desc.get("Error", "")
        self.orig = self.classify_error(self.message)
        super().__init__(self.message)

    def classify_error(self, message: str) -> "RedshiftDataError":
        for error_type, pattern, kind in self.error_patterns:
            if kind == "pattern" and pattern.search(message):
                return globals()[error_type](self.desc)
            if kind == "occurrence" and pattern in message:
                return globals()[error_type](self.desc)
        return UnknownError(self.desc)


class UnknownError(RedshiftDataError):
    """Raise when an unknown error occurs"""


class SyntaxError(RedshiftDataError):
    """Raise when a syntax error occurs"""


class AmbiguousColumn(RedshiftDataError):
    """Raise when a column reference is ambiguous"""


class UndefinedColumn(RedshiftDataError):
    """Raise when a column does not exist"""
