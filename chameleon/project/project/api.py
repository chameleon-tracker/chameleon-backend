from chameleon.common.django import transaction
from chameleon.project.project.models import ChameleonProject
from chameleon.project.project.models import ChameleonProjectHistory
from chameleon.step import core


async def project_history(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    history = await ChameleonProjectHistory.query.by_object_id(
        object_id=project_id
    ).all()
    context.output_business = history


async def project_create_fun(context: core.StepContext):
    project: ChameleonProject = context.input_business

    async with transaction.aatomic():
        await project.insert_with_history()

    context.output_business = project


async def project_list_fun(context: core.StepContext):
    context.output_business = await ChameleonProject.query.all()


async def project_get_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    context.output_business = await ChameleonProject.query.by_id(project_id).first()


async def project_update_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    project_data = context.input_business

    async with transaction.aatomic():
        project: ChameleonProject = await ChameleonProject.query.by_id(
            project_id
        ).first()
        await project.update_with_history(**project_data)

    context.output_business = project
