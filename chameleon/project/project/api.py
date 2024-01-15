from collections import abc
import typing

from chameleon.common import transaction
from chameleon.project.project.models import ChameleonProject, ChameleonProjectHistory
from chameleon.step import core
from chameleon.step.mapping import datetime
from chameleon.history.utils import generate_history_objects


async def project_history(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    history = await ChameleonProjectHistory.query.by_object_id(
        object_id=project_id
    ).all()
    context.output_business = history


async def project_create_fun(context: core.StepContext):
    project = context.input_business
    now = datetime.utcnow()
    async with transaction.aatomic():
        await project.insert()

        source_object = project.to_dict()
        await create_history(
            source_object=None,
            target_object=source_object,
            action="CREATE",
            timestamp=now,
        )

    context.output_business = project


async def project_list_fun(context: core.StepContext):
    context.output_business = await ChameleonProject.query.all()


async def project_get_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    context.output_business = await ChameleonProject.query.by_id(project_id).first()


async def project_update_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    project_data = context.input_business
    now = datetime.utcnow()
    async with transaction.aatomic():
        project: ChameleonProject = await ChameleonProject.query.by_id(
            project_id
        ).first()
        source = project.to_dict()
        project.set_fields(**project_data)
        await project.update(keys=project_data.keys())
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
    await ChameleonProjectHistory.query.bulk_create(history_objects)
