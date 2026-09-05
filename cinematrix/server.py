"""FastAPI Production Server for CineMatrix Studio Platform."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any

from cinematrix.models import DirectorPromptRequest, DirectorPromptResponse
from cinematrix.clickhouse_engine import ClickHouseEngine
from cinematrix.onchain_settler import OnChainSettler
from cinematrix.tools import StudioToolRegistry
from cinematrix.agent import StudioDirectorAgent

app = FastAPI(
    title="CineMatrix Studio Platform",
    description="Autonomous AI Studio Director & On-Chain Micro-Royalty SMR Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core engine instances
ch_engine = ClickHouseEngine()
onchain_settler = OnChainSettler()
tools = StudioToolRegistry(ch_engine, onchain_settler)
director_agent = StudioDirectorAgent(tools)

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "cinematrix-studio"}

@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    l1_status = onchain_settler.get_chain_status()
    return {
        "ok": True,
        "platform": "CineMatrix Studio Platform",
        "gemini_model": director_agent.model,
        "gemini_active": director_agent.client is not None,
        "clickhouse_connected": ch_engine.is_connected,
        "clickhouse_events_indexed": len(ch_engine.streaming_events) + len(ch_engine.box_office_sales),
        "synaptic_l1": {
            "canonical_height": l1_status.get("canonical_height", l1_status.get("checkpoint_height", 5200)),
            "tps": l1_status.get("tps", 420.0),
            "synced": l1_status.get("synced", True),
            "consensus": "SCBFT DAG-Primary (256-Lane SMR)"
        }
    }

@app.post("/api/director/chat", response_model=DirectorPromptResponse)
def director_chat(req: DirectorPromptRequest):
    return director_agent.execute_prompt(user_prompt=req.prompt, title_id=req.title_id or "dune-part-3")

@app.get("/api/analytics/box-office")
def box_office_analytics(title_id: str = "dune-part-3", territory: str = None):
    return tools.query_box_office_analytics(title_id=title_id, territory=territory)

@app.get("/api/analytics/retention")
def retention_analytics(title_id: str = "dune-part-3"):
    return tools.analyze_viewer_retention_curve(title_id=title_id)

@app.get("/api/fraud/detect")
def fraud_detection(title_id: str = "dune-part-3"):
    return tools.detect_streaming_fraud(title_id=title_id)

@app.post("/api/settlements/execute")
def execute_settlement(title_id: str = "dune-part-3", gross_usd: float = 45000000.0):
    return tools.execute_cast_royalty_split(title_id=title_id, gross_revenue_usd=gross_usd)

@app.get("/api/settlements/receipts")
def get_receipts(limit: int = 50):
    return ch_engine.get_recent_royalty_receipts(limit=limit)

# Mount web frontend if exists
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(web_dir, "index.html"))

def run():
    import uvicorn
    port = int(os.environ.get("PORT", 8312))
    uvicorn.run("cinematrix.server:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    run()
