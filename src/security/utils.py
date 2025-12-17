import secrets


def generate_secure_token(length: int=32) -> str:
    """
    Generates a secure random token
    :param length: Length of the token
    :return: Secure token
    """
    return secrets.token_urlsafe(length)
