import json
import tempfile
import unittest
from pathlib import Path

from event_bridge import EventBridge
from llm_chain import select_local_model
from project_state import load_project_state, save_project_state


class ProjectFoundationTests(unittest.TestCase):
    def test_hybrid_fallback_selects_specialized_models(self) -> None:
        self.assertIn("qwen2.5-coder", select_local_model([], "coder"))
        self.assertIn("gemma4", select_local_model([], "business_strategist"))

    def test_event_contract_is_json_serializable(self) -> None:
        event = EventBridge().emit("coder_1", "walking", "laboratorio", "Generando módulo")
        self.assertEqual(json.loads(json.dumps(event))["destination"], "laboratorio")

    def test_state_round_trip(self) -> None:
        workspace = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=workspace) as directory:
            path = Path(directory) / "state.json"
            save_project_state({"phase": "CODING", "idea": "MVP"}, path)
            self.assertEqual(load_project_state(path)["idea"], "MVP")

