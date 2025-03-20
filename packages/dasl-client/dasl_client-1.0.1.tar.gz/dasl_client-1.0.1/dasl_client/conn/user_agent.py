from importlib.metadata import version


def get_user_agent() -> str:
    """
    A helper function defining the user agent for requests originating from
    the ASL python conn library. We include the version of the API that the
    conn was built off.
    :return: A user-agent string.
    """
    return f"asl/python-conn/{version('dasl_api')}"
