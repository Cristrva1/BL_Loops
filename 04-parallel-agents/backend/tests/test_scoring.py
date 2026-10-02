from parallel_agents.contracts import BranchView, FactBundle, FactRowView, LaneView, TableView
from parallel_agents.scoring import join_branches, score_bundle, score_lane
from parallel_agents.sources import load_sources


def test_passing_bundle_covers_required_facts() -> None:
    source = load_sources()[0]
    bundle = FactBundle.model_validate(
        {
            "source_id": "source-a",
            "facts": [
                {
                    "fact_id": "precio_basico",
                    "topic": "precio",
                    "value": "29",
                    "evidence": "plan basico 29",
                },
                {
                    "fact_id": "plan_taller",
                    "topic": "precio",
                    "value": "49",
                    "evidence": "plan taller 49",
                },
            ],
        }
    )

    ok, missing = score_bundle(source, bundle)

    assert ok is True
    assert missing == []


def test_join_omits_failed_branch_rows() -> None:
    branches = [
        BranchView(
            source_id="source-a",
            node_id="par-a",
            title="A",
            status="completed",
            facts=[
                FactRowView(
                    fact_id="precio_basico",
                    topic="precio",
                    value="29",
                    source_id="source-a",
                )
            ],
        ),
        BranchView(
            source_id="source-b",
            node_id="par-b",
            title="B",
            status="timeout",
            facts=[
                FactRowView(
                    fact_id="inventado",
                    topic="horario",
                    value="no",
                    source_id="source-b",
                )
            ],
        ),
    ]

    table = join_branches(branches)

    assert table.completed_sources == ["source-a"]
    assert table.failed_sources == ["source-b"]
    assert [row.source_id for row in table.rows] == ["source-a"]


def test_lane_fails_if_failed_source_leaks_into_completed() -> None:
    sources = load_sources()
    lane = LaneView(
        status="failed",
        passed=False,
        wall_ms=10,
        branches=[
            BranchView(source_id="source-a", node_id="par-a", title="A", status="completed"),
            BranchView(source_id="source-b", node_id="par-b", title="B", status="failed"),
            BranchView(source_id="source-c", node_id="par-c", title="C", status="completed"),
        ],
        table=TableView(
            rows=[
                FactRowView(
                    fact_id="x",
                    topic="t",
                    value="1",
                    source_id="source-b",
                )
            ],
            completed_sources=["source-a", "source-b"],
            failed_sources=["source-b"],
        ),
    )

    scored = score_lane(sources, lane)
    failed = {check.check_id: check for check in scored.checks if not check.passed}

    assert scored.passed is False
    assert "failed_not_complete" in failed
