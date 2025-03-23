from klu.common.errors import BaseKluError


class EvalNotFoundError(BaseKluError):
    datum_id: int

    def __init__(self, guid):
        self.guid = guid
        self.message = f"Eval with GUID {guid} was not found."
        super().__init__(self.message)
