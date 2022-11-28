import os
from typing import Any


class Sentinel:
    """Similar to Symbol in JavaScript."""

    def __init__(self, name=''):
        self.name = f"Sentinel({name})"

    def __repr__(self): # pragma: no cover
        return self.name


NotSet = Sentinel('NOT_SET')


def getenv(key: str, default: Any = NotSet) -> Any:
    """Retrive a value from the environment.

    Args:
        key (str): The variable name.
        default (Any, optional): A default value to fall back on. Defaults to NotSet.

    Raises:
        EnvironmentError: When no default has been set and the variable is not found.

    Returns:
        Any: The value of the ENV variable unless missing and default was set.
    """

    if key in os.environ:
        return os.environ[key]

    if default is NotSet: # pragma: no cover
        raise EnvironmentError(
            f'The envrironment variable "{key}" was not found and no default was set.')
    return default


ENVIRONMENT = getenv('ENVIRONMENT')
if ENVIRONMENT not in ['development', 'staging', 'production']: # pragma: no cover
    raise EnvironmentError(
        f'Invalid environment "{ENVIRONMENT}" found in the environment variable "ENVIRONMENT".')

PRODUCTION = ENVIRONMENT == 'production'
STAGING = ENVIRONMENT == 'staging'
DEVELOPMENT = ENVIRONMENT == 'development'

DATABASE_URL = getenv('DATABASE_URL')
JWT_SECRET = getenv('JWT_SECRET')
JWT_EXPIRE_TIMEPUT_MINUTES = int(getenv('JWT_EXPIRE_TIMEPUT_MINUTES', 60))
STRIPE_PRIVATE_KEY = getenv('STRIPE_PRIVATE_KEY')
STRIPE_SIGNING_KEY = getenv('STRIPE_SIGNING_KEY')

BASE_URL_UI = getenv('BASE_URL_UI')
BASE_URL_API = getenv('BASE_URL_API')

POSITIONSTACK_API_KEY = getenv('POSITIONSTACK_API_KEY')
