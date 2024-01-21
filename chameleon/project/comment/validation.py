from chameleon.step.validation import jsonschema

jsonschema.register_jsonschema_validation(
    type_id="comment",
    action_id="create",
    ref="schema_comment.yml#/$defs/ChameleonCommentCreate",
)

jsonschema.register_jsonschema_validation(
    type_id="comment",
    action_id="get",
    ref="schema_comment.yml#/$defs/ChameleonComment",
)

jsonschema.register_jsonschema_validation(
    type_id="comment",
    action_id="update",
    ref="schema_comment.yml#/$defs/ChameleonCommentUpdate",
)
