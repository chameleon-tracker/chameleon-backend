import itertools
import secrets
import typing
import uuid

import pytest
from chameleon.step import core


class TestException(Exception):
    __test__ = False


processing_step_order = (
    "fill_request_info",
    "check_authenticated",
    "check_headers",
    "check_access_pre_read",
    "extract_body",
    "decrypt",
    "deserialize",
    "validate_input",
    "check_access_post_read",
    "map_input",
    "business",
    "map_output",
)
response_step_order = (
    "serialize",
    "encrypt",
    "response_headers",
    "create_response",
)


@pytest.mark.asyncio
async def test_processing_order():
    step_order: list[str] = []
    await generate_and_run_steps(step_order_collect=step_order)
    assert tuple(step_order) == processing_step_order + response_step_order


@pytest.mark.asyncio
@pytest.mark.parametrize("faulty_step", processing_step_order)
async def test_faulty_processing_step(faulty_step: str):
    step_order: list[str] = []
    expected_steps = (
        tuple(itertools.takewhile(lambda x: x != faulty_step, processing_step_order))
        + (faulty_step, f"exception: {faulty_step}")
        + response_step_order
    )
    await generate_and_run_steps(step_order_collect=step_order, faulty_step=faulty_step)
    assert tuple(step_order) == expected_steps


@pytest.mark.asyncio
@pytest.mark.parametrize("faulty_step", response_step_order)
async def test_faulty_response_step(faulty_step: str):
    step_order: list[str] = []
    expected_steps = (
        processing_step_order
        + tuple(itertools.takewhile(lambda x: x != faulty_step, response_step_order))
        + (faulty_step,)
    )
    with pytest.raises(TestException) as exc_info:
        await generate_and_run_steps(
            step_order_collect=step_order,
            faulty_step=faulty_step,
        )
    assert exc_info is not None
    assert str(exc_info.value) == faulty_step
    assert tuple(step_order) == expected_steps


@pytest.mark.asyncio
@pytest.mark.parametrize("faulty_step", processing_step_order)
async def test_faulty_processing_step_unhandled(faulty_step: str):
    await faulty_step_handler_unhandled(faulty_step, True)


@pytest.mark.asyncio
@pytest.mark.parametrize("faulty_step", response_step_order)
async def test_faulty_response_step_unhandled(faulty_step: str):
    await faulty_step_handler_unhandled(faulty_step, False)


async def faulty_step_handler_unhandled(faulty_step: str, expect_exception: bool):
    step_order: list[str] = []

    total_step_order = processing_step_order + response_step_order
    exception_step: tuple[str]

    if expect_exception:
        exception_step = (f"exception: {faulty_step}",)
    else:
        exception_step = ()  # type: typing.IO[str]

    expected_steps = (
        tuple(itertools.takewhile(lambda x: x != faulty_step, total_step_order))
        + (faulty_step,)
        + exception_step
    )
    with pytest.raises(TestException) as exc_info:
        await generate_and_run_steps(
            step_order_collect=step_order,
            faulty_step=faulty_step,
            exception_handled=False,
        )
    assert exc_info is not None
    assert str(exc_info.value) == faulty_step
    assert tuple(step_order) == expected_steps


def step_handler_generator(
    *,
    expected_step: str,
    step_order_collect: list[str],
    request_obj: typing.Any,
    error_code_mapping: typing.Mapping[int, int],
    expected_custom_info: typing.Mapping[str, typing.Any],
    faulty: bool,
    exception: bool,
    exception_handled: bool = True,
):
    assert expected_step is not None

    async def step_handler(context: core.StepContext):
        assert context is not None
        assert context.current_step == expected_step
        assert context.custom_info == expected_custom_info
        assert context.request_info.request is request_obj
        assert context.error_status_to_http == error_code_mapping

        if exception:
            assert context.exception is not None
            assert isinstance(context.exception, TestException)
            assert context.exception.args == (expected_step,)

            step_order_collect.append(f"exception: {context.current_step}")

            return exception_handled

        # Append for further order check
        step_order_collect.append(context.current_step)

        if faulty:
            raise TestException(expected_step)

    return step_handler


async def generate_and_run_steps(
    *,
    faulty_step: str = "__unknown__",
    step_order_collect: list[str],
    exception_handled: bool = True,
):
    steps = {}
    request = object()
    custom_info_key = "s" + str(uuid.uuid4()).replace("-", "_")
    custom_info = {custom_info_key: uuid.uuid4()}
    error_code_mapping = {random_int(): random_int()}

    total_step_order = (
        processing_step_order + ("exception_handler",) + response_step_order
    )

    for step_name in total_step_order:
        if step_name == "exception_handler":
            exception = True
            expected_step = faulty_step
            faulty = False
        else:
            faulty = faulty_step == step_name
            exception = False
            expected_step = step_name

        steps[step_name] = step_handler_generator(
            expected_step=expected_step,
            step_order_collect=step_order_collect,
            request_obj=request,
            expected_custom_info=custom_info,
            error_code_mapping=error_code_mapping,
            faulty=faulty,
            exception=exception,
            exception_handled=exception_handled,
        )

    handler_steps = core.UrlHandlerSteps(**steps)
    url_handler = core.UrlHandler(
        steps=handler_steps, error_status_to_http=error_code_mapping
    )

    await url_handler(request=request, **custom_info)


def random_int():
    return int.from_bytes(secrets.token_bytes(4))
