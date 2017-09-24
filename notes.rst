* more optimization ideas

    * stop ``GolfGraph.analyze`` if a found path is longer than the last
      diameter?

      * return False?

    * remember long paths, analyze those first next time

      * would provoke filling the hops caches early

* observations regarding the different enhancers

  * idea: allow ``n`` modifications of graphs without actual enhancement
    to escape from local optima

    * result: does not seem to yield enhancements

  * most enhancers yield virtually no enhancements for non-random graphs

    * randomly relink most distant vertices of (all) paths
    * connect most distant vertices of (all) paths

      * appears to stagnate easily

    * randomly replace one edge

      * when most ports are in use (which is usual), the likelihood
        of just re-creating the just removed edge is very high

    * randomly replace ``x`` percent of edges

        * idea was to escape from local optima
        * does not seem to be efficient enough to yield any helpful
          results

      * additionally, stagnates when lower bound of diameter reached

        * needs manual re-configuration when lower bound reached

          * not suitable for non-supervised operation

    * randomly relink most distant vertices in too long paths

      * where "too long" refers to longer than the diameter's lower bound
      * idea was, that shorter routes between the two most distant
        vertices emerge

    * randomly relink all in too long paths

      * idea was to just start from scratch with non-optimal paths

  * randomly link two edges

    * enhances in terribly small steps
    * stagnates the least
