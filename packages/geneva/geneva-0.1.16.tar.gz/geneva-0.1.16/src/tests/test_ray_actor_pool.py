# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import itertools

import pytest

try:
    import ray

    from geneva.runners.ray.actor_pool import ActorPool
except ImportError:
    import pytest

    pytest.skip("failed to import ray", allow_module_level=True)


@ray.remote
class TestActor:
    def echo(self, i: int) -> int:
        return i


@pytest.mark.parametrize(
    ("num_calls", "num_actors"),
    list(itertools.product([1000], range(5, 12))),
)
def test_actor_pool(
    num_calls: int,
    num_actors: int,
) -> None:
    # do it twice should not affect the result
    pool = ActorPool(TestActor.remote, num_actors)
    unordered_res = pool.map_unordered(
        lambda actor, i: actor.echo.remote(i), range(num_calls)
    )
    unordered_res = list(unordered_res)
    assert list(range(num_calls)) == sorted(unordered_res)
    assert len(unordered_res) == num_calls
    assert list(range(num_calls)) != unordered_res


@pytest.mark.parametrize(
    ("num_calls", "num_actors"),
    list(itertools.product([1000], range(5, 12))),
)
def test_actor_pool_fault_tolerance(
    num_calls: int,
    num_actors: int,
) -> None:
    # do it twice should not affect the result
    pool = ActorPool(TestActor.remote, num_actors, simulate_fault=True)
    for _ in range(2):
        unordered_res = pool.map_unordered(
            lambda actor, i: actor.echo.remote(i), range(num_calls)
        )
        unordered_res = list(unordered_res)
        assert list(range(num_calls)) == sorted(unordered_res)
        assert len(unordered_res) == num_calls
        assert list(range(num_calls)) != unordered_res
