# py_vuln_detection



Cleaning functions are functions that clean unsafe input for a respective dangerous function (e.g. in PHP, it's clean_html if you're echoing user input onto the client)

Preliminary version with a lot bugs

Todo (in no particular order)


1. OOP support. 
2. Functions that return user input can be treated as dangerous variables. Implement this. Functions that call dangerous functions with parameters can be treated as dangerous methods. Implement this.
3. Dealing with method calls before said methods are declared (e.g. potential dangerous calls)
4. Local/nonlocal/global variables
5. Tuple assignment/reassignment, decomposition of lists, dictionaries, etc

Some of these will take an hour, others longer

Inspired by: http://php-security.org/downloads/rips.pdf
