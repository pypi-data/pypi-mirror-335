from typing import Optional, TypedDict

HowToResolve = TypedDict("HowToResolve", {"ENGLISH": str, "SIMPLIFIED_CHINESE": str})


class KebleException(Exception):
    def __init__(
        self,
        *,
        # internal, server side
        alert_admin: bool = False,
        function_identifier: Optional[str] = None,
        admin_note: Optional[str] = None,
        # client side, for end user
        status_code: int = 400,
        how_to_resolve: Optional[HowToResolve] = None,
    ):
        self.status_code = status_code
        self.alert_admin = alert_admin
        self.how_to_resolve = how_to_resolve
        self.function_identifier = function_identifier
        self.admin_note = admin_note

    def __str__(self):
        return self.__class__.__name__
