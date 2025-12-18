from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=14, deprecated="auto")


def hash_password(raw_password: str) -> str:
    """
    Hash a plain-text password using the configured password context.

    This function takes a plain-text password and returns its bcrypt hash.
    The bcrypt algorithm is used with a specified number of rounds for enhanced security.

    Args:
        raw_password(str): The plain-text password to hash.

    Returns:
        str: The resulting hashed password.
    """
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against the configured password context.

    :param raw_password: The plain-text password to verify provided by user.
    :param hashed_password: The bcrypt hashed password stored in database.
    :return: bool: True if the password matches the stored password, False otherwise.
    """
    return pwd_context.verify(raw_password, hashed_password)
