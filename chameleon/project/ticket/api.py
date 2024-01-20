from chameleon.common.django import transaction
from chameleon.project.ticket.models import ChameleonTicket
from chameleon.project.ticket.models import ChameleonTicketHistory
from chameleon.step import core


async def ticket_history(context: core.StepContext):
    ticket_id = context.custom_info["ticket_id"]
    history = await ChameleonTicketHistory.query.by_object_id(object_id=ticket_id).all()
    context.output_business = history


async def ticket_create_fun(context: core.StepContext):
    ticket: ChameleonTicket = context.input_business
    project_id = context.custom_info["project_id"]
    ticket.project_id = project_id

    async with transaction.aatomic():
        await ticket.insert_with_history()

    context.output_business = ticket


async def ticket_list_fun(context: core.StepContext):
    project_id = context.custom_info["project_id"]
    context.output_business = await ChameleonTicket.query.by_project_id(
        project_id
    ).all()


async def ticket_get_fun(context: core.StepContext):
    ticket_id = context.custom_info["ticket_id"]
    context.output_business = await ChameleonTicket.query.by_id(ticket_id).first()


async def ticket_update_fun(context: core.StepContext):
    ticket_id = context.custom_info["ticket_id"]
    ticket_data = context.input_business
    async with transaction.aatomic():
        ticket: ChameleonTicket = await ChameleonTicket.query.by_id(ticket_id).first()
        await ticket.update_with_history(**ticket_data)

    context.output_business = ticket
