"""
An enhancement of str.isnumeric()
"""

from re import match

NM_RETURN_MATCH = "RM"
NM_ALLOW_NEGATIVE = "AN"
NM_ALLOW_DECIMALS = "AD"

def is_numeric(string:str, flags:set[str]=None):
    """
    This function uses a "flag" system to control what's allowed and what isn't.
    You can pass these in a set called "flags" in the arguments.
    The flags are in variables, but you can also use their string values.
    1: NM_RETURN_MATCH - Set to the string "RM", this flag makes the function return the raw output of the match function.
    2: NM_ALLOW_NEGATIVE - Set to the string "AN" and enabled by default, this flag allows negative numbers.
    3: NM_ALLOW_DECIMALS - Set to the string "AD", this flag allows numbers with decimals.
    """
    if flags is None: # this is ugly and adds unnecessary lines but my IDE complained
        flags = {NM_ALLOW_NEGATIVE}
    regex = "^" # make sure the string starts like this
    if NM_ALLOW_NEGATIVE in flags:
        regex += f"-?" # allow zero or one (no more than one) minus symbols
    regex += "[0-9]+" # allow one or more digits. must be digits
    if NM_ALLOW_DECIMALS in flags:
        regex += "(\\.[0-9]+)?" # allow zero or one instances of: a decimal point followed by one or more digits
    regex += "$" # make sure the string ends like this
    matched = match(regex, string)
    if NM_RETURN_MATCH in flags:
        return matched
    else:
        return bool(matched)