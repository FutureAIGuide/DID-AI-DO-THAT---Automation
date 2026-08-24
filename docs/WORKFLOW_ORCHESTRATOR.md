# Workflow Orchestrator

The DADT Workflow Orchestrator provides enhanced automation for story production with intelligent retry logic, parallel execution, state tracking, and failure recovery.

## Features

### Core Capabilities

- **State Management**: Persistent tracking of all workflow states
- **Retry Logic**: Automatic retry of failed steps with exponential backoff
- **Parallel Execution**: Concurrent production of multiple stories
- **Failure Recovery**: Resume failed workflows from the last successful step
- **Status Monitoring**: Real-time visibility into pipeline health
- **CLI Interface**: Command-line tools for manual workflow management

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Workflow Orchestrator                │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐        ┌─────────────────┐       │
│  │   Registry   │◄──────►│  State Manager  │       │
│  └──────┬───────┘        └─────────────────┘       │
│         │                                            │
│         │                                            │
│  ┌──────▼───────────────────────────────┐          │
│  │       Step Executor (Retry Logic)    │          │
│  └──────────────┬───────────────────────┘          │
│                 │                                    │
│     ┌───────────┼───────────┐                      │
│     ▼           ▼           ▼                      │
│  Research   Draft      Publishing                   │
│  ┌─────┐   ┌─────┐    ┌──────────┐                │
│  └─────┘   └─────┘    └──────────┘                │
└─────────────────────────────────────────────────────┘
```

## Installation

No additional dependencies required beyond the base DADT repository.

Ensure Python 3.11+ is installed:

```bash
python --version
```

## CLI Usage

### Check Status

View overall workflow status:

```bash
python scripts/workflow_cli.py status
```

Output as JSON:

```bash
python scripts/workflow_cli.py status --json
```

### List Workflows

List all workflows:

```bash
python scripts/workflow_cli.py list
```

Filter by status:

```bash
python scripts/workflow_cli.py list --status failed
python scripts/workflow_cli.py list --status running
```

Limit results:

```bash
python scripts/workflow_cli.py list --limit 10
```

### Show Workflow Details

View detailed information about a specific workflow:

```bash
python scripts/workflow_cli.py show anthropic-frontier-model-shutdown
```

Output as JSON:

```bash
python scripts/workflow_cli.py show anthropic-frontier-model-shutdown --json
```

### Produce Single Story

Run production for one story:

```bash
export OPENROUTER_API_KEY="your-api-key"
python scripts/workflow_cli.py produce my-story-slug
```

With custom options:

```bash
python scripts/workflow_cli.py produce my-story-slug \
  --model "anthropic/claude-3.5-sonnet" \
  --max-retries 5 \
  --log-level DEBUG
```

### Produce Multiple Stories in Parallel

Run production for multiple stories concurrently:

```bash
export OPENROUTER_API_KEY="your-api-key"
python scripts/workflow_cli.py produce-batch "story-one,story-two,story-three" \
  --max-parallel 3
```

With custom configuration:

```bash
python scripts/workflow_cli.py produce-batch "story-one,story-two" \
  --max-parallel 2 \
  --max-retries 5 \
  --model "anthropic/claude-3.5-sonnet" \
  --log-level INFO
