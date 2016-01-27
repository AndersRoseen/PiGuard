import configmanager
import base64


class AuthManager(object):

    def __init__(self, credentials):
        self._credentials = credentials

    def authenticate(self, token):
        if token in self._credentials:
            return True
        else:
            return False


def encode_credentials(credentials):
    return str(base64.b64encode(bytes(credentials, "utf-8")), "utf-8")


def _get_credentials():
    credentials = set()
    list_cred = configmanager.config["auth"]["credentials"].split(",")
    for cred in list_cred:
        credentials.add(encode_credentials(cred))

    return credentials

manager = AuthManager(_get_credentials())
