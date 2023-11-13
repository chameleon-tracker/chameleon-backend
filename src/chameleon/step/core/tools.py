import typing

from chameleon.step import core

__all__ = ("noop_step", "method_dispatcher")

from chameleon.step.core.multi import multi_processor_steps


async def noop_step(_context: core.StepContext):
    ...


def ensure_steps_object(
    value: core.ProcessorSteps | typing.Mapping[str, core.StepHandlerProtocol]
):
    if isinstance(value, core.ProcessorSteps):
        return value
    elif isinstance(value, typing.Mapping):
        return core.ProcessorSteps(**value)
    else:
        raise TypeError("Value must be ProcessorHooks or a mapping")


def method_dispatcher(
    *,
    invalid_method,
    **kwargs: core.ProcessorSteps | typing.Mapping[str, core.StepHandlerProtocol],
):
    table = {
        key.lower(): core.UrlHandler(steps=multi_processor_steps(**value))
        for key, value in kwargs.items()
    }

    async def process(request, *url_args, **url_kwargs):
        handler = table.get(request.method.lower())

        if handler is None:
            await invalid_method(request, *url_args, **url_kwargs)

        return await handler.process(request, *url_args, **url_kwargs)

    return process
