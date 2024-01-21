import dataclasses
import typing
from collections import abc

from chameleon.step.core import context as ctx
from chameleon.step.core.doc import create_field

__all__ = [
    "UrlHandlerSteps",
    "UrlHandler",
    "StepHandlerProtocol",
]


@typing.runtime_checkable
class StepHandlerProtocol(typing.Protocol):
    async def __call__(self, context: ctx.StepContext) -> bool | None:
        ...


@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class UrlHandlerProcessSteps:
    # framework-specific
    fill_request_info: StepHandlerProtocol | None = create_field(
        doc="""Extracts basic request info to minimize dependency from framework."""
    )  # type: ignore[assignment]

    # framework-specific
    check_authenticated: StepHandlerProtocol | None = create_field(
        doc="""Check if a user authenticated e.g. auth token is valid."""
    )  # type: ignore[assignment]

    # framework-specific
    check_headers: StepHandlerProtocol | None = create_field(
        doc="""Check request headers are expected."""
    )  # type: ignore[assignment]
    check_access_pre_read: StepHandlerProtocol | None = create_field(
        doc="""Check a requester has an access to that resource"
         "(body hasn't been read)."""
    )  # type: ignore[assignment]

    # framework-specific
    extract_body: StepHandlerProtocol | None = create_field(
        doc="""Extract body from the request layer."""
    )  # type: ignore[assignment]

    decrypt: StepHandlerProtocol | None = create_field(
        doc="""Optional decryption and/or signature check of the request_body."""
    )  # type: ignore[assignment]

    # could be generated from default impl
    deserialize: StepHandlerProtocol | None = create_field(
        doc="""Deserialize request body to the input_raw."""
    )  # type: ignore[assignment]

    # could be generated from default impl
    validate_input: StepHandlerProtocol | None = create_field(
        doc="""Validate input_raw and/or request body."""
    )  # type: ignore[assignment]

    check_access_post_read: StepHandlerProtocol | None = create_field(
        doc="""Check a requester has an access to that resource (body has been read)."""
    )  # type: ignore[assignment]

    # could be generated from default impl
    map_input: StepHandlerProtocol | None = create_field(
        doc="""Map input_raw to the internal representation to be processed."""
    )  # type: ignore[assignment]

    business: StepHandlerProtocol | None = create_field(
        doc="""Endpoint business part. Could be database handling and/or"""
        """sending another request somewhere else"""
    )  # type: ignore[assignment]

    # could be generated from default impl
    map_output: StepHandlerProtocol | None = create_field(
        doc="""Map output_business to the raw representation to be serialized."""
    )  # type: ignore[assignment]

    def process_order(self):
        """Intended execution order."""
        return (
            ("fill_request_info", self.fill_request_info),
            ("check_authenticated", self.check_authenticated),
            ("check_headers", self.check_headers),
            ("check_access_pre_read", self.check_access_pre_read),
            ("extract_body", self.extract_body),
            ("decrypt", self.decrypt),
            ("deserialize", self.deserialize),
            ("validate_input", self.validate_input),
            ("check_access_post_read", self.check_access_post_read),
            ("map_input", self.map_input),
            ("business", self.business),
            ("map_output", self.map_output),
        )


@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class UrlHandlerSteps(UrlHandlerProcessSteps):
    exception_handler: StepHandlerProtocol | None = create_field(
        doc="""Handle an exception."""
    )  # type: ignore[assignment]

    serialize: StepHandlerProtocol | None = create_field(
        doc="""Serialize output_raw to be passed for transport layers."""
    )  # type: ignore[assignment]

    encrypt: StepHandlerProtocol | None = create_field(
        doc="""Optional encryption, signing, etc."""
    )  # type: ignore[assignment]

    response_headers: StepHandlerProtocol | None = create_field(
        doc="""Prepare additional response headers."""
    )  # type: ignore[assignment]

    # framework-specific
    create_response: StepHandlerProtocol | None = create_field(
        doc="""Create HTTP response to be returned."""
    )  # type: ignore[assignment]

    def response_order(self):
        """Intended response preparation order."""
        return (
            ("serialize", self.serialize),
            ("encrypt", self.encrypt),
            ("response_headers", self.response_headers),
            ("create_response", self.create_response),
        )


def defined_steps(
    steps: abc.Sequence[tuple[str, StepHandlerProtocol | None]],
) -> abc.Iterable[tuple[str, StepHandlerProtocol]]:
    return (step for step in steps if step[1] is not None)  # type: ignore[misc]


async def default_exception_handler(context: ctx.StepContext):
    return False


async def call_steps(
    context: ctx.StepContext, steps: tuple[tuple[str, StepHandlerProtocol], ...]
):
    for current_step, step_handler in steps:
        context.current_step = current_step
        await step_handler(context)


class UrlHandler:
    process_steps: tuple[tuple[str, StepHandlerProtocol], ...]
    error_status_to_http: abc.Mapping[int, int]
    response_steps: tuple[tuple[str, StepHandlerProtocol], ...]

    def __init__(
        self, *, steps: UrlHandlerSteps, error_status_to_http: abc.Mapping[int, int]
    ):
        self.error_status_to_http = error_status_to_http
        self.process_steps = tuple(defined_steps(steps.process_order()))
        self.exception_handler = steps.exception_handler or default_exception_handler
        self.response_steps = tuple(defined_steps(steps.response_order()))

    async def __call__(
        self, request: typing.Any, **url_params: typing.Any
    ) -> typing.Any:
        context: ctx.StepContext = ctx.StepContext(
            request_info=ctx.StepContextRequestInfo(request=request),
            custom_info=url_params,
            error_status_to_http=self.error_status_to_http,
        )

        try:
            await call_steps(context, self.process_steps)
        except Exception as e:  # pylint: disable=W0718
            context.exception = e
            if not await self.exception_handler(context):
                raise  # re-raise the exception if not handled

        await call_steps(context, self.response_steps)
        return context.response
