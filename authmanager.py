import configmanager
import base64


def encode_credentials(credentials: str) -> str:
    return str(base64.b64encode(bytes(credentials, "utf-8")), "utf-8")


class AuthManager(object):

    def __init__(self, credentials: set):
        self._credentials = credentials

    def authenticate(self, token: str) -> bool:
        if token in self._credentials:
            return True
        else:
            return False

    def encode_and_authenticate(self, credentials: str) -> bool:
        return self.authenticate(encode_credentials(credentials))


def _get_credentials() -> set:
    credentials = set()
    list_cred = configmanager.config["auth"]["credentials"].split(",")
    for cred in list_cred:
        credentials.add(encode_credentials(cred))

    return credentials

manager = AuthManager(_get_credentials())
