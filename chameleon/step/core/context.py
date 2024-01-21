import dataclasses
import typing
from collections import abc

from chameleon.step.core.doc import create_field

__all__ = ["StepContextRequestInfo", "StepContext"]


@dataclasses.dataclass(slots=True, kw_only=True)
class StepContextRequestInfo:
    """Request information for processing context."""

    request: typing.Any = create_field(
        doc="""HTTP request to obtain data from.""",
        default=dataclasses.MISSING,
    )
    method: str = create_field(
        doc="""HTTP request method.""",
    )  # type: ignore[assignment]

    content_type: str | bytes | None = create_field(
        doc="""Request content type.""",
    )  # type: ignore[assignment]

    content_encoding: str | None = create_field(
        doc="""Request content encoding.""",
    )  # type: ignore[assignment]


@dataclasses.dataclass(slots=True, kw_only=True)
class StepContext:
    """Processing context."""

    request_info: StepContextRequestInfo = create_field(
        doc="""Basic request information based on request headers.""",
        default=dataclasses.MISSING,
    )  # type: ignore[assignment]

    request_body: str | bytes = create_field(
        doc="""Request body.""",
    )  # type: ignore[assignment]

    input_raw: typing.Any = create_field(
        doc="""Raw parsed input based on request body and headers."""
    )  # type: ignore[assignment]

    input_business: typing.Any = create_field(
        doc="""Business input based on raw input."""
    )  # type: ignore[assignment]

    output_business: typing.Any = create_field(
        doc="""Business output data based on business input."""
    )  # type: ignore[assignment]

    exception: Exception = create_field(
        doc="""Exception occurred on previous steps.""",
    )  # type: ignore[assignment]

    current_step: str = create_field(
        doc="""Current step name based for exception handler."""
    )  # type: ignore[assignment]

    error_status: int = create_field(
        doc="""Application error status.""",
        default=0,
    )  # type: ignore[assignment]

    error_status_to_http: abc.Mapping[int, int] = create_field(
        doc="""Mapping from Application Errors to HTTP errors.""",
        default=dataclasses.MISSING,
    )  # type: ignore[assignment]

    output_raw: typing.Any = create_field(
        doc="""Raw output to be serialized.""",
    )  # type: ignore[assignment]

    response_body: bytes = create_field(
        doc="""Serialized response body.""",
    )  # type: ignore[assignment]

    response_headers: abc.MutableMapping[str, str] = create_field(
        doc="""Additional response headers."""
    )  # type: ignore[assignment]

    response: typing.Any = create_field(
        doc="""Final response object.""",
    )  # type: ignore[assignment]

    custom_info: abc.MutableMapping[str, typing.Any] = create_field(
        doc="""Custom information if needed."""
    )  # type: ignore[assignment]
