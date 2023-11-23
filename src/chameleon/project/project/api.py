from chameleon.step import core
from chameleon.project.project.models import ChameleonProject


async def project_create_fun(context: core.StepContext):
    project = context.input_business
    print(f"{project=!r}")
    await project.asave(force_insert=True)
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
    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    project = await ChameleonProject.objects.aget(pk=project_id)
    print(f"==>> {project=!r}")
    await project.update(commit=True, **project_data)
    context.output_business = project
