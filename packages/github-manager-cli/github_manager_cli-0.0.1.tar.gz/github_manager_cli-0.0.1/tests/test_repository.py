"""Tests for repository management functionality."""
import pytest
from github import GithubException
from src.repository import (
    create_repository,
    delete_repository,
    get_repo,
    get_labels,
    get_pull_requests
)

def test_create_repository(github_org, test_repo_name):
    """Test repository creation."""
    description = "Test repository description"

    # Test creation
    create_repository(test_repo_name, description)

    # Verify repository exists
    repo = github_org.get_repo(test_repo_name)
    assert repo.name == test_repo_name
    assert repo.description == description
    assert repo.private is True

    # Cleanup
    repo.delete()

def test_delete_repository(test_repo):
    """Test repository deletion."""
    repo_name = test_repo.name

    # Test deletion
    delete_repository(repo_name)

    # Verify repository no longer exists
    with pytest.raises(GithubException) as exc:
        github_org.get_repo(repo_name)
    assert exc.value.status == 404

def test_get_repo_existing(test_repo):
    """Test getting an existing repository."""
    repo = get_repo(test_repo.name)
    assert repo is not None
    assert repo.name == test_repo.name

def test_get_repo_nonexistent():
    """Test getting a non-existent repository."""
    repo = get_repo("nonexistent-repo-" + os.urandom(4).hex())
    assert repo is None

def test_get_labels(test_repo):
    """Test getting repository labels."""
    # Create some test labels
    test_repo.create_label("bug", "ff0000", "Bug label")
    test_repo.create_label("enhancement", "00ff00", "Enhancement label")

    # Get labels
    labels = get_labels(test_repo.name)

    # Verify labels
    label_names = [label.name for label in labels]
    assert "bug" in label_names
    assert "enhancement" in label_names

def test_get_pull_requests(test_repo):
    """Test getting pull requests."""
    # Create a test branch and PR
    main_branch = test_repo.get_branch("main")
    test_repo.create_git_ref(
        ref=f"refs/heads/test-branch",
        sha=main_branch.commit.sha
    )

    test_repo.create_pull(
        title="Test PR",
        body="Test PR body",
        head="test-branch",
        base="main"
    )

    # Get PRs
    prs = get_pull_requests(test_repo.name)

    # Verify PR exists
    assert len(prs) > 0
