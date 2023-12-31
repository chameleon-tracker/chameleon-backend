import dataclasses
from collections import abc
from unittest import mock

import pytest

from chameleon.step.core import context as ctx
from chameleon.step.core import core
from chameleon.step.core import multi


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class StepParams:
    exists: bool = True
    return_value: bool = True
    awaited: bool = True
    step: str = "test"


step_not_exists = StepParams(exists=False)
step_not_awaited = StepParams(awaited=False)
step_return_false = StepParams(return_value=False)
step_default = StepParams()
step_test1 = StepParams(awaited=False, step="test1")
test_context = ctx.StepContext(
    current_step="test",
    request_info=ctx.StepContextRequestInfo(request=object()),
    error_status_to_http={},
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "default_params,step_params,expected_value",
    (
        (step_not_exists, step_default, True),
        (step_not_exists, step_return_false, False),
        (step_not_awaited, step_default, True),
        (step_default, step_return_false, True),
        (step_return_false, step_return_false, False),
        (step_default, step_test1, True),
        (step_return_false, step_test1, False),
        (step_not_exists, step_test1, False),
    ),
)
async def test_multi_dict_step(
    *,
    default_params: StepParams,
    step_params: StepParams,
    expected_value: bool,
):
    """Test default and dict with a single element.

    Args:
        default_params: Default step to use
        step_params: Primary step
        expected_value: which value expect at the end
    """
    default_handler = create_step(default_params)
    step_handler = create_step(step_params)

    step = multi.multi_dict_step(
        default_handler=default_handler, steps_by_name={step_params.step: step_handler}
    )

    assert step is not None
    assert step is not default_handler

    value = await step(test_context)
    assert value == expected_value  # Could be is as well

    assert_step_awaited(default_params, default_handler)
    assert_step_awaited(step_params, step_handler)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "default_params,steps_by_name",
    (
        (step_not_exists, {}),
        (step_not_exists, {"test": None}),
        (step_not_exists, {"test1": None}),
        (step_default, {}),
        (step_default, {"test": None}),
        (step_default, {"test1": None}),
    ),
)
async def test_multi_dict_step_default(
    *,
    default_params: StepParams,
    steps_by_name: abc.Mapping[str, core.StepHandlerProtocol | None],
):
    """Test default without custom steps defined.

    This is a special case of test_multi_dict_step,
        where step_by_name may not define any handler.
    """
    default_handler = create_step(default_params)

    step = multi.multi_dict_step(
        default_handler=default_handler, steps_by_name=steps_by_name
    )

    assert step is default_handler


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "step1_params,step2_params,expect_first,expect_second",
    (
        (step_not_exists, step_not_exists, True, True),
        (step_default, step_not_exists, True, False),
        (step_not_exists, step_default, False, True),
        (step_default, step_default, False, False),
    ),
)
async def test_list_step(
    step1_params: StepParams,
    step2_params: StepParams,
    expect_first: bool,
    expect_second: bool,
):
    """Test all combinations for list_step.

    Args:
        step1_params: params for first step
        step2_params: params for second step
        expect_first: if resulting step is exactly first one
        expect_second: if resulting step is exactly first one
    """
    step1 = create_step(step1_params)
    step2 = create_step(step2_params)

    step = multi.list_step([step1, step2])
    if expect_first:
        assert step is step1
    else:
        assert step is not step1

    if expect_second:
        assert step is step2
    else:
        assert step is not step2

    if step is None:
        return

    await step(test_context)

    assert_step_awaited(step1_params, step1)
    assert_step_awaited(step2_params, step2)


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class MultiStepParams:
    step1: StepParams = step_not_exists
    step2: StepParams = step_not_exists
    multi_type: str  # dict, list, or single


# To keep param definitions short, following abbreviations are used:
# ex means exists, default
# aw means "not awaited"
# no means not defined

