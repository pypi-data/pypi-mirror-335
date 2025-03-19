# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Ray Authors
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# forked actor pool from ray.util.actor_pool
# we will add FT and autoscaling to this implementation

import contextlib
import logging
import random
from collections.abc import Callable, Iterable, Iterator
from typing import Any, TypeVar

import ray
import ray.actor
import ray.exceptions

V = TypeVar("V")

_LOG = logging.getLogger(__name__)


class ActorPool:
    """Utility class to operate on a fixed pool of actors.

    Arguments:
        actors: List of Ray actor handles to use in this pool.

    Examples:
        .. testcode::

            import ray
            from ray.util.actor_pool import ActorPool

            @ray.remote
            class Actor:
                def double(self, v):
                    return 2 * v

            a1, a2 = Actor.remote(), Actor.remote()
            pool = ActorPool([a1, a2])
            print(list(pool.map(lambda a, v: a.double.remote(v),
                                [1, 2, 3, 4])))

        .. testoutput::

            [2, 4, 6, 8]
    """

    def __init__(
        self,
        actors_factory: Callable[[], Any],
        num_actors: int,
        *,
        simulate_fault: bool = False,
    ) -> None:
        # factory to create actors
        self._actor_factory = actors_factory

        # number of actors
        self._num_actors = num_actors

        # readyness future to actor
        self._ready_fut_to_actor = {}

        # actors to be used
        self._idle_actors = []

        # get actor from future
        self._future_to_actor = {}

        # get future from index
        self._index_to_future = {}

        # next task to do
        self._next_task_index = 0

        # next work depending when actors free
        self._pending_submits = []

        # the task that was submitted
        self._future_to_task = {}

        # simulate fault
        self._simulate_fault = simulate_fault

        for _ in range(num_actors):
            self._queue_actor_startup()

    def _queue_actor_startup(self) -> None:
        new_actor = self._actor_factory()
        ready_fut = new_actor.__ray_ready__.remote()
        self._ready_fut_to_actor[ready_fut] = new_actor

    def _collect_ready_actors(self) -> None:
        futs = list(self._ready_fut_to_actor.keys())
        # only take one ready actor at a time to taper the scaleup rate
        ready, _ = ray.wait(futs, num_returns=1, timeout=0.0)

        for fut in ready:
            _LOG.debug("Adding ready actors to pool: %s", fut)
            actor = self._ready_fut_to_actor.pop(fut)
            try:
                ray.get(fut)
                self._return_actor(actor)
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                _LOG.exception("Actor died or unavailable, cleaning it up")
                ray.kill(actor)
                self._queue_actor_startup()

    def _map(
        self,
        fn: Callable[["ray.actor.ActorHandle", V], Any],
        values: Iterable[V],
        *,
        ordered: bool,
    ) -> Iterator[Any]:
        # Ignore/Cancel all the previous submissions
        # by calling `has_next` and `gen_next` repeteadly.
        while self.has_next():
            with contextlib.suppress(TimeoutError):
                self.get_next_unordered(timeout=0)

        it = iter(values)

        def _maybe_submit() -> bool:
            try:
                v = next(it)
            except StopIteration:
                return False
            self.submit(fn, v)
            return True

        # prime the workers
        # always have one pending task so when we call get_next or get_next_unordered
        # we can submit task immediately without waiting for the puller to yield back
        submits = self._num_actors + 1
        while submits and _maybe_submit():
            submits -= 1

        next_fn = self.get_next_unordered

        while self.has_next():
            yield next_fn()
            _maybe_submit()

    def map_unordered(
        self, fn: Callable[["ray.actor.ActorHandle", V], Any], values: Iterable[V]
    ) -> Iterator[Any]:
        """Similar to map(), but returning an unordered iterator.

        This returns an unordered iterator that will return results of the map
        as they finish. This can be more efficient that map() if some results
        take longer to compute than others.

        Arguments:
            fn: Function that takes (actor, value) as argument and
                returns an ObjectRef computing the result over the value. The
                actor will be considered busy until the ObjectRef completes.
            values: Iterable of values that fn(actor, value) should be
                applied to.

        Returns:
            Iterator over results from applying fn to the actors and values.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1, a2 = Actor.remote(), Actor.remote()
                pool = ActorPool([a1, a2])
                print(list(pool.map_unordered(lambda a, v: a.double.remote(v),
                                              [1, 2, 3, 4])))

            .. testoutput::
                :options: +MOCK

                [6, 8, 4, 2]
        """
        yield from self._map(fn, values, ordered=False)

    def submit(self, fn, value) -> None:
        """Schedule a single task to run in the pool.

        This has the same argument semantics as map(), but takes on a single
        value instead of a list of values. The result can be retrieved using
        get_next() / get_next_unordered().

        Arguments:
            fn: Function that takes (actor, value) as argument and
                returns an ObjectRef computing the result over the value. The
                actor will be considered busy until the ObjectRef completes.
            value: Value to compute a result for.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1, a2 = Actor.remote(), Actor.remote()
                pool = ActorPool([a1, a2])
                pool.submit(lambda a, v: a.double.remote(v), 1)
                pool.submit(lambda a, v: a.double.remote(v), 2)
                print(pool.get_next(), pool.get_next())

            .. testoutput::

                2 4
        """
        if self._idle_actors:
            actor = self._idle_actors.pop()
            future = fn(actor, value)
            future_key = tuple(future) if isinstance(future, list) else future
            self._future_to_actor[future_key] = (self._next_task_index, actor)
            self._index_to_future[self._next_task_index] = future
            self._next_task_index += 1
            self._future_to_task[future_key] = (fn, value)
        else:
            self._pending_submits.append((fn, value))

    def has_next(self) -> bool:
        """Returns whether there are any pending results to return.

        Returns:
            True if there are any pending results not yet returned.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1, a2 = Actor.remote(), Actor.remote()
                pool = ActorPool([a1, a2])
                pool.submit(lambda a, v: a.double.remote(v), 1)
                print(pool.has_next())
                print(pool.get_next())
                print(pool.has_next())

            .. testoutput::

                True
                2
                False
        """
        return bool(self._future_to_actor) or bool(self._pending_submits)

    class NoResult: ...

    def _get_next_by_fut(self, futures, timeout=None) -> Any | NoResult:
        timeout_msg = "Timed out waiting for result"

        # get_next will just pass a single future
        # get_next_unordered will pass a list of futures
        res, _ = ray.wait(futures, num_returns=1, timeout=timeout, fetch_local=True)
        if res:
            [future] = res
        else:
            raise TimeoutError(timeout_msg)

        i, a = self._future_to_actor.pop(future)
        fn, task = self._future_to_task.pop(future)
        del self._index_to_future[i]

        try:
            # this is fast because ray.wait already fetched the result
            res = ray.get(future)
            # don't return the future till we get the result
            # because the actor could be dead
            self._return_actor(a)
        except (ray.exceptions.ActorDiedError, ray.exceptions.ActorUnavailableError):
            _LOG.exception("Actor died or unavailable, cleaning it up")
            ray.kill(a)
            # queue a new actor
            self._queue_actor_startup()
            # resubmit the task
            self.submit(fn, task)
            return self.NoResult

        return res

    def get_next_unordered(self, timeout=None) -> Any:
        """Returns any of the next pending results.

        This returns some result produced by submit(), blocking for up to
        the specified timeout until it is available. Unlike get_next(), the
        results are not always returned in same order as submitted, which can
        improve performance.

        Returns:
            The next result.

        Raises:
            TimeoutError: if the timeout is reached.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1, a2 = Actor.remote(), Actor.remote()
                pool = ActorPool([a1, a2])
                pool.submit(lambda a, v: a.double.remote(v), 1)
                pool.submit(lambda a, v: a.double.remote(v), 2)
                print(pool.get_next_unordered())
                print(pool.get_next_unordered())

            .. testoutput::
                :options: +MOCK

                4
                2
        """
        if not self.has_next():
            raise StopIteration("No more results to get")
        # collect ready actors

        def _get_futs() -> list:
            while (self._collect_ready_actors() or True) and not (
                futs := list(self._future_to_actor)
            ):
                ...
            return futs

        # poll till we have a result
        while (item := self._get_next_by_fut(_get_futs(), timeout)) == self.NoResult:
            ...

        return item

    def _return_actor(self, actor) -> None:
        if self._simulate_fault and random.random() < 0.01:
            ray.kill(actor)
        self._idle_actors.append(actor)
        if self._pending_submits:
            self.submit(*self._pending_submits.pop(0))

    def has_free(self) -> bool:
        """Returns whether there are any idle actors available.

        Returns:
            True if there are any idle actors and no pending submits.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1 = Actor.remote()
                pool = ActorPool([a1])
                pool.submit(lambda a, v: a.double.remote(v), 1)
                print(pool.has_free())
                print(pool.get_next())
                print(pool.has_free())

            .. testoutput::

                False
                2
                True
        """
        return len(self._idle_actors) > 0 and len(self._pending_submits) == 0

    def pop_idle(self) -> bool:
        """Removes an idle actor from the pool.

        Returns:
            An idle actor if one is available.
            None if no actor was free to be removed.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1 = Actor.remote()
                pool = ActorPool([a1])
                pool.submit(lambda a, v: a.double.remote(v), 1)
                assert pool.pop_idle() is None
                assert pool.get_next() == 2
                assert pool.pop_idle() == a1

        """
        if self.has_free():
            return self._idle_actors.pop()
        return None

    def push(self, actor) -> None:
        """Pushes a new actor into the current list of idle actors.

        Examples:
            .. testcode::

                import ray
                from ray.util.actor_pool import ActorPool

                @ray.remote
                class Actor:
                    def double(self, v):
                        return 2 * v

                a1, a2 = Actor.remote(), Actor.remote()
                pool = ActorPool([a1])
                pool.push(a2)
        """
        busy_actors = []
        if self._future_to_actor.values():
            _, busy_actors = zip(*self._future_to_actor.values(), strict=False)
        if actor in self._idle_actors or actor in busy_actors:
            raise ValueError("Actor already belongs to current ActorPool")
        else:
            self._return_actor(actor)
