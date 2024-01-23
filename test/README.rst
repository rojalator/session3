Automated testing of session2
-----------------------------

The directory 'twill-tests' contains several tests that verify the
behavior of 'test_session2.py'.  To run them, you need to install
twill_ and nose_.  Then just execute 'nosetests' in the top directory.

You can also just run 'test_session2.py' with no command-line arguments
for help.

The tests do not test persistence or multithreading yet.

.. _twill: http://www.idyll.org/~t/www-tools/twill.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/


Download the quixote-main.zip, extract it then (e.g if it's in ~/qsetup/quixote-main):

    python -m pip install -e  ~/qsetup/quixote-main/

To start Quixote's demo:

    python -m quixote run

or

    python -m quixote run --app quixote.demo.altdemo  (This one for session testing)

or

    python -m quixote run --app quixote.demo.mini_demo


Then http://localhost:8080

To start the session3 quixote demo that has been modified for testing, move into the
test/ directory for session3:

    cd test

and run the demo

    python -m quixote run --app modified_quix_demo
