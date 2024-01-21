from chameleon.common.django import transaction
from chameleon.project.comment.models import ChameleonComment
from chameleon.project.comment.models import ChameleonCommentHistory
from chameleon.step import core


async def comment_history(context: core.StepContext):
    comment_id = context.custom_info["comment_id"]
    history = await ChameleonCommentHistory.query.by_object_id(
        object_id=comment_id
    ).all()
    context.output_business = history


async def comment_create_fun(context: core.StepContext):
    comment: ChameleonComment = context.input_business
    ticket_id = context.custom_info["ticket_id"]
    comment.ticket_id = ticket_id

    async with transaction.aatomic():
        await comment.insert_with_history()

    context.output_business = comment


async def comment_list_fun(context: core.StepContext):
    ticket_id = context.custom_info["ticket_id"]
    context.output_business = await ChameleonComment.query.by_ticket_id(ticket_id).all()


async def comment_get_fun(context: core.StepContext):
    comment_id = context.custom_info["comment_id"]
    context.output_business = await ChameleonComment.query.by_id(comment_id).first()


async def comment_update_fun(context: core.StepContext):
    comment_id = context.custom_info["comment_id"]
    comment_data = context.input_business
    async with transaction.aatomic():
        comment: ChameleonComment = await ChameleonComment.query.by_id(
            comment_id
        ).first()
        await comment.update_with_history(**comment_data)

    context.output_business = comment
