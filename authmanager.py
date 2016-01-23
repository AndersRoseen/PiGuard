import factory


_credentials = factory.get_credentials()


def authenticate(token):
    global _credentials
    if token in _credentials:
        return True
    else:
        return False
