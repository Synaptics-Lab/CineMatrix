"""Automated Test Suite for CineMatrix Platform."""
import pytest
from cinematrix.models import StreamingEvent, BoxOfficeSale, RoyaltyRecipient
from cinematrix.clickhouse_engine import ClickHouseEngine
from cinematrix.onchain_settler import OnChainSettler
from cinematrix.tools import StudioToolRegistry
from cinematrix.agent import StudioDirectorAgent

@pytest.fixture
def setup_cinematrix():
    ch = ClickHouseEngine()
    settler = OnChainSettler()
    tools = StudioToolRegistry(ch, settler)
    agent = StudioDirectorAgent(tools, model="gemini-3.1-pro")
    return ch, settler, tools, agent

def test_box_office_analytics(setup_cinematrix):
    ch, settler, tools, agent = setup_cinematrix
    res = tools.query_box_office_analytics(title_id="dune-part-3")
    assert res["total_tickets_sold"] > 0
    assert res["total_gross_usd"] > 0
    assert "IMAX" in res["gross_by_screen_format"]

def test_viewer_retention_curve(setup_cinematrix):
    ch, settler, tools, agent = setup_cinematrix
    ret = tools.analyze_viewer_retention_curve(title_id="dune-part-3")
    assert ret["total_sample_viewers"] > 0
    assert len(ret["retention_curve"]) > 0
    assert "00:42:18" in ret["critical_drop_scene_timestamp"]

def test_fraud_detection(setup_cinematrix):
    ch, settler, tools, agent = setup_cinematrix
    fraud = tools.detect_streaming_fraud(title_id="dune-part-3")
    assert fraud["flagged_anomalies_count"] == 2
    assert fraud["quarantined_revenue_usd"] > 0

def test_onchain_settlement_256_lanes(setup_cinematrix):
    ch, settler, tools, agent = setup_cinematrix
    split_res = tools.execute_cast_royalty_split(title_id="dune-part-3", gross_revenue_usd=10000000.0)
    assert split_res["status"] == "ONCHAIN_SETTLEMENT_CONFIRMED"
    assert split_res["total_recipients"] == 6
    assert len(split_res["receipts"]) == 6
    # Verify lane assignments are within [0, 255] and tx hashes are 0x-prefixed
    for r in split_res["receipts"]:
        assert 0 <= r["lane_id"] < 256
        assert r["tx_hash"].startswith("0x")
        assert r["finality_ms"] < 150.0

def test_gemini_director_reasoning(setup_cinematrix):
    ch, settler, tools, agent = setup_cinematrix
    prompt = "Analyze box office drop-off and execute cast royalty splits for Dune Part 3."
    response = agent.execute_prompt(prompt, title_id="dune-part-3")
    assert response.response is not None
    assert len(response.executed_tools) >= 2
    assert len(response.settlement_receipts) == 6

def test_mcp_server_tools():
    """Verifies all 5 tools on the official Model Context Protocol (MCP) server execute and serialize cleanly."""
    import json
    from cinematrix.mcp_server import (
        query_box_office_analytics,
        analyze_viewer_retention_curve,
        detect_streaming_fraud,
        execute_cast_royalty_split,
        predict_box_office_dropoff
    )
    
    # 1. Box Office
    bo = json.loads(query_box_office_analytics("dune-part-3"))
    assert bo["total_tickets_sold"] > 0
    
    # 2. Retention
    ret = json.loads(analyze_viewer_retention_curve("dune-part-3"))
    assert "00:42:18" in ret["critical_drop_scene_timestamp"]
    
    # 3. Fraud
    fraud = json.loads(detect_streaming_fraud("dune-part-3"))
    assert fraud["flagged_anomalies_count"] >= 1
    
    # 4. Multi-Lane Royalty Split
    split = json.loads(execute_cast_royalty_split("dune-part-3", 10000000.0))
    assert split["status"] == "ONCHAIN_SETTLEMENT_CONFIRMED"
    assert len(split["receipts"]) == 6
    
    # 5. Drop-off Prediction
    pred = json.loads(predict_box_office_dropoff("dune-part-3", 45000000.0))
    assert "projected_week_2_usd" in pred

