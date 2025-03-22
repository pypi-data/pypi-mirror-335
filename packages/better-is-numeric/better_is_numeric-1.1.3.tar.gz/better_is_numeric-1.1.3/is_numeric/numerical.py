"""
An enhancement of str.isnumeric()
"""

from re import match
from io import StringIO

NM_ALLOW_NEGATIVE = "AN"
NM_ALLOW_DECIMALS = "AD"
NM_ALLOW_LEADING_ZERO = "AZ"
NM_RETURN_MATCH = "RM"
NM_RETURN_REGEX = "RX"

def is_numeric(string:str, flags:set[str]=None):
    """
    This function uses a "flag" system to control what's allowed and what isn't.
    You can pass these in a set called "flags" in the arguments.
    Certain flags switch the function to dictionary output, to include whatever data you requested.
    The simple boolean output is still included in the dictionary output, in the "numeric" field.
    The flags are in variables, but you can also use their string values.
    1: NM_ALLOW_NEGATIVE - Set to the string "AN" and enabled by default, this flag allows negative numbers.
    2: NM_ALLOW_DECIMALS - Set to the string "AD", this flag allows numbers with decimals.
    3: NM_ALLOW_LEADING_ZERO - Set to the string "AZ" and enabled by default, this flag allows "invalid" numbers like 01.
    4: NM_RETURN_MATCH - Set to the string "RM", this flag uses dictionary output and returns the raw output of the match function inside the "match" field.
    5: NM_RETURN_REGEX - Set to the string "RX", this flag uses dictionary output and returns the constructed regex inside the "regex" field.
    """
    if flags is None: # this is ugly and adds unnecessary lines but my IDE complained
        flags = {NM_ALLOW_NEGATIVE, NM_ALLOW_LEADING_ZERO}
    regex = StringIO() # should be faster than being a string and using regex += "stuff"
    regex.write("^") # make sure the string starts like this
    if NM_ALLOW_NEGATIVE in flags:
        regex.write("-?") # allow zero or one (no more than one) minus symbols
    if NM_ALLOW_LEADING_ZERO in flags:
        regex.write("\\d+") # allow one or more digits. must be digits
    else:
        regex.write("([1-9]\\d*|0)") # allows either: a non-zero digit followed by any (including zero) amount of any digits OR a single zero
    if NM_ALLOW_DECIMALS in flags:
        regex.write("(\\.\\d+)?") # allow zero or one instances of: a decimal point followed by one or more digits
    regex.write("$") # make sure the string ends like this
    regex.seek(0)
    regex = regex.read()
    matched = match(regex, string)
    if NM_RETURN_MATCH in flags or NM_RETURN_REGEX in flags:
        output = {"numeric": bool(matched)} # ensure the user still gets the simple output as well as whatever they want
        if NM_RETURN_MATCH in flags:
            output["match"] = matched
        if NM_RETURN_REGEX in flags:
            output["regex"] = regex
        return output
    else:
        return bool(matched)