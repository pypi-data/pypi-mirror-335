"""Tests for the CmdAgent class."""
import unittest
from unittest.mock import patch, MagicMock
import os
from cmdclever.agent import CmdAgent


class TestCmdAgent(unittest.TestCase):
    """Tests for the CmdAgent class."""
    
    @patch.dict(os.environ, {"AGNO_API_KEY": "test-key", "AGNO_API_BASE": "test-base"})
    def test_init_from_env(self):
        """Test initialization using environment variables."""
        agent = CmdAgent()
        self.assertEqual(agent.api_key, "test-key")
        self.assertEqual(agent.api_base, "test-base")
        self.assertEqual(agent.model_id, "qwen-plus")
    
    def test_init_from_params(self):
        """Test initialization using parameters."""
        agent = CmdAgent(api_key="param-key", api_base="param-base", model_id="custom-model")
        self.assertEqual(agent.api_key, "param-key")
        self.assertEqual(agent.api_base, "param-base")
        self.assertEqual(agent.model_id, "custom-model")
    
    @patch.dict(os.environ, {})
    def test_missing_api_key(self):
        """Test that an error is raised when API key is missing."""
        with self.assertRaises(ValueError):
            CmdAgent(api_base="test-base")
    
    @patch.dict(os.environ, {"AGNO_API_KEY": "test-key"})
    def test_missing_api_base(self):
        """Test that an error is raised when API base is missing."""
        with self.assertRaises(ValueError):
            CmdAgent()
    
    @patch("cmdclever.agent.Agent")
    @patch("cmdclever.agent.OpenAILike")
    @patch.dict(os.environ, {"AGNO_API_KEY": "test-key", "AGNO_API_BASE": "test-base"})
    def test_run(self, mock_openai, mock_agent):
        """Test the run method."""
        mock_instance = mock_agent.return_value
        mock_instance.run.return_value = "test response"
        
        agent = CmdAgent()
        result = agent.run("test query")
        
        mock_instance.run.assert_called_once_with("test query", stream=True)
        self.assertEqual(result, "test response")


if __name__ == "__main__":
    unittest.main() 