```

### Retry Failed Workflows

Automatically retry all failed workflows:

```bash
python scripts/workflow_cli.py retry
```

### Clean Up Old State

Remove workflow state files older than 30 days:

```bash
python scripts/workflow_cli.py cleanup --days 30
```

## GitHub Actions Integration

### Orchestrated Production Workflow

Trigger parallel story production via GitHub Actions:

1. Go to **Actions** → **Orchestrated story production**
2. Click **Run workflow**
3. Enter comma-separated story slugs: `story-one,story-two,story-three`
4. Set max parallel executions (default: 3)
5. Set max retries per step (default: 3)
6. Optionally specify a model override
7. Click **Run workflow**

The workflow will:
- Produce all stories in parallel (respecting the concurrency limit)
- Track state for each story individually
- Retry failed steps automatically
- Generate a comprehensive summary
- Commit all generated assets
- Upload workflow state as an artifact

### Workflow Monitor

The monitor workflow runs hourly to check pipeline health:

- Tracks total workflows, running count, and failure count
- Alerts if failure rate is too high
- Provides retry recommendations
- Exits with error if critical thresholds exceeded

View monitoring results in **Actions** → **Workflow monitor**

## State Management

### State Directory

Workflow state is stored in `.workflow-state/` (gitignored by default).

Each story has a JSON state file: `.workflow-state/[story-slug].json`

### State Schema

```json
{
  "story_slug": "example-story",
  "run_id": "run-123",
  "run_date": "2026-08-24",
  "status": "running",
  "created_at": 1724533200.0,
  "started_at": 1724533210.0,
  "completed_at": null,
  "draft_decision": null,
  "package_decision": null,
  "archive_eligible": false,
  "steps": {
    "research": {
      "name": "research",
      "status": "success",
      "started_at": 1724533210.0,
      "completed_at": 1724533250.0,
      "attempt": 1,
      "max_attempts": 3,
      "error": null,
      "output_path": "case-files/active/example-story-research-packet.md"
    },
    "draft": {
      "name": "draft",
      "status": "running",
      "started_at": 1724533260.0,
      "completed_at": null,
      "attempt": 1,
      "max_attempts": 3,
      "error": null,
      "output_path": null
    }
  },
  "metadata": {}
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key (required) | - |
| `OPENROUTER_MODEL` | Default model | `anthropic/claude-3.5-sonnet` |
| `OPENROUTER_MAX_TOKENS` | Max tokens per request | `8000` |
| `OPENROUTER_DRAFT_MAX_TOKENS` | Max tokens for draft generation | `16000` |
| `OPENROUTER_SITE_URL` | Referer URL for OpenRouter | - |
| `OPENROUTER_SITE_NAME` | Site name for OpenRouter | `DID AI DO THAT?!` |

### Orchestrator Configuration

Create custom configuration in Python:

```python
from workflow_orchestrator import OrchestratorConfig, WorkflowOrchestrator

config = OrchestratorConfig(
    root_dir=Path("/path/to/repo"),
    state_dir=Path(".workflow-state"),
    max_parallel_stories=5,
    max_retries_per_step=3,
    retry_delay_seconds=60,
    enable_parallel_execution=True,
    log_level="INFO",
)

orchestrator = WorkflowOrchestrator(config)
```

## Retry Logic

### Step-Level Retries

Each workflow step can retry up to `max_attempts` (default: 3) times:

1. Step fails
2. If `attempt < max_attempts`, wait `retry_delay_seconds` (default: 60s)
3. Retry step
4. Repeat until success or max attempts exceeded

### Workflow-Level Recovery

Failed workflows can be resumed:

```bash
# Mark all failed workflows for retry
python scripts/workflow_cli.py retry
```

## Parallel Execution

### Concurrency Control

The orchestrator limits parallel story production to prevent:
- OpenRouter rate limits
- Resource exhaustion
- Git merge conflicts

Configure with `--max-parallel`:

```bash
python scripts/workflow_cli.py produce-batch "s1,s2,s3,s4,s5" --max-parallel 3
```

This runs 3 stories at once, queuing the rest.

### Thread Pool Executor

Parallel execution uses Python's `concurrent.futures.ThreadPoolExecutor`:

```python
workflows = orchestrator.produce_stories_parallel(
    story_slugs=["story-one", "story-two", "story-three"],
    run_date="2026-08-24",
    run_id="batch-001",
    client=openrouter_client,
    repo_context=context,
)
```

## Monitoring

### Status Dashboard (CLI)

```bash
python scripts/workflow_cli.py status
```

Example output:

```
============================================================
WORKFLOW STATUS SUMMARY
============================================================

Total workflows: 15

By status:
  pending        :   2
  running        :   3
  success        :   8
  failed         :   2

Currently running (3):
  - story-alpha (245s)
  - story-beta (180s)
  - story-gamma (90s)

Failed workflows (2):
  - story-delta
    Error: OpenRouterError: Request failed during draft verification
  - story-epsilon

Recent completions:
  - story-zeta                   success      420s [draft:PUBLISH, pkg:PUBLISH]
  - story-theta                  success      385s [draft:PUBLISH, pkg:PUBLISH]
```

### GitHub Actions Summary

Each orchestrated workflow generates a summary:

- Total workflows processed
- Status breakdown
- Currently running workflows
- Failed workflows with error details
- Recent completions with verification decisions

## Error Handling

### Error Categories

1. **Transient Errors**: Automatically retried
   - Network timeouts
   - OpenRouter 429/5xx errors
   - Temporary file locks

2. **Validation Errors**: Workflow stopped
   - Draft gate: HOLD or REJECT
   - Package gate: HOLD or REJECT
   - Invalid slug format

3. **Fatal Errors**: Workflow failed
   - Max retries exceeded
   - Missing required files
   - Invalid API key

### Error Recovery

View failed workflows:

```bash
python scripts/workflow_cli.py list --status failed
```

Inspect error details:

```bash
python scripts/workflow_cli.py show failed-story-slug
```

Retry after fixing issues:

```bash
python scripts/workflow_cli.py retry
```

## Best Practices

### Local Development

1. Test single story production first:
   ```bash
   python scripts/workflow_cli.py produce test-story
   ```

2. Verify state tracking works:
   ```bash
   python scripts/workflow_cli.py status
   python scripts/workflow_cli.py show test-story
   ```

3. Test parallel execution with 2-3 stories:
   ```bash
   python scripts/workflow_cli.py produce-batch "story-1,story-2" --max-parallel 2
   ```

### Production Use

1. **Use GitHub Actions for scheduled runs**: Avoid manual CLI invocations for production workloads

2. **Monitor failure rates**: Set up alerts when failed workflows exceed threshold

3. **Clean up old state regularly**:
   ```bash
   python scripts/workflow_cli.py cleanup --days 30
   ```

4. **Archive workflow states for successful runs**: Upload state artifacts in GitHub Actions

5. **Set reasonable concurrency limits**: Start with `max_parallel=3` and adjust based on:
   - OpenRouter rate limits
   - Runner resource capacity
   - Git merge conflict frequency

### Cost Management

1. **Use smaller models for testing**:
   ```bash
   python scripts/workflow_cli.py produce test --model "anthropic/claude-3-haiku"
   ```

2. **Set token limits**:
   ```bash
   export OPENROUTER_MAX_TOKENS=4000
   export OPENROUTER_DRAFT_MAX_TOKENS=8000
   ```

3. **Monitor spend** via OpenRouter dashboard

4. **Limit parallel executions** to control burst costs

## Troubleshooting

### State File Corruption

If state files become corrupted:

```bash
rm .workflow-state/problematic-slug.json
python scripts/workflow_cli.py produce problematic-slug
```

### Stuck Workflows

If a workflow appears stuck in "running" state:

1. Check if the process is actually running
2. If not, manually update state:
   ```bash
   # Edit .workflow-state/stuck-slug.json
   # Change "status": "running" to "status": "failed"
   ```
3. Retry the workflow:
   ```bash
   python scripts/workflow_cli.py retry
   ```

### Permission Errors

Ensure the workflow state directory is writable:

```bash
chmod -R u+w .workflow-state/
```

### OpenRouter Errors

Check API key:

```bash
echo $OPENROUTER_API_KEY
```

Verify model availability:

```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

## API Reference

### WorkflowOrchestrator

```python
class WorkflowOrchestrator:
    def __init__(self, config: OrchestratorConfig | None = None)
    def create_workflow(self, story_slug: str, run_date: str, run_id: str) -> StoryWorkflow
    def produce_story(...) -> StoryWorkflow
    def produce_stories_parallel(...) -> list[StoryWorkflow]
    def retry_failed_workflows() -> list[StoryWorkflow]
    def get_status_summary() -> dict[str, Any]
```

### WorkflowRegistry

```python
class WorkflowRegistry:
    def add_workflow(self, workflow: StoryWorkflow) -> None
    def get_workflow(self, story_slug: str) -> StoryWorkflow | None
    def save_workflow(self, workflow: StoryWorkflow) -> Path
    def load_workflow(self, story_slug: str) -> StoryWorkflow | None
    def list_workflows(status: WorkflowStatus | None = None, limit: int | None = None) -> list[StoryWorkflow]
    def get_running_workflows() -> list[StoryWorkflow]
    def get_failed_workflows() -> list[StoryWorkflow]
    def cleanup_old_workflows(days: int = 30) -> int
```

### StoryWorkflow

```python
class StoryWorkflow:
    story_slug: str
    run_id: str
    run_date: str
    status: WorkflowStatus
    steps: dict[str, StepState]
    draft_decision: str | None
    package_decision: str | None
    archive_eligible: bool
    metadata: dict[str, Any]
    
    def start() -> None
    def succeed() -> None
    def fail() -> None
    def cancel() -> None
    def get_step(stage: StoryStage | str) -> StepState
    
    @property
    def duration() -> float | None
    
    @property
    def is_complete() -> bool
```

## Roadmap

Future enhancements planned:

- [ ] Web dashboard for visual monitoring
- [ ] Slack/Discord notifications for workflow events
- [ ] Advanced analytics and cost tracking
- [ ] Workflow templates and presets
- [ ] Dependency management between stories
- [ ] Priority queue for story production
- [ ] Integration with project management tools
- [ ] Automated rollback on verification failures
- [ ] Performance profiling per workflow stage

## Contributing

When contributing to the orchestrator:

1. Add tests for new features in `scripts/tests/`
2. Update this documentation
3. Follow existing code style
4. Test with actual story production runs

## Support

For issues or questions:

1. Check this documentation first
2. Review workflow state files in `.workflow-state/`
3. Check GitHub Actions logs
4. Review OpenRouter dashboard for API issues
