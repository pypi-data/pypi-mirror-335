"""Tests for CLI functionality."""
import pytest
from click.testing import CliRunner
from src.cli import main

@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()

def test_create_repo_command(runner, test_repo_name):
    """Test the create repository command."""
    result = runner.invoke(main, [
        'create',
        '--repo', test_repo_name,
        '--description', 'Test repository'
    ])
    assert result.exit_code == 0
    assert f"Repository created: {test_repo_name}" in result.output

def test_list_issues_command(runner, test_repo):
    """Test the list issues command."""
    # Create a test issue
    test_repo.create_issue(
        title="Test Issue",
        body="Test issue body"
    )

    result = runner.invoke(main, [
        'issues',
        '--repo', test_repo.name
    ])
    assert result.exit_code == 0
    assert "Test Issue" in result.output

def test_invalid_command(runner):
    """Test invalid command handling."""
    result = runner.invoke(main, ['invalid-command'])
    assert result.exit_code != 0

def test_missing_required_args(runner):
    """Test handling of missing required arguments."""
    result = runner.invoke(main, ['create'])
    assert result.exit_code != 0
    assert "Error" in result.output
