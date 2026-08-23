import pandas as pd

from experiments.data_stream import build_stream_records, iter_stream_events


def _stream_df():
    rows = []
    for unit in [2, 1]:
        for cycle in [3, 1, 2]:
            rows.append(
                {
                    "unit": unit,
                    "cycle": cycle,
                    "RUL": float(10 - cycle),
                    **{f"op_setting_{i}": 0.0 for i in range(1, 4)},
                    **{f"sensor_{i}": float(unit * 10 + cycle) for i in range(1, 22)},
                }
            )
    return pd.DataFrame(rows)


def test_research_mode_preserves_unit_cycle_order():
    records = build_stream_records(_stream_df(), stream_mode="research", seed=1)

    assert [(row["unit"], row["cycle"]) for row in records] == [
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (2, 2),
        (2, 3),
    ]


def test_legacy_mode_is_seeded():
    df = _stream_df()

    assert build_stream_records(df, "legacy", seed=5) == build_stream_records(df, "legacy", seed=5)
    assert build_stream_records(df, "legacy", seed=5) != build_stream_records(df, "legacy", seed=6)


def test_same_seed_reproduces_fault_injection():
    records = build_stream_records(_stream_df(), stream_mode="research", seed=1)
    stds = {f"sensor_{i}": 1.0 for i in range(1, 22)}
    stds.update({f"op_setting_{i}": 1.0 for i in range(1, 4)})

    a = list(iter_stream_events(records, stds, "intermittent_spikes", 123, 20, 5))
    b = list(iter_stream_events(records, stds, "intermittent_spikes", 123, 20, 5))
    c = list(iter_stream_events(records, stds, "intermittent_spikes", 124, 20, 5))

    assert [event.data for event in a] == [event.data for event in b]
    assert [event.data for event in a] != [event.data for event in c]
    assert a[5].degradation_started is True
