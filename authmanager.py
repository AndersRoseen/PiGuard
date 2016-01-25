class AuthManager(object):

    def __init__(self, credentials):
        self._credentials = credentials

    def authenticate(self, token):
        if token in self._credentials:
            return True
        else:
            return False




