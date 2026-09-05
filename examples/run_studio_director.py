#!/usr/bin/env python3
"""Interactive CLI demonstration of CineMatrix Studio Director Agent."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cinematrix.clickhouse_engine import ClickHouseEngine
from cinematrix.onchain_settler import OnChainSettler
from cinematrix.tools import StudioToolRegistry
from cinematrix.agent import StudioDirectorAgent

def main():
    print("=" * 80)
    print("  🎬 CineMatrix Studio Director — Interactive Terminal Showcase")
    print("  Google Gemini Pro 3.1 · ClickHouse Cloud · SynapticChain L1 SMR")
    print("=" * 80)

    ch = ClickHouseEngine()
    settler = OnChainSettler()
    tools = StudioToolRegistry(ch, settler)
    agent = StudioDirectorAgent(tools, model="gemini-3.1-pro")

    demo_prompts = [
        "Analyze opening weekend box office yields and IMAX screen format shares for Dune Part 3.",
        "Scan the streaming viewer retention curve and detect critical pacing anomalies.",
        "Run fraud detection against streaming telemetry to quarantine VPN botnets.",
        "Execute on-chain cast and crew royalty splits for $45,000,000 USD gross across parallel lanes."
    ]

    for i, prompt in enumerate(demo_prompts, 1):
        print(f"\n[{i}/4] 🎙️ EXECUTIVE PROMPT: '{prompt}'")
        resp = agent.execute_prompt(prompt, title_id="dune-part-3")
        print("\n" + resp.response)
        if resp.settlement_receipts:
            print("\n  ⚡ IMMUTABLE ON-CHAIN RECEIPTS:")
            for r in resp.settlement_receipts:
                print(f"    • [{r.recipient_role}] {r.recipient_name} -> ${r.payout_amount_susd:,.2f} sUSD (Lane {r.lane_id}, Tx: {r.tx_hash[:16]}..., Finality: {r.finality_ms}ms)")
        print("-" * 80)

if __name__ == "__main__":
    main()
