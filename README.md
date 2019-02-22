# py_vuln_detection

User input (methods/variables) are initialized in the user_inputs set()

Dangerous functions are initialized in the bad_functions dictionary as {string:[dangerous parameter, cleaning functions]}

Cleaning functions are functions that clean unsafe input

Preliminary version with a lot bugs


Todo:

Refactor to get rid of redundant/ugly/non-pythonic code

Deal with nested function calls of depth more than 1

Functions that return user input can be treated as dangerous variables

Duplicate method names may cause false positives (last one declared is the one that's actually defined)

Dealing with method calls before said methods are declared (e.g. potential dangerous calls)

Local/nonlocal/global variables

Tuple assignment/reassignment

Look into other magic methods other than __init__


Inspired by: http://php-security.org/downloads/rips.pdf
