"""Tests for the command-line interface."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from cmdclever.cli.main import main


class TestCLI(unittest.TestCase):
    """Tests for the command-line interface."""
    
    @patch("cmdclever.cli.main.CmdAgent")
    @patch("sys.argv", ["cmd-clever", "test", "query"])
    def test_cli_with_query(self, mock_agent):
        """Test CLI with a query."""
        mock_instance = mock_agent.return_value
        mock_instance.run.return_value = "test response"
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
        
        mock_agent.assert_called_once_with(
            api_key=None, 
            api_base=None, 
            model_id="qwen-plus"
        )
        mock_instance.run.assert_called_once_with("test query", stream=True)
    
    @patch("cmdclever.cli.main.CmdAgent")
    @patch("sys.argv", ["cmd-clever", "--api-key", "test-key", "--api-base", "test-base", "test", "query"])
    def test_cli_with_api_params(self, mock_agent):
        """Test CLI with API parameters."""
        mock_instance = mock_agent.return_value
        mock_instance.run.return_value = "test response"
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
        
        mock_agent.assert_called_once_with(
            api_key="test-key", 
            api_base="test-base", 
            model_id="qwen-plus"
        )
        mock_instance.run.assert_called_once_with("test query", stream=True)
    
    @patch("cmdclever.cli.main.CmdAgent")
    @patch("sys.argv", ["cmd-clever", "--no-stream", "test", "query"])
    def test_cli_no_stream(self, mock_agent):
        """Test CLI with no-stream option."""
        mock_instance = mock_agent.return_value
        mock_instance.run.return_value = "test response"
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
        
        mock_agent.assert_called_once_with(
            api_key=None, 
            api_base=None, 
            model_id="qwen-plus"
        )
        mock_instance.run.assert_called_once_with("test query", stream=False)


if __name__ == "__main__":
    unittest.main() 