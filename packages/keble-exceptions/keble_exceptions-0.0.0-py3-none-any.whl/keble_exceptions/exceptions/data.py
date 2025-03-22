from .base import KebleException


class ServerSideMissingParams(KebleException):
    def __init__(self, *, missing_params: str, alert_admin: bool):
        super(ServerSideMissingParams, self).__init__(
            how_to_resolve={
                "ENGLISH": f"Missing <{missing_params}>. This may cause by the programmer rather than you (the end user). You may need to wait for devs to resolve this problem.",
                "SIMPLIFIED_CHINESE": f"缺少了数据 <{missing_params}>。这很大概率是程序员导致的错误，并非你（终端用户）。你有可能需要等程序员下个版本更新迭代才能解决这个问题。",
            },
            alert_admin=alert_admin,
        )


class ClientSideMissingParams(KebleException):
    def __init__(self, *, missing_params: str, alert_admin: bool):
        super(ClientSideMissingParams, self).__init__(
            how_to_resolve={
                "ENGLISH": f"Missing <{missing_params}>. This may cause by the the client side or user(the end user). You may need to recheck your form, or you may need to wait for devs to resolve this problem.",
                "SIMPLIFIED_CHINESE": f"缺少了数据 <{missing_params}>。这很大概率是客户端，或者是你的表格填写的有问题。你可以先尝试检查表格是否有填写错误的信息。如果没有，那么很有可能你需要等程序员更新版本后才能解决这个问题了。",
            },
            alert_admin=alert_admin,
        )


class ServerSideInvalidParams(KebleException):
    def __init__(
        self, *, invalid_params: str, expected: str, but_got: str, alert_admin: bool
    ):
        super(ServerSideInvalidParams, self).__init__(
            how_to_resolve={
                "ENGLISH": f"Invalid value in <{invalid_params}>. Expected {expected}, but got {but_got}. This issue is likely caused by the programmer rather than you (the end user). You may need to wait for the developers to resolve this problem.",
                "SIMPLIFIED_CHINESE": f"<{invalid_params}> 的值无效。本应 {expected}，但却 {but_got}。这很大概率是程序员导致的错误，并非你（终端用户）。你可能需要等程序员修复这个问题。",
            },
            alert_admin=alert_admin,
        )


class ClientSideInvalidParams(KebleException):
    def __init__(
        self, *, invalid_params: str, expected: str, but_got: str, alert_admin: bool
    ):
        super(ClientSideInvalidParams, self).__init__(
            how_to_resolve={
                "ENGLISH": f"Invalid value in <{invalid_params}>. Expected {expected}, but got {but_got}. This issue is likely caused by incorrect input from the client side or the user (you). Please double-check your form or input before submitting again.",
                "SIMPLIFIED_CHINESE": f"<{invalid_params}> 的值无效。本应 {expected}，但却 {but_got}。这很大概率是客户端或你的输入问题。请检查你的表单或输入数据后再提交。",
            },
            alert_admin=alert_admin,  # Since it's a client-side issue, no need to alert the admin
        )


class UnhandledScenarioOrCase(KebleException):
    def __init__(self, *, unhandled_case: str, alert_admin: bool):
        super(UnhandledScenarioOrCase, self).__init__(
            how_to_resolve={
                "ENGLISH": f"{unhandled_case} is/are unsupported in current version of codebase. However, this could happen in future update.",
                "SIMPLIFIED_CHINESE": f"目前系统还不能处理：{unhandled_case}。目前要等开发更新迭代之后在后续考虑支持。",
            },
            alert_admin=alert_admin,  # Since it's a client-side issue, no need to alert the admin
        )
