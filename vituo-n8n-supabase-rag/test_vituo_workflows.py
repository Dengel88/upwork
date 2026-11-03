import json
import pathlib
import unittest


BASE_DIR = pathlib.Path(__file__).resolve().parent


class TestVituoN8nWorkflows(unittest.TestCase):
    def test_ingestion_workflow_uses_native_nodes_only(self):
        wf_path = BASE_DIR / "workflows" / "supabase_rag_ingestion.json"
        data = json.loads(wf_path.read_text(encoding="utf-8"))
        self.assertIn("nodes", data)
        node_types = [n["type"] for n in data["nodes"]]
        # Must NOT rely on brittle custom Code nodes
        self.assertNotIn("n8n-nodes-base.code", node_types)
        self.assertIn("@n8n/n8n-nodes-langchain.vectorStoreSupabase", node_types)
        self.assertIn("@n8n/n8n-nodes-langchain.embeddingsOpenAi", node_types)

    def test_agent_workflow_uses_gpt4o_mini_and_native_tools(self):
        wf_path = BASE_DIR / "workflows" / "google_workspace_agent.json"
        data = json.loads(wf_path.read_text(encoding="utf-8"))
        node_types = [n["type"] for n in data["nodes"]]
        self.assertNotIn("n8n-nodes-base.code", node_types)
        self.assertIn("@n8n/n8n-nodes-langchain.agent", node_types)
        self.assertIn("n8n-nodes-base.googleCalendarTool", node_types)
        self.assertIn("n8n-nodes-base.gmailTool", node_types)

        openai_nodes = [n for n in data["nodes"] if n["type"] == "@n8n/n8n-nodes-langchain.lmChatOpenAi"]
        self.assertEqual(len(openai_nodes), 1)
        self.assertEqual(openai_nodes[0]["parameters"]["model"]["value"], "gpt-4o-mini")

    def test_proposal_starts_with_secret_codeword_vituo(self):
        proposal_path = BASE_DIR / "PROPOSAL.md"
        text = proposal_path.read_text(encoding="utf-8").lstrip()
        self.assertTrue(text.startswith("VITUO"), "PROPOSAL.md must start with secret codeword VITUO")


if __name__ == "__main__":
    unittest.main()
