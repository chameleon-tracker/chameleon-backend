import logging
import typing

logger = logging.getLogger(__name__)

__all__ = ("ProcessorRegistry", "ProcessorProtocol")


@typing.runtime_checkable
class ProcessorProtocol(typing.Protocol):
    def __call__(self, value: typing.Any) -> typing.Any:
        ...


class ProcessorRegistry:
    _registry: typing.MutableMapping[str, ProcessorProtocol]
    name: str

    def __init__(self, name: str):
        self._registry = {}
        self.name = name

    def register(
        self,
        *,
        type_id: str,
        action_id: str | None = None,
        processor: ProcessorProtocol,
    ):
        """Register a validator.

        type_id - type id
        action_id - action made on this type
        processor - actual processor for this type_id and action_id

        """
        if processor is None:
            raise ValueError("Processor can't be None")

        processor_id = _processor_id(type_id, action_id)

        if processor_id in self._registry:
            raise ValueError(
                f"{self.name.capitalize()} registry already contains {processor_id!r}"
            )

        self._registry[processor_id] = processor

    def __getitem__(self, item):
        return self._registry[item]

    def get(
        self,
        type_id: str,
        action_id: str | None = None,
        default: ProcessorProtocol = None,
    ):
        processor_id = _processor_id(type_id, action_id)
        return self._registry.get(processor_id, default)


def _processor_id(type_id: str, action_id: str | None = None):
    if not isinstance(type_id, str) or not type_id:
        raise TypeError(f"type_id must be non-empty str, got {type_id!r}")
    if action_id and not isinstance(action_id, str):
        raise TypeError(f"action_id must be non-empty str, got {action_id!r}")

    if action_id:
        processor_id = f"{type_id}:{action_id}"
    else:
        processor_id = type_id

    return processor_id
