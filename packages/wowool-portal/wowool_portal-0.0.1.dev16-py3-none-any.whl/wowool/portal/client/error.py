from typing import Optional

from wowool.portal.client.httpcode import HttpCode


class ServerError(RuntimeError):
    """
    An error generated at the server-side.
    """

    def __init__(self, message: str, status_code: int, type: Optional[str] = None, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.type = type
        self.details = details
        super(ServerError, self).__init__(message)

    @property
    def status_code_name(self):
        if self.status_code:
            for name in dir(HttpCode):
                if self.status_code == getattr(HttpCode, name):
                    return name
        return ""


class ClientError(RuntimeError):
    """
    An error generated at the client-side.
    """

    pass
