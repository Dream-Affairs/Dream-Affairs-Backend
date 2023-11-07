import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    pw_bytes = password.encode("utf-8")

    # generating the salt
    salt = bcrypt.gensalt()

    # Hashing the password
    return bcrypt.hashpw(pw_bytes, salt)
