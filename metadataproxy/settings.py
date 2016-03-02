from os import getenv


def bool_env(var_name, default=False):
    """
    Get an environment variable coerced to a boolean value.
    Example:
        Bash:
            $ export SOME_VAL=True
        settings.py:
            SOME_VAL = bool_env('SOME_VAL', False)
    Arguments:
        var_name: The name of the environment variable.
        default: The default to use if `var_name` is not specified in the
                 environment.
    Returns: `var_name` or `default` coerced to a boolean using the following
        rules:
            "False", "false" or "" => False
            Any other non-empty string => True
    """
    test_val = getenv(var_name, default)
    # Explicitly check for 'False', 'false', and '0' since all non-empty
    # string are normally coerced to True.
    if test_val in ('False', 'false', '0'):
        return False
    return bool(test_val)


def float_env(var_name, default=0.0):
    """
    Get an environment variable coerced to a float value.
    This has the same arguments as bool_env. If a value cannot be coerced to a
    float, a ValueError will be raised.
    """
    return float(getenv(var_name, default))


def int_env(var_name, default=0):
    """
    Get an environment variable coerced to an integer value.
    This has the same arguments as bool_env. If a value cannot be coerced to an
    integer, a ValueError will be raised.
    """
    return int(getenv(var_name, default))


def str_env(var_name, default=''):
    """
    Get an environment variable as a string.
    This has the same arguments as bool_env.
    """
    return getenv(var_name, default)


DEFAULT_ROLE = str_env('DEFAULT_ROLE')
PORT = int_env('PORT', 45001)
HOST = str_env('HOST', '0.0.0.0')
DEBUG = bool_env('DEBUG', True)
MOCK_API = bool_env('MOCK_API', False)
METADATA_URL = str_env('METADATA_URL', 'http://169.254.169.254')
MOCKED_INSTANCE_ID = str_env('MOCKED_INSTANCE_ID', 'mockedid')
ROLE_MAPPING_FILE = str_env('ROLE_MAPPING_FILE')
ROLE_REVERSE_LOOKUP = bool_env('ROLE_REVERSE_LOOKUP', False)
HOSTNAME_MATCH_REGEX = str_env('HOSTNAME_MATCH_REGEX', '^.*$')
DOCKER_URL = str_env('DOCKER_URL', 'unix://var/run/docker.sock')
