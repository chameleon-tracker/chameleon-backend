import logging
import typing
from collections import abc

from django import http

from chameleon.step import core
from chameleon.step.steps import steps_default as default
from chameleon.step.steps import steps_json as json

logger = logging.getLogger(__name__)

__all__ = ("method_dispatcher", "django_json_steps")


def method_dispatcher(
    *,
    error_status_to_http: abc.Mapping[int, int] | None = None,
    **kwargs: core.StepsDefinitionDict,
):
    async def invalid_method(*_args, **_kwargs):
        return http.HttpResponseNotAllowed(kwargs.keys())

    return core.method_dispatcher(
        invalid_method=invalid_method,
        error_status_to_http=error_status_to_http,
        **kwargs,
    )


async def django_fill_request_info(context: core.StepContext):
    request: http.HttpRequest = context.request_info.request
    if request.method is None:
        raise ValueError("Invalid request method.")
    context.request_info.method = request.method
    context.request_info.content_type = request.content_type
    context.request_info.content_encoding = request.encoding


HTTP_METHODS_WITH_INPUT = {"POST", "PUT"}


async def extract_body(context: core.StepContext):
    request_method = context.request_info.method

    if request_method in HTTP_METHODS_WITH_INPUT:
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
    **kwargs: typing.Unpack[DjangoParams],
) -> core.StepsDefinitionDict:
    default_json_kwargs = default.default_json_steps(**kwargs)

    default_json_kwargs.update(
        {
            "fill_request_info_default": django_fill_request_info,
            "check_headers_default": [
                django_check_accepts_json,
                json.check_content_type_json,
            ],
            "extract_body_default": extract_body,
            "create_response_default": create_response_json,
        }
    )

    return default_json_kwargs
