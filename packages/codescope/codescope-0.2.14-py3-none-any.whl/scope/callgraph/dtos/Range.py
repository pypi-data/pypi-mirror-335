# Local
from scope.callgraph.utils import stable_hash


class Range(object):
    def __init__(self, start_line, start_column, end_line, end_column):
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __eq__(self, other):
        if not isinstance(other, Range):
            return NotImplemented

        start_line_eq = self.start_line == other.start_line
        start_col_eq = self.start_column == other.start_column
        end_line_eq = self.end_line == other.end_line
        end_col_eq = self.end_column == other.end_column
        return all([start_line_eq, start_col_eq, end_line_eq, end_col_eq])

    def contains(self, other) -> bool:
        if not isinstance(other, Range):
            return NotImplemented
        return (
            self.start_line <= other.start_line
            and self.end_line >= other.end_line
            and (
                self.start_line < other.start_line
                or (
                    self.start_line == other.start_line
                    and self.start_column <= other.start_column
                )
            )
            and (
                self.end_line > other.end_line
                or (
                    self.end_line == other.end_line
                    and self.end_column >= other.end_column
                )
            )
        )

    def __hash__(self):
        return stable_hash(
            {
                "start_line": self.start_line,
                "start_column": self.start_column,
                "end_line": self.end_line,
                "end_column": self.end_column,
            },
            as_int=True,
        )

    def __str__(self):
        return f"Range([{self.start_line}:{self.start_column}] - [{self.end_line}:{self.end_column}])"

    def to_dict(self):
        return {
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }

    def to_list(self):
        return [self.start_line, self.start_column, self.end_line, self.end_column]

    def invalid(self):
        start_line_invalid = self.start_line == -1
        start_col_invalid = self.start_column == -1
        end_line_invalid = self.end_line == -1
        end_col_invalid = self.end_column == -1
        return any(
            [
                start_line_invalid,
                start_col_invalid,
                end_line_invalid,
                end_col_invalid,
            ]
        )

    def height(self):
        return self.end_line - self.start_line

    def width(self):
        return max(self.end_column, self.start_column)
