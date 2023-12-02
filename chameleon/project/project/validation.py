from chameleon.step.validation import jsonschema

jsonschema.register_jsonschema_validation(
    type_id="project",
    action_id="create",
    ref="schema_project.yml#/$defs/ChameleonProjectCreate",
)

jsonschema.register_jsonschema_validation(
    type_id="project",
    action_id="get",
    ref="schema_project.yml#/$defs/ChameleonProject",
)

jsonschema.register_jsonschema_validation(
    type_id="project",
    action_id="update",
    ref="schema_project.yml#/$defs/ChameleonProjectUpdate",
)
