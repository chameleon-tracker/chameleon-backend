from collections import abc
import typing

from chameleon.common import transaction
from chameleon.project.project.models import ChameleonProject, ChameleonProjectHistory
from chameleon.step import core
from chameleon.step.mapping import datetime
from chameleon.history.utils import generate_history_objects


async def project_history(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    filtered = ChameleonProjectHistory.objects.filter(object_id=project_id)
    history = [value async for value in filtered]
    context.output_business = history


async def project_create_fun(context: core.StepContext):
    project = context.input_business
    now = datetime.utcnow()
    async with transaction.aatomic():
        await project.asave(force_insert=True)

        source_object = project.to_dict()
        await create_history(
            source_object=None,
            target_object=source_object,
            action="CREATE",
            timestamp=now,
        )

    context.output_business = project


async def project_list_fun(context: core.StepContext):
    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    context.output_business = [
        project async for project in ChameleonProject.objects.all()
    ]


async def project_get_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    context.output_business = await ChameleonProject.objects.aget(pk=project_id)


async def project_update_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    project_data = context.input_business
    now = datetime.utcnow()
    async with transaction.aatomic():
        # noinspection PyUnresolvedReferences
        # pylint: disable=E1101
        project: ChameleonProject = await ChameleonProject.objects.aget(pk=project_id)
        source = project.to_dict()
        await project.update(commit=True, **project_data)
        target = project.to_dict()
        await create_history(
            source_object=source, target_object=target, action="UPDATE", timestamp=now
        )
    context.output_business = project


async def create_history(
    *,
    source_object: abc.Mapping[str, typing.Any] | ChameleonProject | None,
    target_object: abc.Mapping[str, typing.Any] | ChameleonProject | None,
    action: str,
    timestamp: datetime.datetime,
):
    history_objects = generate_history_objects(
        source_object=source_object,
        target_object=target_object,
        history_model=ChameleonProjectHistory,
        action=action,
        timestamp=timestamp,
    )
    await ChameleonProjectHistory.objects.abulk_create(history_objects)
