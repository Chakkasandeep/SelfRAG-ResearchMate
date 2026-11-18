from .rails import check_input as rails_check_input


class GuardrailBlocked(Exception):
    def __init__(self, stage: str, reason: str):
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


async def check_input(text: str, stage: str):
    return await rails_check_input(text, stage)
