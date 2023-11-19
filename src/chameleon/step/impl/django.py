import logging
import typing

from django import http
from django.core.exceptions import ObjectDoesNotExist

from chameleon.step import core
from chameleon.step import impl as default


logger = logging.getLogger(__name__)

__all__ = ("method_dispatcher", "django_json_steps")


def method_dispatcher(
    *,
    error_status_to_http: typing.Mapping[int, int] | None = None,
    **kwargs: core.StepsDefinitionDict
):
    async def invalid_method(*_args, **_kwargs):
        return http.HttpResponseNotAllowed(kwargs.keys())

    return core.method_dispatcher(
        invalid_method=invalid_method,
        error_status_to_http=error_status_to_http,
        **kwargs
    )


async def django_fill_request_info(context: core.StepContext):
    request: http.HttpRequest = context.request_info.request
    if request.method is None:
        raise ValueError("Invalid request method.")
    context.request_info.method = request.method
    context.request_info.content_type = request.content_type
    context.request_info.content_encoding = request.encoding


async def extract_body(context: core.StepContext):
    request_method = context.request_info.method

    if request_method in ("POST", "PUT"):
        context.request_body = context.request_info.request.body


async def django_check_accepts_json(context: core.StepContext):
    request: http.HttpRequest = context.request_info.request
    if not request.accepts("application/json"):
        raise ValueError("Requester doesn't accept json")


async def create_response_json(context: core.StepContext):
    content = context.response_body

    error_status = context.error_status
    method = context.request_info.method

    if error_status:
        http_status = context.error_status_to_http.get(error_status, 500)

    elif not content or method.lower() == "delete":
        http_status = 204
    else:
        http_status = 200

    if http_status == 204:
        response = http.HttpResponse(
            status=http_status,
            headers=context.response_headers,
            content_type="application/json",
        )
    else:
        response = http.HttpResponse(
            status=http_status,
            content=content,
            headers=context.response_headers,
            content_type="application/json",
        )

    context.response = response


class DjangoParams(core.StepsDefinitionDict, default.DefaultJsonSteps):
    pass


def django_json_steps(
    exception_handler_map: typing.Mapping[str, core.StepHandlerProtocol] | None = None,
    **kwargs: typing.Unpack[DjangoParams]
) -> core.StepsDefinitionDict:
    exception_handler = kwargs.get("exception_handler_default")

    if exception_handler is not None and exception_handler_map is not None:
        raise ValueError(
            'Set both "exception_handler_default" and'
            ' "exception_handler_map" is not allowed'
        )

    if exception_handler is None:
        exception_handler = exception_handler_map
        if exception_handler is None:
            exception_handler = {}

        if (
            isinstance(exception_handler, typing.MutableMapping)
            and "business" not in exception_handler
        ):
            exception_handler["business"] = generic_business_error_handler
        kwargs["exception_handler_default"] = exception_handler

    default_json_kwargs = default.default_json_steps(**kwargs)

    default_json_kwargs.update(
        {
            "fill_request_info_default": django_fill_request_info,
            "check_headers_default": [
                django_check_accepts_json,
                default.check_content_type_json,
            ],
            "extract_body_default": extract_body,
            "create_response_default": create_response_json,
        }
    )

    return default_json_kwargs


async def generic_business_error_handler(context: core.StepContext) -> bool:
    if isinstance(context.exception, ObjectDoesNotExist):
        context.error_status = 404

        if context.output_raw is None:
            context.output_raw = {"error": 404, "reason": "object doesn't exist"}

            return True

    return False
