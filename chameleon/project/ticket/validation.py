from chameleon.step.validation import jsonschema

jsonschema.register_jsonschema_validation(
    type_id="ticket",
    action_id="create",
    ref="schema_ticket.yml#/$defs/ChameleonTicketCreate",
)

jsonschema.register_jsonschema_validation(
    type_id="ticket",
    action_id="get",
    ref="schema_ticket.yml#/$defs/ChameleonTicket",
)

jsonschema.register_jsonschema_validation(
    type_id="ticket",
    action_id="update",
    ref="schema_ticket.yml#/$defs/ChameleonTicketUpdate",
)
