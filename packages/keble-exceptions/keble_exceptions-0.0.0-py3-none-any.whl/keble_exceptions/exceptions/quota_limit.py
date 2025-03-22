from .base import KebleException


class EmailSendingLimitReached(KebleException):
    def __init__(self, *, wait_minutes: str, alert_admin: bool):
        super(EmailSendingLimitReached, self).__init__(
            how_to_resolve={
                "ENGLISH": f"You have reached the sending limit, you may retry after {wait_minutes} minutes.",
                "SIMPLIFIED_CHINESE": f"你达到了发送邮件的次数限制，你最好等{wait_minutes}分钟后再尝试",
            },
            alert_admin=alert_admin,
        )


class SmsSendingLimitReached(KebleException):
    def __init__(self, *, wait_minutes: str, alert_admin: bool):
        super(SmsSendingLimitReached, self).__init__(
            how_to_resolve={
                "ENGLISH": f"You have reached the sms limit, you may retry after {wait_minutes} minutes.",
                "SIMPLIFIED_CHINESE": f"你达到了发送短信的次数限制，你最好等{wait_minutes}分钟后再尝试",
            },
            alert_admin=alert_admin,
        )


class FrequencyLimitReached(KebleException):
    def __init__(self, *, wait_minutes: str, alert_admin: bool):
        super(FrequencyLimitReached, self).__init__(
            how_to_resolve={
                "ENGLISH": f"You are performing this action too often, you may retry after {wait_minutes} minutes.",
                "SIMPLIFIED_CHINESE": f"你尝试了太多次，请等候{wait_minutes}分钟后再尝试",
            },
            alert_admin=alert_admin,
        )
