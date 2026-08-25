"""Workflow state management for DADT production pipeline.

Tracks the state of story production workflows, including status, retries,
failures, and timing information. Provides persistence and recovery mechanisms.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowStatus(str, Enum):
    """Status of a workflow or workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class StoryStage(str, Enum):
    """Stages in the story production pipeline."""
    DISCOVERY = "discovery"
    RESEARCH = "research"
    OUTLINE = "outline"
    DRAFT = "draft"
    DRAFT_VERIFICATION = "draft_verification"
    DERIVATIVE_CONTENT = "derivative_content"
    PACKAGE_VERIFICATION = "package_verification"
    PUBLISHING = "publishing"
    ARCHIVAL = "archival"


@dataclass
class StepState:
    """State of a single workflow step."""
    name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: float | None = None
    completed_at: float | None = None
    attempt: int = 0
    max_attempts: int = 3
    error: str | None = None
    output_path: str | None = None
    
    def start(self) -> None:
        """Mark step as started."""
        self.status = WorkflowStatus.RUNNING
        self.started_at = time.time()
        self.completed_at = None
        self.output_path = None
        self.error = None
        self.attempt += 1
    
    def succeed(self, output_path: str | None = None) -> None:
        """Mark step as successful."""
        self.status = WorkflowStatus.SUCCESS
        self.completed_at = time.time()
        self.output_path = output_path
        self.error = None
    
    def fail(self, error: str) -> None:
        """Mark step as failed."""
        self.status = WorkflowStatus.FAILED
        self.completed_at = time.time()
        self.error = error
    
    def can_retry(self) -> bool:
        """Check if step can be retried."""
        return self.attempt < self.max_attempts and self.status == WorkflowStatus.FAILED
    
    def retry(self) -> None:
        """Mark step for retry."""
        self.status = WorkflowStatus.RETRYING
        self.error = None
    
    @property
    def duration(self) -> float | None:
        """Get step duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


@dataclass
class StoryWorkflow:
    """State of a complete story production workflow."""
    story_slug: str
    run_id: str
    run_date: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    steps: dict[str, StepState] = field(default_factory=dict)
    draft_decision: str | None = None
    package_decision: str | None = None
    archive_eligible: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def get_step(self, stage: StoryStage | str) -> StepState:
        """Get or create a step for the given stage."""
        stage_name = stage.value if isinstance(stage, StoryStage) else stage
        if stage_name not in self.steps:
            self.steps[stage_name] = StepState(name=stage_name)
        return self.steps[stage_name]
    
    def start(self) -> None:
        """Mark workflow as started."""
        self.status = WorkflowStatus.RUNNING
        self.started_at = time.time()
    
    def succeed(self) -> None:
        """Mark workflow as successful."""
        self.status = WorkflowStatus.SUCCESS
        self.completed_at = time.time()
    
    def fail(self) -> None:
        """Mark workflow as failed."""
        self.status = WorkflowStatus.FAILED
        self.completed_at = time.time()
    
    def cancel(self) -> None:
        """Mark workflow as cancelled."""
        self.status = WorkflowStatus.CANCELLED
        self.completed_at = time.time()
    
    @property
    def duration(self) -> float | None:
        """Get workflow duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if workflow is in a terminal state."""
        return self.status in {
            WorkflowStatus.SUCCESS,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
            WorkflowStatus.SKIPPED,
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        for step_name, step_data in data["steps"].items():
            step_data["status"] = self.steps[step_name].status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> StoryWorkflow:
        """Create from dictionary."""
        data = data.copy()
        steps_data = data.pop("steps", {})
        workflow = cls(**{k: v for k, v in data.items() if k != "status"})
        workflow.status = WorkflowStatus(data["status"])

        for step_name, step_data in steps_data.items():
            step_data = step_data.copy()
            step_status = WorkflowStatus(step_data.pop("status"))
            step = StepState(**step_data)
            step.status = step_status
            workflow.steps[step_name] = step

        return workflow


@dataclass
class WorkflowRegistry:
    """Registry for managing multiple story workflows."""
    workflows: dict[str, StoryWorkflow] = field(default_factory=dict)
    state_dir: Path = field(default_factory=lambda: Path(".workflow-state"))
    
    def __post_init__(self):
        """Ensure state directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def add_workflow(self, workflow: StoryWorkflow) -> None:
        """Add a workflow to the registry."""
        self.workflows[workflow.story_slug] = workflow
        self.save_workflow(workflow)
    
    def get_workflow(self, story_slug: str) -> StoryWorkflow | None:
        """Get a workflow by story slug."""
        if story_slug in self.workflows:
            return self.workflows[story_slug]
        return self.load_workflow(story_slug)
    
    def save_workflow(self, workflow: StoryWorkflow) -> Path:
        """Save workflow state to disk."""
        file_path = self.state_dir / f"{workflow.story_slug}.json"
        temp_path = file_path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as temp_file:
            temp_file.write(json.dumps(workflow.to_dict(), indent=2) + "\n")
            temp_file.flush()
        temp_path.replace(file_path)
        return file_path
    
    def load_workflow(self, story_slug: str) -> StoryWorkflow | None:
        """Load workflow state from disk."""
        file_path = self.state_dir / f"{story_slug}.json"
        if not file_path.exists():
            return None
        
        data = json.loads(file_path.read_text(encoding="utf-8"))
        workflow = StoryWorkflow.from_dict(data)
        self.workflows[story_slug] = workflow
        return workflow
    
    def list_workflows(
        self,
        status: WorkflowStatus | None = None,
        limit: int | None = None,
    ) -> list[StoryWorkflow]:
        """List workflows, optionally filtered by status."""
        all_workflows = []
        
        for file_path in sorted(self.state_dir.glob("*.json"), reverse=True):
            if file_path.stem not in self.workflows:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                workflow = StoryWorkflow.from_dict(data)
                self.workflows[workflow.story_slug] = workflow
            else:
                workflow = self.workflows[file_path.stem]
            
            if status is None or workflow.status == status:
                all_workflows.append(workflow)
        
        if limit is not None:
            return all_workflows[:limit]
        return all_workflows
    
    def get_running_workflows(self) -> list[StoryWorkflow]:
        """Get all currently running workflows."""
        return self.list_workflows(status=WorkflowStatus.RUNNING)
    
    def get_failed_workflows(self) -> list[StoryWorkflow]:
        """Get all failed workflows."""
        return self.list_workflows(status=WorkflowStatus.FAILED)
    
    def cleanup_old_workflows(self, days: int = 30) -> int:
        """Remove workflow state files older than specified days."""
        cutoff = time.time() - (days * 86400)
        removed = 0
        
        for file_path in self.state_dir.glob("*.json"):
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if data.get("created_at", 0) < cutoff:
                file_path.unlink()
                removed += 1
                if file_path.stem in self.workflows:
                    del self.workflows[file_path.stem]
        
        return removed
