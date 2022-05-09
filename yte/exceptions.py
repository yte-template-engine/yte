class YteError(Exception):
    def __init__(self, msg, context):
        section = (
            "in section /" + "/".join(context.template) if context else "at top level"
        )
        super().__init__(f"Error processing template {section}: {msg}")
