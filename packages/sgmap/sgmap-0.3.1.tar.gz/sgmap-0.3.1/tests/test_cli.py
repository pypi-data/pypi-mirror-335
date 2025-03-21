"""
Tests for sgmap.cli module
"""

from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from sgmap.cli import main


class TestCli:
    """Tests for CLI interface"""

    @pytest.fixture
    def cli_runner(self):
        """Fixture for CLI runner"""
        return CliRunner()

    @patch('sgmap.cli.get_security_groups')
    @patch('sgmap.cli.analyze_security_group_connections')
    @patch('sgmap.cli.generate_mermaid_diagram')
    def test_main_with_mermaid_output(
        self, mock_generate_mermaid, mock_analyze, mock_get_sg, cli_runner, sample_vpc_and_sgs
    ):
        """Test main function with mermaid output"""
        # Setup mocks
        mock_get_sg.return_value = sample_vpc_and_sgs
        mock_analyze.return_value = {'vpc': {}, 'security_groups': {}}
        mock_generate_mermaid.return_value = "```mermaid\nflowchart LR\n```"

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678'])

        # Verify the result
        assert result.exit_code == 0
        assert "```mermaid" in result.output
        assert "flowchart LR" in result.output

        # Verify the function calls
        mock_get_sg.assert_called_once_with('vpc-12345678', None)
        mock_analyze.assert_called_once_with(sample_vpc_and_sgs)
        mock_generate_mermaid.assert_called_once_with({'vpc': {}, 'security_groups': {}}, False)

    @patch('sgmap.cli.get_security_groups')
    @patch('sgmap.cli.analyze_security_group_connections')
    @patch('sgmap.cli.generate_json_output')
    def test_main_with_json_output(
        self, mock_generate_json, mock_analyze, mock_get_sg, cli_runner, sample_vpc_and_sgs
    ):
        """Test main function with JSON output"""
        # Setup mocks
        mock_get_sg.return_value = sample_vpc_and_sgs
        mock_analyze.return_value = {'vpc': {}, 'security_groups': {}}
        mock_generate_json.return_value = '{"vpc": {}, "security_groups": {}}'

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678', '--json'])

        # Verify the result
        assert result.exit_code == 0
        assert '{"vpc": {}, "security_groups": {}}' in result.output

        # Verify the function calls
        mock_get_sg.assert_called_once_with('vpc-12345678', None)
        mock_analyze.assert_called_once_with(sample_vpc_and_sgs)
        mock_generate_json.assert_called_once_with({'vpc': {}, 'security_groups': {}})

    @patch('sgmap.cli.get_security_groups')
    @patch('sgmap.cli.analyze_security_group_connections')
    @patch('sgmap.cli.generate_mermaid_diagram')
    def test_main_with_security_group_filter(
        self, mock_generate_mermaid, mock_analyze, mock_get_sg, cli_runner, sample_vpc_and_sgs
    ):
        """Test main function with security group filter"""
        # Setup mocks
        mock_get_sg.return_value = sample_vpc_and_sgs
        mock_analyze.return_value = {'vpc': {}, 'security_groups': {}}
        mock_generate_mermaid.return_value = "```mermaid\nflowchart LR\n```"

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678', '--security-group-id', 'sg-11111111'])

        # Verify the result
        assert result.exit_code == 0

        # Verify the function calls
        mock_get_sg.assert_called_once_with('vpc-12345678', 'sg-11111111')

    @patch('sgmap.cli.get_security_groups')
    @patch('sgmap.cli.analyze_security_group_connections')
    @patch('sgmap.cli.generate_mermaid_diagram')
    def test_main_with_with_vpc_option(
        self, mock_generate_mermaid, mock_analyze, mock_get_sg, cli_runner, sample_vpc_and_sgs
    ):
        """Test main function with with-vpc option"""
        # Setup mocks
        mock_get_sg.return_value = sample_vpc_and_sgs
        mock_analyze.return_value = {'vpc': {}, 'security_groups': {}}
        mock_generate_mermaid.return_value = "```mermaid\nflowchart LR\n```"

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678', '--with-vpc'])

        # Verify the result
        assert result.exit_code == 0

        # Verify the function calls
        mock_generate_mermaid.assert_called_once_with({'vpc': {}, 'security_groups': {}}, True)

    @patch('sgmap.cli.get_security_groups')
    def test_main_vpc_not_found(self, mock_get_sg, cli_runner):
        """Test main function when VPC is not found"""
        # Setup mocks
        mock_get_sg.return_value = {'vpc': None, 'security_groups': []}

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-nonexistent'])

        # Verify the result
        assert result.exit_code == 1
        assert "VPC not found: vpc-nonexistent" in result.output

    @patch('sgmap.cli.get_security_groups')
    def test_main_no_security_groups_found(self, mock_get_sg, cli_runner):
        """Test main function when no security groups are found"""
        # Setup mocks
        mock_get_sg.return_value = {'vpc': {'VpcId': 'vpc-12345678'}, 'security_groups': []}

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678'])

        # Verify the result
        assert result.exit_code == 1
        assert "No security groups found for VPC ID: vpc-12345678" in result.output

    @patch('sgmap.cli.get_security_groups')
    def test_main_exception_handling(self, mock_get_sg, cli_runner):
        """Test main function exception handling"""
        # Setup mocks
        mock_get_sg.side_effect = Exception("Test error")

        # Run the CLI command
        result = cli_runner.invoke(main, ['--vpc-id', 'vpc-12345678'])

        # Verify the result
        assert result.exit_code == 1
        assert "Error: Test error" in result.output