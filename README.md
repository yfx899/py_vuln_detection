# py_vuln_detection

User input (methods/variables) are initialized in the user_inputs set()

Dangerous functions are initialized in the bad_functions dictionary as {string:[dangerous parameter, cleaning functions]}

Cleaning functions are functions that clean unsafe input

Preliminary version with a lot bugs


Todo (in no particular order)

1. Refactor to get rid of redundant/ugly/non-pythonic code

2. Deal with nested function calls of depth more than 1

3. Functions that return user input can be treated as dangerous variables

4. Duplicate method names may cause false positives (last one declared is the one that's actually defined)

5. Dealing with method calls before said methods are declared (e.g. potential dangerous calls)

6. Local/nonlocal/global variables

7. Tuple assignment/reassignment

8. Look into other magic methods other than __init__


Some of these will take an hour, others much longer

Inspired by: http://php-security.org/downloads/rips.pdf
