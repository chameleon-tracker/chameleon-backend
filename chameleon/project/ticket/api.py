import typing
from collections import abc

from chameleon.common.django import transaction
from chameleon.history.utils import generate_history_objects
from chameleon.project.ticket.models import ChameleonTicket
from chameleon.project.ticket.models import ChameleonTicketHistory
from chameleon.step import core
from chameleon.step.mapping import datetime


async def ticket_history(context: core.StepContext):
    ticket_id = context.custom_info["ticket_id"]
    history = await ChameleonTicketHistory.query.by_object_id(object_id=ticket_id).all()
    context.output_business = history


async def ticket_create_fun(context: core.StepContext):
    ticket: ChameleonTicket = context.input_business
    project_id = context.custom_info["project_id"]
    ticket.project_id = project_id

    now = datetime.utcnow()

    ticket.creation_time = now
    async with transaction.aatomic():
        await ticket.insert()

        source_object = ticket.to_dict()
        await create_history(
            source_object=None,
            target_object=source_object,
            action="CREATE",
            timestamp=now,
        )

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
    now = datetime.utcnow()
    async with transaction.aatomic():
        ticket: ChameleonTicket = await ChameleonTicket.query.by_id(ticket_id).first()
        source = ticket.to_dict()
        ticket.set_fields(**ticket_data)
        await ticket.update(keys=ticket_data.keys())
        target = ticket.to_dict()
        await create_history(
            source_object=source, target_object=target, action="UPDATE", timestamp=now
        )
    context.output_business = ticket


async def create_history(
    *,
    source_object: abc.Mapping[str, typing.Any] | ChameleonTicket | None,
    target_object: abc.Mapping[str, typing.Any] | ChameleonTicket | None,
    action: str,
    timestamp: datetime.datetime,
):
    history_objects = generate_history_objects(
        source_object=source_object,
        target_object=target_object,
        history_model=ChameleonTicketHistory,
        action=action,
        timestamp=timestamp,
    )
    await ChameleonTicketHistory.query.bulk_create(history_objects)
