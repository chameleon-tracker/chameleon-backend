import dataclasses
import typing

from chameleon.step.core.doc import create_field

__all__ = ["StepContextRequestInfo", "StepContext"]


@dataclasses.dataclass(slots=True, kw_only=True)
class StepContextRequestInfo:
    """Request information for processing context."""

    request: typing.Any = create_field(
        doc="""HTTP request to obtain data from.""",
        default=dataclasses.MISSING,
    )
    method: str = create_field(doc="""HTTP request method.""")

    content_type: str | bytes = create_field(doc="""Request content type.""")

    content_encoding: str = create_field(doc="""Request content encoding.""")


@dataclasses.dataclass(slots=True, kw_only=True)
class StepContext:
    """Processing context."""

    request_info: StepContextRequestInfo = create_field(
        doc="""Basic request information based on request headers.""",
        default=dataclasses.MISSING,
    )

    request_body: str | bytes = create_field(doc="""Request body.""")

    input_raw: typing.Any = create_field(
        doc="""Raw parsed input based on request body and headers."""
    )

    input_business: typing.Any = create_field(
        doc="""Business input based on raw input."""
    )

    output_business: typing.Any = create_field(
        doc="""Business output data based on business input."""
    )

    exception: Exception = create_field(doc="""Exception occurred on previous steps.""")

    current_step: str = create_field(
        doc="""Current step name based for exception handler."""
    )

    error_status: int = create_field(
        doc="""Application error status.""",
        default=0,
    )

    error_status_to_http: typing.Mapping[int, int] = create_field(
        doc="""Mapping from Application Errors to HTTP errors.""",
        default=dataclasses.MISSING,
    )

    output_raw: typing.Any = create_field(doc="""Raw output to be serialized.""")

    response_body: bytes = create_field(doc="""Serialized response body.""")

    response_headers: typing.MutableMapping[str, str] = create_field(
        doc="""Additional response headers."""
    )

    response: typing.Any = create_field(doc="""Final response object.""")

    custom_info: typing.MutableMapping[str, typing.Any] = create_field(
        doc="""Custom information if needed."""
    )
