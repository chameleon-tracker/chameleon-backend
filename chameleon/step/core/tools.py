import typing
from collections import abc

from chameleon.step.core import core
from chameleon.step.core import multi

__all__ = ("method_dispatcher",)


class InvalidHandlerProtocol(typing.Protocol):
    async def __call__(self, *args, **kwargs): ...


def method_dispatcher(
    *,
    invalid_method: InvalidHandlerProtocol,
    error_status_to_http: abc.Mapping[int, int] | None = None,
    **kwargs: multi.StepsDefinitionDict,
):
    error_status_to_http = error_status_to_http or {}
    table = {
        key.lower(): core.UrlHandler(
            steps=multi.multi_processor_steps(**value),
            error_status_to_http=error_status_to_http,
        )
        for key, value in kwargs.items()
    }

    async def process(request, *url_args, **url_kwargs):
        handler = table.get(request.method.lower(), invalid_method)
        return await handler(request, *url_args, **url_kwargs)

    return process
