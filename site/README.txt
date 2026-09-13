LLMs and Cybersecurity - offline copy of the lecture
===================================================

Opening index.html directly does not work: the viewer fetches the trace
over HTTP, which a file:// page is not allowed to do. Instead run

    python3 serve.py

from this folder. It starts a local web server and opens the lecture in
your browser (http://localhost:8000/?trace=01_intro).

Navigation: right/left arrow step forward/back, shift+arrows step over a
call, 'u' steps out, 'N' toggles the instructor notes, 'E' the variable
panel, 'A' the reveal animation, 'g' loads another trace.

01_intro.pdf, next to this file, is the same lecture as a printable
handout (if it was built).

What this is, exactly: a recording. It holds the lecture's source and
every step that was executed, with the values and output of that run -
not a running Python program. It is all you need to follow the lecture.
To ask the models something of your own, or to read the code behind the
case studies (which is not in here), clone the repository:
    https://github.com/MatteoBoffa/Lecture-LLM_Cybersecurity
