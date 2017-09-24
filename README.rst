Experiments for the
`graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__.

Although this is (was) just a personal playground, feel free to join in!

To configure this tool according to your hardware, please see the bottom
of the file ``lib/enhancers.py``.

concepts
========

* see how far we can get with an implementation that runs on PyPy3

  * no C modules etc.

* semantically

  * if beneficial for performance (measure!)

    * implement as much domain knowledge as possible
    * do invariant and sanity checks using ``assert`` statements

      * so we can easily skip them with the "-O" option
      * also, we skip some debug statements using
        ``assert None is debug(...)``

        * nasty, sorry

    * classes/instances do only what is inherently needed

      * more responsibility for callers

        * callers often can act more precise/targeted since they tend to
          have more information available

      * e.g. a function expects a list with unique items as argument;
        instead of just making the items in the list unique, the
        function requires the caller to supply a list with only unique
        items; the caller - with its potential additional knowledge -
        might be able to avoid duplicate items in the first place

* `adhere to Python performance tips <https://wiki.python.org/moin/PythonSpeed/PerformanceTips>`__

  * keep in mind that with PyPy (w/ JIT etc.) things might be a bit different

    * but it usually won't get worse adhering to the tips, thought

* data structures

  * i.e. mainly sets vs. lists vs. tuples vs. dicts etc.
  * identify required properties

    * order?
    * uniqueness?
    * mutability?

  * identify predominant operation

    * iterate
    * add/append
    * remove
    * member checks
    * ...

  * choose data structure by performance measurements of predominant
    operations

    * e.g. w/ module ``timeit``
