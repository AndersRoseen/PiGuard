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


def _get_credentials():
    credentials = set()
    list_cred = configmanager.config["auth"]["credentials"].split(",")
    for cred in list_cred:
        credentials.add(str(base64.b64encode(bytes(cred, "utf-8")), "utf-8"))

    return credentials

manager = AuthManager(_get_credentials())
