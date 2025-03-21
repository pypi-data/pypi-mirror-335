# numerical

Python library I made to learn regex and to have a better version of str.isnumeric()

Uploading to PyPI was a horrible experience and they rejected the name without telling me why (too similar to numerics?), so its called better-is-numeric there.

Supports decimals and negative numbers, managed by flags.

Should work down to Python 3.9.

Importing is kind of ugly, maybe I'll fix it one day. In the meantime, you can avoid this and the PyPI name by just downloading the code from the Codeberg repository and putting it in the same directory as your program, for a simple `from numerical import *`

Here's some example code:
```python
from is_numeric.numerical import *

print(is_numeric("1", {NM_ALLOW_NEGATIVE, NM_ALLOW_DECIMALS}))
```

This will print True, since the ALLOW flags do not require, they only allow.

A known "issue" with the library is that numbers like `01` will be recognized, but something like int() will strip the leading zero anyway.

I've copied this from the docstring(?) of the function, since it describes basically everything you need to know:

```
This function uses a "flag" system to control what's allowed and what isn't.
You can pass these in a set called "flags" in the arguments.
The flags are in variables, but you can also use their string values.
1: NM_RETURN_MATCH - Set to the string "RM", this flag makes the function return the raw output of the match function.
2: NM_ALLOW_NEGATIVE - Set to the string "AN" and enabled by default, this flag allows negative numbers.
3: NM_ALLOW_DECIMALS - Set to the string "AD", this flag allows numbers with decimals.
```

If you want no flags, try passing the result of `set()`