# Single (direct handler) ---------------
multi_step_single_ex = MultiStepParams(step1=step_default, multi_type="single")
multi_step_single_aw = MultiStepParams(step1=step_not_awaited, multi_type="single")
multi_step_single_no = MultiStepParams(multi_type="single")
# List (list of handlers) -----------------
# form is [ step1 ]
# second step is not used as it basically adds nothing. See test_list_step for cases
multi_step_list_no = MultiStepParams(multi_type="list")
multi_step_list_ex = MultiStepParams(step1=step_default, multi_type="list")
multi_step_list_aw = MultiStepParams(step1=step_not_awaited, multi_type="list")

# Dict (map of handlers) -----------------
# {"test": step1, "test1": step2}
multi_step_dict_no_no = MultiStepParams(multi_type="dict")
multi_step_dict_ex_no = MultiStepParams(step1=step_default, multi_type="dict")
multi_step_dict_no_aw = MultiStepParams(step2=step_not_awaited, multi_type="dict")
multi_step_dict_ex_aw = MultiStepParams(
    step1=step_default, step2=step_not_awaited, multi_type="dict"
)
# Additional special forms for dict:
multi_step_dict_aw_no = MultiStepParams(step1=step_not_awaited, multi_type="dict")
multi_step_dict_aw_aw = MultiStepParams(
    step1=step_not_awaited, step2=step_not_awaited, multi_type="dict"
)

# pre- and post- steps for expected result True
pre_post_expect_result_True = (
    multi_step_single_no,
    multi_step_list_no,
    multi_step_dict_no_no,
    multi_step_dict_no_aw,
    multi_step_single_ex,
    multi_step_list_ex,
    multi_step_dict_ex_aw,
)

# pre- and post- steps for expected result False
pre_post_expect_result_False = (
    multi_step_single_no,
    multi_step_list_no,
    multi_step_dict_no_no,
    multi_step_dict_no_aw,
)

