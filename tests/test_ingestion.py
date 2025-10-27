from src.cs2_analyzer.application.ingestion import AwpyDemoParser
from pathlib import Path
from unittest.mock import Mock, patch


def test_awpy_demo_parser_parse():
    """Test that AwpyDemoParser correctly parses a demo file."""
    parser = AwpyDemoParser()

    # Mock the awpy Demo class
    with patch('src.cs2_analyzer.application.ingestion.Demo') as MockDemo:
        mock_demo_instance = Mock()
        mock_demo_instance.header = {'map_name': 'de_dust2'}
        mock_demo_instance.ticks = Mock()
        mock_demo_instance.events = {}
        mock_demo_instance.rounds = Mock()

        MockDemo.return_value = mock_demo_instance

        # Parse a demo
        result = parser.parse('test_path.dem')

        # Verify Demo was instantiated with Path
        MockDemo.assert_called_once()
        call_args = MockDemo.call_args[0][0]
        assert isinstance(call_args, Path)
        assert str(call_args) == 'test_path.dem'

        # Verify parse was called
        mock_demo_instance.parse.assert_called_once()

        # Verify result is the demo instance
        assert result == mock_demo_instance


def test_awpy_demo_parser_with_string_path():
    """Test that AwpyDemoParser handles string paths correctly."""
    parser = AwpyDemoParser()

    with patch('src.cs2_analyzer.application.ingestion.Demo') as MockDemo:
        mock_demo_instance = Mock()
        MockDemo.return_value = mock_demo_instance

        # Parse with string path
        parser.parse('/path/to/demo.dem')

        # Verify Path conversion
        call_args = MockDemo.call_args[0][0]
        assert isinstance(call_args, Path)
