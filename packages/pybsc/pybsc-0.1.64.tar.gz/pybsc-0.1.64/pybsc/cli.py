import sys


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    Parameters
    ----------
    question : str
        The question presented to the user.
    default : str, optional
        The presumed answer if the user just hits <Enter>.
        It must be one of "yes", "no", or None. Defaults to "yes".

    Returns
    -------
    bool
        True for "yes" or False for "no".

    Raises
    ------
    ValueError
        If the default answer is not one of "yes", "no", or None.

    Notes
    -----
    The function repeatedly prompts the user until they provide a valid
    yes/no response. The response is case-insensitive and accepts
    'y'/'yes' or 'n'/'no'.

    Examples
    --------
    >>> query_yes_no("Do you like Python?")
    Do you like Python? [Y/n]
    # User inputs 'yes'
    True

    >>> query_yes_no("Do you like Python?", default=None)
    Do you like Python? [y/n]
    # User inputs 'n'
    False
    """

    valid = {"yes": True, "y": True, "no": False, "n": False}
    prompt_options = {"yes": " [Y/n] ", "no": " [y/N] ", None: " [y/n] "}

    if default not in prompt_options:
        raise ValueError(f"Invalid default answer: '{default}'")

    prompt = prompt_options[default]

    while True:
        sys.stdout.write(f"{question}{prompt}")
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
