"""Data models for CineMatrix telemetry, analytics, and on-chain settlements."""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class StreamingEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title_id: str
    viewer_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    watch_duration_seconds: int
    completion_rate: float
    territory: str  # North America, EMEA, APAC, LATAM
    device_type: str  # SmartTV, Mobile, Web, VR
    bitrate_mbps: float
    is_premium_tier: int = 1

class BoxOfficeSale(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title_id: str
    theater_id: str
    territory: str
    screen_format: str  # IMAX, Dolby, 3D, Standard
    ticket_price_usd: float
    timestamp: datetime = Field(default_factory=utc_now)

class RoyaltyRecipient(BaseModel):
    name: str
    role: str  # Director, Lead Cast, Composer, VFX Lead, Stunt Crew, Studio
    wallet_address: str
    share_bps: int  # Basis points: e.g. 1500 = 15.00%

class RoyaltySplitReceipt(BaseModel):
    split_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title_id: str
    recipient_name: str
    recipient_role: str
    wallet_address: str
    share_bps: int
    gross_basis_usd: float
    payout_amount_susd: float
    lane_id: int
    tx_hash: str
    finality_ms: float
    block_height: int
    timestamp: datetime = Field(default_factory=utc_now)

class DirectorPromptRequest(BaseModel):
    prompt: str
    title_id: Optional[str] = "dune-part-3"
    model: Optional[str] = "gemini-3.1-pro"

class DirectorPromptResponse(BaseModel):
    response: str
    model_used: str
    executed_tools: List[Dict[str, Any]] = []
    settlement_receipts: List[RoyaltySplitReceipt] = []
    timestamp: datetime = Field(default_factory=utc_now)
