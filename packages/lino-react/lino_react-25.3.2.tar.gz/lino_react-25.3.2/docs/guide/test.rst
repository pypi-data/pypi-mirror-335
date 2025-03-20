=============
Testing react
=============

We use `jest` and `puppeteer` as javascript testing media.

Python unittest and doctest does NOT cover much of the testing
system and instead rely on javascript packages.

JEST setup
==========

Other then the configuration files, react has four important setup
files in `lino_react/react/testSetup` directory which are as follows::

.. xfile:: lino_react/react/testSetup/setupJEST.js

    Contains initial custom setup for puppeteer browser endpoint and
    runs lino_noi django runserver.

.. xfile:: lino_react/react/testSetup/teardownJEST.js

    Shuts down the lino_noi server and teardown puppeteer endpoint setup.

.. xfile:: lino_react/react/testSetup/testEnvironment.js

    Contains environment setup for each test suite.

.. xfile:: lino_react/react/testSetup/setupTests.ts

    Contains utility functions for test suites used to maintain
    synchronous code executions of each test block.

.. _react.jest.testcommand:

Tests using jest
================

The actual test files are located in the `lino_react/react/components/__test__`
directory.

To run the individual test such as the `integrity.ts`,
run the following command (from the root of repository)::

    $ npm run ntest lino_react/react/components/__test__/integrity.ts

To run all the test suites at once, call::

    $ npm run test
