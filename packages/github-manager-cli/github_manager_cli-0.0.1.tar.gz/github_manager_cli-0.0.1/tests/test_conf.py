"""Pytest configuration and shared fixtures."""
import os
import pytest
from dotenv import load_dotenv
from github import Github, Auth

@pytest.fixture(scope="session")
def github_client():
    """Create a GitHub client for testing."""
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(str(github_token))
    return Github(auth=auth)

@pytest.fixture(scope="session")
def github_org(github_client):
    """Get GitHub organization for testing."""
    org_name = os.getenv("GITHUB_ORG")
    return github_client.get_organization(org_name)

@pytest.fixture
def test_repo_name():
    """Generate a unique test repository name."""
    return "test-repo-" + os.urandom(4).hex()

@pytest.fixture
def test_repo(github_org, test_repo_name):
    """Create and return a test repository, then clean it up after test."""
    repo = github_org.create_repo(
        name=test_repo_name,
        private=True,
        description="Test repository"
    )
    yield repo
    try:
        repo.delete()
    except Exception as e:
        print(f"Failed to delete test repository: {e}")
