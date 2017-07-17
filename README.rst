experiments for the
`graph golf challenge <http://research.nii.ac.jp/graphgolf/>`__

concepts for performance
========================

* use PyPy3
* semantically

  * if beneficial for performance

    * implement as much domain knowledge as possible
    * do invariant and sanity checks using ``assert`` statements

      * so we can easily skip them with the "-O" option

    * classes/instances do only what is inherently needed

      * more responsibility for callers

        * callers often can act more precise/targeted since they have
          more information

      * e.g. a function expects a list with unique items as argument;
        instead of just making the items in the list unique (suppose
        order does not matter), the functions requires the caller to
        supply a list with only unique items; the caller - with its
        additional knowledge - might be able to avoid duplicate items in
        the list in the first place

* `adhere to Python performance tips <https://wiki.python.org/moin/PythonSpeed/PerformanceTips>`__

  * keep in mind that with PyPy (w/ JIT etc.) things might be a bit different

    * but it won't get worse adhering to the tips, thought

* data structures

  * i.e. mainly sets vs. lists vs. tuples vs. dicts etc.
  * identify possible types basic properties

    * do we need order?
    * do we need uniqueness?
    * do we need mutability?

  * identify predominant operation

    * iterate
    * add/append
    * remove
    * member checks
    * ...

  * choose data structure by performance measurements of predominant
    operations

    * e.g. w/ module ``timeit``
