import re
from dataclasses import dataclass

@dataclass
class Column:
    name: str
    cast_type: str
    line_no: int

CAST_REGEX = re.compile(
    r"cast\s*\(.*?\s+as\s+(\w+)\)\s+as\s+(\w+)",
    re.IGNORECASE
)

def parse_sqlx(sql: str):
    columns = []
    for i, line in enumerate(sql.splitlines(), start=1):
        match = CAST_REGEX.search(line)
        if match:
            cast_type, alias = match.groups()
            columns.append(Column(
                name=alias,
                cast_type=cast_type.lower(),
                line_no=i
            ))
    return columns
