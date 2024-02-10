import dataclasses


@dataclasses.dataclass
class ErrorItem:
    code: int
    message: str
    field: str | None


@dataclasses.dataclass
class Error:
    errors: ErrorItem
