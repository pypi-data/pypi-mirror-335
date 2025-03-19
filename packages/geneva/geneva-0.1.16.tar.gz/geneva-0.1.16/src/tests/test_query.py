# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from pathlib import Path

import pyarrow as pa

from geneva.query import Scan, connect


def test_scan_over_fragments(tmp_path: Path) -> None:
    db = connect(tmp_path)

    a = pa.array([1, 2, 3])
    b = pa.array([4, 5, 6])
    tbl = db.create_table("tbl", pa.Table.from_arrays([a, b], names=["a", "b"]))

    c = pa.array([7, 8, 9])
    d = pa.array([10, 11, 12])
    tbl.add(pa.Table.from_arrays([c, d], names=["a", "b"]))

    fragments = tbl.get_fragments()
    assert len(fragments) == 2

    scan = Scan(tbl, columns=["a"]).with_fragments(fragments[0].fragment_id)
    results = list(scan.to_batches())

    assert len(results) == 1
    assert results[0]["a"].equals(a)
