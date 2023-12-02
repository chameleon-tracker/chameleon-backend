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
    )

    # framework-specific
    check_authenticated: StepHandlerProtocol | None = create_field(
        doc="""Check if a user authenticated e.g. auth token is valid."""
    )

    # framework-specific
    check_headers: StepHandlerProtocol | None = create_field(
        doc="""Check request headers are expected."""
    )
    check_access_pre_read: StepHandlerProtocol | None = create_field(
        doc="""Check a requester has an access to that resource"
         "(body hasn't been read)."""
    )

    # framework-specific
    extract_body: StepHandlerProtocol | None = create_field(
        doc="""Extract body from the request layer."""
    )

    decrypt: StepHandlerProtocol | None = create_field(
        doc="""Optional decryption and/or signature check of the request_body."""
    )

    # could be generated from default impl
    deserialize: StepHandlerProtocol | None = create_field(
        doc="""Deserialize request body to the input_raw."""
    )
    # could be generated from default impl
    validate_input: StepHandlerProtocol | None = create_field(
        doc="""Validate input_raw and/or request body."""
    )

    check_access_post_read: StepHandlerProtocol | None = create_field(
        doc="""Check a requester has an access to that resource (body has been read)."""
    )

    # could be generated from default impl
    map_input: StepHandlerProtocol | None = create_field(
        doc="""Map input_raw to the internal representation to be processed."""
    )

    business: StepHandlerProtocol | None = create_field(
        doc="""Endpoint business part. Could be database handling and/or"""
        """sending another request somewhere else"""
    )
    # could be generated from default impl
    map_output: StepHandlerProtocol | None = create_field(
        doc="""Map output_business to the raw representation to be serialized."""
    )

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
    )

    serialize: StepHandlerProtocol | None = create_field(
        doc="""Serialize output_raw to be passed for transport layers."""
    )
    encrypt: StepHandlerProtocol | None = create_field(
        doc="""Optional encryption, signing, etc."""
    )

    response_headers: StepHandlerProtocol | None = create_field(
        doc="""Prepare additional response headers."""
    )

    # framework-specific
    create_response: StepHandlerProtocol | None = create_field(
        doc="""Create HTTP response to be returned."""
    )

    def response_order(self):
        """Intended response preparation order."""
        return (
            ("serialize", self.serialize),
            ("encrypt", self.encrypt),
            ("response_headers", self.response_headers),
            ("create_response", self.create_response),
        )


def defined_steps(
    steps: abc.Sequence[tuple[str, StepHandlerProtocol | None]]
) -> abc.Iterable[tuple[str, StepHandlerProtocol]]:
    return filter(lambda step: step[1] is not None, steps)


class UrlHandler:
    steps: UrlHandlerSteps
    error_status_to_http: abc.Mapping[int, int]

    def __init__(
        self, *, steps: UrlHandlerSteps, error_status_to_http: abc.Mapping[int, int]
    ):
        self.steps = steps
        self.error_status_to_http = error_status_to_http

    async def __call__(self, request, **url_params):
        steps = self.steps

        context: ctx.StepContext = ctx.StepContext(
            request_info=ctx.StepContextRequestInfo(request=request),
            custom_info=dict(url_params),
            error_status_to_http=self.error_status_to_http,
        )

        try:
            for current_step, step_handler in defined_steps(steps.process_order()):
                context.current_step = current_step
                await step_handler(context)
        except Exception as e:  # pylint: disable=W0718
            context.exception = e
            if steps.exception_handler is None:
                raise
            if not await steps.exception_handler(context):
                raise  # re-raise the exception if not handled

        for current_step, step_handler in defined_steps(steps.response_order()):
            context.current_step = current_step
            await step_handler(context)

        return context.response