# pre- and post- steps for expected result None
pre_post_expect_result_None = (
    multi_step_single_no,
    multi_step_list_no,
    multi_step_dict_no_no,
    multi_step_single_aw,
    multi_step_list_aw,
    multi_step_dict_no_aw,
    multi_step_dict_aw_no,
    multi_step_dict_aw_aw,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("pre_params", pre_post_expect_result_True)
@pytest.mark.parametrize("post_params", pre_post_expect_result_True)
@pytest.mark.parametrize(
    "default_params, step_params, expect_result",
    (
        # Single step, Single default
        (multi_step_single_ex, multi_step_single_no, True),  # 2
        (multi_step_single_no, multi_step_single_ex, True),  # 3
        (multi_step_single_aw, multi_step_single_ex, True),  # 4
        # Single step, List default
        (multi_step_list_ex, multi_step_single_no, True),  # 6
        (multi_step_list_no, multi_step_single_ex, True),  # 7
        (multi_step_list_aw, multi_step_single_ex, True),  # 8
        # Single step, Dict default (called)
        (multi_step_dict_ex_no, multi_step_single_no, True),  # 9
        (multi_step_dict_ex_aw, multi_step_single_no, True),  # 10
        # Single step, Dict default (not called)
        (multi_step_dict_aw_no, multi_step_single_ex, True),  # 12
        (multi_step_dict_aw_aw, multi_step_single_ex, True),  # 13
        (multi_step_dict_no_aw, multi_step_single_ex, True),  # 14
    ),
)
async def test_ensure_single_step_single(
    *,
    default_params: MultiStepParams,
    step_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    """Test ensure_single_step in case of the single StepHandlerProtocol instance.

    Args:
        default_params: default step definition
        step_params: primary step definition
        pre_params: pre-step definition
        post_params: post-step definition
        expect_result: expected result
    """
    await ensure_single_step_test_impl(
        step_params=step_params,
        default_params=default_params,
        pre_params=pre_params,
        post_params=post_params,
        expect_result=expect_result,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("pre_params", pre_post_expect_result_True)
@pytest.mark.parametrize("post_params", pre_post_expect_result_True)
@pytest.mark.parametrize(
    "default_params, step_params, expect_result",
    (
        # List - no default
        (multi_step_single_no, multi_step_list_ex, True),  # 1
        # List - single default
        (multi_step_single_ex, multi_step_list_no, True),  # 3
        (multi_step_single_aw, multi_step_list_ex, True),  # 4
        # List - single list default
        (multi_step_list_ex, multi_step_list_no, True),  # 6
        (multi_step_list_aw, multi_step_list_ex, True),  # 7
        # List - no step, dict default (called)
        (multi_step_dict_ex_no, multi_step_list_no, True),  # 8
        (multi_step_dict_ex_aw, multi_step_list_no, True),  # 9
        # List - step, dict default (not called)
        (multi_step_dict_aw_no, multi_step_list_ex, True),  # 8
        (multi_step_dict_aw_aw, multi_step_list_ex, True),  # 9
        (multi_step_dict_no_aw, multi_step_list_ex, True),  # 10
    ),
)
async def test_ensure_single_step_list(
    *,
    default_params: MultiStepParams,
    step_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    """Test ensure_single_step in case of the list StepHandlerProtocol instance.

    Args:
        default_params: default step definition
        step_params: primary step definition
        pre_params: pre-step definition
        post_params: post-step definition
        expect_result: expected result
    """
    await ensure_single_step_test_impl(
        step_params=step_params,
        default_params=default_params,
        pre_params=pre_params,
        post_params=post_params,
        expect_result=expect_result,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("pre_params", pre_post_expect_result_True)
@pytest.mark.parametrize("post_params", pre_post_expect_result_True)
@pytest.mark.parametrize(
    "default_params, step_params, expect_result",
    (
        # Dict - no default
        (multi_step_single_no, multi_step_dict_ex_no, True),  # 1
        (multi_step_single_no, multi_step_dict_ex_aw, True),  # 3
        # Dict - single default
        (multi_step_single_ex, multi_step_dict_no_no, True),  # 4
        (multi_step_single_aw, multi_step_dict_ex_no, True),  # 5
        (multi_step_single_ex, multi_step_dict_no_aw, True),  # 6
        (multi_step_single_aw, multi_step_dict_ex_aw, True),  # 7
        # Dict - list default
        (multi_step_list_aw, multi_step_dict_ex_no, True),  # 9
        (multi_step_list_ex, multi_step_dict_no_aw, True),  # 10
        (multi_step_list_aw, multi_step_dict_ex_aw, True),  # 11
        # Dict - no step,, dict default
        (multi_step_dict_ex_no, multi_step_dict_no_no, True),  # 13
        (multi_step_dict_ex_aw, multi_step_dict_no_no, True),  # 15
        # Dict - ex step, dict default
        (multi_step_dict_no_no, multi_step_dict_ex_no, True),  # 12
        (multi_step_dict_aw_no, multi_step_dict_ex_no, True),  # 13
        (multi_step_dict_no_aw, multi_step_dict_ex_no, True),  # 14
        (multi_step_dict_no_no, multi_step_dict_ex_aw, True),  # 15
        (multi_step_dict_aw_no, multi_step_dict_ex_aw, True),  # 16
        (multi_step_dict_no_aw, multi_step_dict_ex_aw, True),  # 17
        # Dict - aw step, dict default
        (multi_step_dict_ex_no, multi_step_dict_no_aw, True),  # 19
    ),
)
async def test_ensure_single_step_dict(
    *,
    default_params: MultiStepParams,
    step_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    """Test ensure_single_step in case of the dict StepHandlerProtocol instance.

    Args:
        default_params: default step definition
        step_params: primary step definition
        pre_params: pre-step definition
        post_params: post-step definition
        expect_result: expected result
    """
    await ensure_single_step_test_impl(
        step_params=step_params,
        default_params=default_params,
        pre_params=pre_params,
        post_params=post_params,
        expect_result=expect_result,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("pre_params", pre_post_expect_result_False)
@pytest.mark.parametrize("post_params", pre_post_expect_result_False)
@pytest.mark.parametrize(
    "default_params, step_params, expect_result",
    (
        (multi_step_dict_no_aw, multi_step_single_no, False),  # 11
        (multi_step_dict_no_aw, multi_step_list_no, False),  # 10
        (multi_step_single_no, multi_step_dict_no_aw, False),  # 2
        (multi_step_dict_no_aw, multi_step_dict_no_no, False),  # 14
        (multi_step_dict_no_no, multi_step_dict_no_aw, False),  # 18
        (multi_step_dict_no_aw, multi_step_dict_no_aw, False),  # 20
    ),
)
async def test_ensure_single_step_false(
    *,
    default_params: MultiStepParams,
    step_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    """Test ensure_single_step in case of the expected result False.

    Args:
        default_params: default step definition
        step_params: primary step definition
        pre_params: pre-step definition
        post_params: post-step definition
        expect_result: expected result
    """
    await ensure_single_step_test_impl(
        step_params=step_params,
        default_params=default_params,
        pre_params=pre_params,
        post_params=post_params,
        expect_result=expect_result,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("pre_params", pre_post_expect_result_None)
@pytest.mark.parametrize("post_params", pre_post_expect_result_None)
@pytest.mark.parametrize(
    "default_params, step_params, expect_result",
    (
        (multi_step_single_no, multi_step_single_no, None),
        (multi_step_list_no, multi_step_single_no, None),
        (multi_step_dict_no_no, multi_step_single_no, None),
        (multi_step_single_no, multi_step_list_no, None),
        (multi_step_single_no, multi_step_list_no, None),
        (multi_step_list_no, multi_step_list_no, None),
        (multi_step_dict_no_no, multi_step_list_no, None),
        (multi_step_single_no, multi_step_dict_no_no, None),
        (multi_step_list_no, multi_step_dict_no_no, None),
        (multi_step_dict_no_no, multi_step_dict_no_no, None),
    ),
)
async def test_ensure_single_step_none(
    *,
    default_params: MultiStepParams,
    step_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    """Test ensure_single_step in case of the expected result None.

    Args:
        default_params: default step definition
        step_params: primary step definition
        pre_params: pre-step definition
        post_params: post-step definition
        expect_result: expected result
    """
    await ensure_single_step_test_impl(
        step_params=step_params,
        default_params=default_params,
        pre_params=pre_params,
        post_params=post_params,
        expect_result=expect_result,
    )


async def ensure_single_step_test_impl(
    *,
    step_params: MultiStepParams,
    default_params: MultiStepParams,
    pre_params: MultiStepParams,
    post_params: MultiStepParams,
    expect_result: bool | None,
):
    step1, step2, step_multi = create_multi_step(step_params)
    default1, default2, default_multi = create_multi_step(default_params)
    pre1, pre2, pre_multi = create_multi_step(pre_params)
    post1, post2, post_multi = create_multi_step(post_params)

    step = multi.ensure_single_step(
        step_base=step_multi,
        step_default=default_multi,
        step_post=pre_multi,
        step_pre=post_multi,
    )

    if expect_result is None:
        assert step is None
    else:
        assert step is not None

        value = await step(test_context)
        assert value is expect_result

    assert_multi_step_awaited(step_params, step1, step2)
    assert_multi_step_awaited(default_params, default1, default2)
    assert_multi_step_awaited(post_params, post1, post2)
    assert_multi_step_awaited(pre_params, pre1, pre2)


def create_multi_step(
    step_params: MultiStepParams,
) -> tuple[mock.AsyncMock | None, mock.AsyncMock | None, multi.StepHandlerMulti | None]:
    step1 = create_step(step_params.step1)
    step2 = create_step(step_params.step2)

    match step_params.multi_type:
        case "dict":
            return step1, step2, {"test": step1, "test1": step2}
        case "list":
            return step1, step2, [step1]
        case "single":
            return step1, step2, step1
        case _:
            raise ValueError("Invalid step type")


def assert_multi_step_awaited(
    step_params: MultiStepParams,
    step1: mock.AsyncMock | None,
    step2: mock.AsyncMock | None,
):
    assert_step_awaited(step_params.step1, step1)
    assert_step_awaited(step_params.step2, step2)


def assert_step_awaited(params: StepParams, handler: mock.AsyncMock | None):
    if not params.exists:
        assert handler is None
        return

    assert handler is not None
    if params.awaited:
        handler.assert_awaited_once()
    else:
        handler.assert_not_awaited()


def create_step(params: StepParams) -> mock.AsyncMock | None:
    if not params.exists:
        return None

    return mock.AsyncMock(
        spec=core.StepHandlerProtocol, return_value=params.return_value
    )
