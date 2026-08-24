"""Tests for workflow state management."""

import json
import tempfile
import time
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_state import (
    StepState,
    StoryStage,
    StoryWorkflow,
    WorkflowRegistry,
    WorkflowStatus,
)


def test_step_state_lifecycle():
    """Test step state transitions."""
    step = StepState(name="test-step", max_attempts=3)
    
    assert step.status == WorkflowStatus.PENDING
    assert step.attempt == 0
    
    # Start step
    step.start()
    assert step.status == WorkflowStatus.RUNNING
    assert step.attempt == 1
    assert step.started_at is not None
    
    # Succeed
    step.succeed(output_path="/path/to/output.md")
    assert step.status == WorkflowStatus.SUCCESS
    assert step.output_path == "/path/to/output.md"
    assert step.completed_at is not None
    assert step.duration is not None


def test_step_state_retry():
    """Test step retry logic."""
    step = StepState(name="test-step", max_attempts=3)
    
    # First attempt fails
    step.start()
    step.fail("Error message")
    assert step.status == WorkflowStatus.FAILED
    assert step.error == "Error message"
    assert step.can_retry() is True
    
    # Retry
    step.retry()
    assert step.status == WorkflowStatus.RETRYING
    assert step.error is None
    
    # Second attempt
    step.start()
    assert step.attempt == 2
    step.fail("Another error")
    assert step.can_retry() is True
    
    # Third attempt
    step.retry()
    step.start()
    assert step.attempt == 3
    step.fail("Final error")
    assert step.can_retry() is False


def test_workflow_lifecycle():
    """Test workflow state transitions."""
    workflow = StoryWorkflow(
        story_slug="test-story",
        run_id="run-123",
        run_date="2026-08-24",
    )
    
    assert workflow.status == WorkflowStatus.PENDING
    assert workflow.is_complete is False
    
    workflow.start()
    assert workflow.status == WorkflowStatus.RUNNING
    assert workflow.started_at is not None
    
    workflow.succeed()
    assert workflow.status == WorkflowStatus.SUCCESS
    assert workflow.completed_at is not None
    assert workflow.is_complete is True


def test_workflow_steps():
    """Test workflow step management."""
    workflow = StoryWorkflow(
        story_slug="test-story",
        run_id="run-123",
        run_date="2026-08-24",
    )
    
    # Get or create step
    step = workflow.get_step(StoryStage.RESEARCH)
    assert step.name == "research"
    assert step.status == WorkflowStatus.PENDING
    
    # Same step returned on subsequent calls
    step2 = workflow.get_step(StoryStage.RESEARCH)
    assert step is step2
    
    # Multiple steps
    draft_step = workflow.get_step(StoryStage.DRAFT)
    assert draft_step.name == "draft"
    assert len(workflow.steps) == 2


def test_workflow_serialization():
    """Test workflow to/from dict conversion."""
    workflow = StoryWorkflow(
        story_slug="test-story",
        run_id="run-123",
        run_date="2026-08-24",
    )
    workflow.start()
    
    step = workflow.get_step(StoryStage.RESEARCH)
    step.start()
    step.succeed(output_path="output.md")
    
    workflow.draft_decision = "PUBLISH"
    workflow.metadata["test_key"] = "test_value"
    
    # Convert to dict
    data = workflow.to_dict()
    assert data["story_slug"] == "test-story"
    assert data["status"] == "running"
    assert "research" in data["steps"]
    assert data["draft_decision"] == "PUBLISH"
    assert data["metadata"]["test_key"] == "test_value"
    
    # Convert back from dict
    workflow2 = StoryWorkflow.from_dict(data)
    assert workflow2.story_slug == workflow.story_slug
    assert workflow2.status == workflow.status
    assert workflow2.draft_decision == workflow.draft_decision
    assert "research" in workflow2.steps
    assert workflow2.steps["research"].status == WorkflowStatus.SUCCESS


def test_registry_workflow_management():
    """Test workflow registry operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = WorkflowRegistry(state_dir=Path(tmpdir))
        
        # Add workflow
        workflow = StoryWorkflow(
            story_slug="test-story",
            run_id="run-123",
            run_date="2026-08-24",
        )
        registry.add_workflow(workflow)
        
        # Get workflow
        retrieved = registry.get_workflow("test-story")
        assert retrieved is not None
        assert retrieved.story_slug == "test-story"
        
        # Verify file was created
        state_file = Path(tmpdir) / "test-story.json"
        assert state_file.exists()
        
        # Load workflow from disk
        registry2 = WorkflowRegistry(state_dir=Path(tmpdir))
        loaded = registry2.get_workflow("test-story")
        assert loaded is not None
        assert loaded.story_slug == "test-story"


def test_registry_list_workflows():
    """Test listing workflows with filters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = WorkflowRegistry(state_dir=Path(tmpdir))
        
        # Add multiple workflows with different statuses
        workflow1 = StoryWorkflow("story-1", "run-1", "2026-08-24")
        workflow1.start()
        registry.add_workflow(workflow1)
        
        workflow2 = StoryWorkflow("story-2", "run-2", "2026-08-24")
        workflow2.start()
        workflow2.succeed()
        registry.add_workflow(workflow2)
        
        workflow3 = StoryWorkflow("story-3", "run-3", "2026-08-24")
        workflow3.start()
        workflow3.fail()
        registry.add_workflow(workflow3)
        
        # List all
        all_workflows = registry.list_workflows()
        assert len(all_workflows) == 3
        
        # Filter by status
        running = registry.list_workflows(status=WorkflowStatus.RUNNING)
        assert len(running) == 1
        assert running[0].story_slug == "story-1"
        
        success = registry.list_workflows(status=WorkflowStatus.SUCCESS)
        assert len(success) == 1
        assert success[0].story_slug == "story-2"
        
        failed = registry.list_workflows(status=WorkflowStatus.FAILED)
        assert len(failed) == 1
        assert failed[0].story_slug == "story-3"
        
        # Limit
        limited = registry.list_workflows(limit=2)
        assert len(limited) == 2


def test_registry_cleanup():
    """Test cleanup of old workflow states."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = WorkflowRegistry(state_dir=Path(tmpdir))
        
        # Add old workflow
        old_workflow = StoryWorkflow("old-story", "run-1", "2026-07-01")
        old_workflow.created_at = time.time() - (40 * 86400)  # 40 days ago
        registry.add_workflow(old_workflow)
        
        # Add recent workflow
        new_workflow = StoryWorkflow("new-story", "run-2", "2026-08-24")
        registry.add_workflow(new_workflow)
        
        # Cleanup workflows older than 30 days
        removed = registry.cleanup_old_workflows(days=30)
        assert removed == 1
        
        # Verify only new workflow remains
        workflows = registry.list_workflows()
        assert len(workflows) == 1
        assert workflows[0].story_slug == "new-story"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
