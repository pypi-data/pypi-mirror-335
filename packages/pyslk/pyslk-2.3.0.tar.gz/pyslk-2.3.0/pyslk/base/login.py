import re
from datetime import datetime

from ..raw import hostname_raw, session_raw
from ..utils import convert_expiration_date

__all__ = ["expiration_date", "session", "hostname", "valid_session", "valid_token"]


def valid_token() -> bool:
    """Returns whether session token is valid or not

    :returns: True if valid token exists; False otherwise
    :rtype: ``bool``
    """
    exit_code: int = session_raw(return_type=1)
    if exit_code == 0:
        return True
    else:
        return False


def valid_session() -> bool:
    """Returns whether session token is valid or not

    :returns: True if valid token exists; False otherwise
    :rtype: ``bool``
    """
    return valid_token()


def session() -> datetime:
    """Shows expiration date of your token

    :returns: expiration date of the login token
    :rtype: ``datetime``
    """
    output = session_raw()
    str_date = re.search(
        "[A-Z][a-z]{2} [A-Z][a-z]{2} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ [0-9]{4}",
        output,
    ).group(0)
    return convert_expiration_date(str_date)


def expiration_date() -> datetime:
    """Shows expiration date of your token

    :returns: expiration date of the login token
    :rtype: ``datetime``
    """
    return session()


def hostname() -> str:
    """Shows current hostname you are connected to

    :returns: hostname of the StrongLink system to which slk and slk_helpers currently connect to
    :rtype: ``str``
    """
    return hostname_raw()
