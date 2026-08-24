# Workflow Orchestrator Architecture

Technical architecture documentation for the DADT Workflow Orchestrator.

## System Overview

The Workflow Orchestrator is a stateful, retry-capable automation system for managing story production workflows. It provides a higher-level abstraction over the existing GitHub Actions workflows with enhanced reliability, observability, and control.

## Components

### 1. State Management Layer (`workflow_state.py`)

Handles persistence and tracking of workflow states.

#### Key Classes

**`WorkflowStatus`** (Enum)
- Defines workflow/step status: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `RETRYING`, `CANCELLED`, `SKIPPED`

**`StoryStage`** (Enum)
- Pipeline stages: `DISCOVERY`, `RESEARCH`, `OUTLINE`, `DRAFT`, `DRAFT_VERIFICATION`, `DERIVATIVE_CONTENT`, `PACKAGE_VERIFICATION`, `PUBLISHING`, `ARCHIVAL`

**`StepState`** (Dataclass)
- Tracks individual step execution
- Fields: name, status, started_at, completed_at, attempt, max_attempts, error, output_path
- Methods: `start()`, `succeed()`, `fail()`, `can_retry()`, `retry()`
- Computed: `duration`

**`StoryWorkflow`** (Dataclass)
- Tracks complete story production workflow
- Fields: story_slug, run_id, run_date, status, steps (dict), draft_decision, package_decision, archive_eligible, metadata
- Methods: `start()`, `succeed()`, `fail()`, `cancel()`, `get_step()`, `to_dict()`, `from_dict()`
- Computed: `duration`, `is_complete`

**`WorkflowRegistry`** (Dataclass)
- Registry for managing multiple workflows
- Fields: workflows (dict), state_dir (Path)
- Methods: `add_workflow()`, `get_workflow()`, `save_workflow()`, `load_workflow()`, `list_workflows()`, `cleanup_old_workflows()`
- Helpers: `get_running_workflows()`, `get_failed_workflows()`

#### State Persistence

States are persisted as JSON files in `.workflow-state/`:

```
.workflow-state/
├── story-slug-1.json
├── story-slug-2.json
└── story-slug-3.json
```

Each file contains the complete workflow state including all steps, timing, decisions, and metadata.

### 2. Orchestration Layer (`workflow_orchestrator.py`)

Coordinates workflow execution with retry logic and parallel processing.

#### Key Classes

**`OrchestratorConfig`** (Dataclass)
- Configuration for orchestrator behavior
- Fields: root_dir, state_dir, max_parallel_stories, max_retries_per_step, retry_delay_seconds, enable_parallel_execution, log_level

**`StepExecutor`** (Dataclass)
- Executes individual steps with retry logic
- Methods: `execute_step(workflow, stage, executor_fn) -> bool`
- Handles: retry on failure, backoff delays, state updates

**`WorkflowOrchestrator`** (Class)
- Main orchestration engine
- Key methods:
  - `create_workflow()` - Initialize new workflow
  - `produce_story()` - Execute complete story workflow
  - `produce_stories_parallel()` - Parallel execution
  - `retry_failed_workflows()` - Bulk retry
  - `get_status_summary()` - Status reporting

#### Execution Flow

```
produce_story()
├── create_workflow() / load existing
├── _execute_research_phase()
│   ├── StepExecutor.execute_step()
│   │   ├── step.start()
│   │   ├── executor_fn() [with retries]
│   │   └── step.succeed() / step.fail()
│   └── registry.save_workflow()
├── _execute_outline_phase()
├── _execute_draft_phase()
├── _execute_draft_verification()
│   └── Check draft_decision
├── _execute_derivative_content()
│   ├── _generate_newsletter()
│   ├── _generate_social_content()
│   ├── _generate_visual_briefs()
│   └── _generate_prompt_pad()
├── _execute_package_verification()
│   └── Check package_decision
├── _execute_publishing_phase() [if approved]
│   ├── _generate_metadata()
│   ├── _generate_seo_package()
│   ├── _generate_youtube_package()
│   ├── _generate_distribution_plan()
│   ├── _generate_executive_summary()
│   └── _create_publishing_package()
└── workflow.succeed() / workflow.fail()
```

### 3. CLI Layer (`workflow_cli.py`)

Command-line interface for human interaction.

#### Commands

- `status` - Show workflow status summary
- `list` - List workflows with filters
- `show` - Show detailed workflow info
- `produce` - Produce single story
- `produce-batch` - Produce multiple stories in parallel
- `retry` - Retry failed workflows
- `cleanup` - Remove old state files

#### Command Structure

```
workflow_cli.py
├── main() - Argument parsing
├── cmd_status() - Status command
├── cmd_list() - List command
├── cmd_show() - Show command
├── cmd_produce() - Produce command
├── cmd_produce_batch() - Batch produce command
├── cmd_retry() - Retry command
├── cmd_cleanup() - Cleanup command
└── _load_repo_context() - Helper
```

## Data Flow

### Single Story Production

```
User/GitHub Actions
       │
       ▼
   CLI / Workflow
       │
       ▼
WorkflowOrchestrator
       │
       ├─► WorkflowRegistry (state management)
       │          │
       │          ├─► .workflow-state/story.json (read/write)
       │          │
       ▼          ▼
   StepExecutor ──► OpenRouterClient (API calls)
       │                    │
       │                    ▼
       │              OpenRouter API
       │                    │
       │                    ▼
       ├────────────► Generated Content
       │
       ▼
   File System
   (articles/, publishing/, etc.)
```

### Parallel Story Production

```
WorkflowOrchestrator.produce_stories_parallel()
       │
       ├─► ThreadPoolExecutor (max_workers=max_parallel_stories)
       │        │
       │        ├─► Worker 1: produce_story(slug-1)
       │        ├─► Worker 2: produce_story(slug-2)
       │        └─► Worker 3: produce_story(slug-3)
       │             │
       │             ├─► Independent state tracking
       │             ├─► Independent API calls
       │             └─► Independent file writes
       │
       └─► Wait for all to complete
               │
               ▼
         List[StoryWorkflow]
```

## State Transitions

### Workflow State Machine

```
PENDING ──start()──► RUNNING ──succeed()──► SUCCESS (terminal)
                        │
                        ├──fail()──► FAILED (terminal)
                        │
                        └──cancel()──► CANCELLED (terminal)

Draft/Package gates may result in:
RUNNING ──gate:HOLD/REJECT──► SKIPPED (terminal)
```

### Step State Machine

```
PENDING ──start()──► RUNNING ──succeed()──► SUCCESS
                        │
                        └──fail()──► FAILED ──can_retry()?──Yes──► RETRYING
                                                    │
                                                    No
                                                    │
                                                    ▼
                                              (stays FAILED)
```

## Retry Logic

### Exponential Backoff

```python
attempt = 1
while attempt <= max_attempts:
    try:
        execute()
        return success
    except Exception:
        if attempt < max_attempts:
            sleep(retry_delay_seconds)
            attempt += 1
        else:
            return failure
```

Default configuration:
- `max_attempts` = 3
- `retry_delay_seconds` = 60

### Retry Scope

- **Step-level**: Individual step failures retry automatically
- **Workflow-level**: Failed workflows can be manually retried via CLI
- **Transient errors**: Network timeouts, API rate limits
- **Non-retryable**: Validation failures (HOLD/REJECT decisions), invalid inputs

## Concurrency Control

### Thread Pool Execution

Uses Python's `concurrent.futures.ThreadPoolExecutor`:

```python
with ThreadPoolExecutor(max_workers=max_parallel) as executor:
    futures = {
        executor.submit(produce_story, slug): slug
        for slug in slugs
    }
    for future in as_completed(futures):
        result = future.result()
```

### Resource Isolation

Each story workflow:
- Has independent state file
- Makes independent API calls
- Writes to different file paths
- Can fail without affecting others

### Synchronization Points

- State file writes (atomic via temp + rename)
- Git commits (handled by GitHub Actions)
- OpenRouter API (rate limiting by provider)

## Error Handling

### Error Categories

1. **Transient Errors**
   - Network timeouts
   - OpenRouter 429/5xx responses
   - Temporary file locks
   - Action: Automatic retry with backoff

2. **Validation Errors**
   - Draft gate: HOLD or REJECT
   - Package gate: HOLD or REJECT
   - Action: Stop workflow, mark as SKIPPED

3. **Fatal Errors**
   - Max retries exceeded
   - Invalid API key
   - Missing required files
   - Action: Mark workflow as FAILED

### Error Recovery

1. User inspects failed workflow:
   ```bash
   workflow_cli.py show failed-slug
   ```

2. User fixes underlying issue (API key, files, etc.)

3. User retries:
   ```bash
   workflow_cli.py retry
   ```

4. Orchestrator resumes from last successful step

## Monitoring & Observability

### Metrics Collected

- Total workflows
- Status distribution (pending/running/success/failed)
- Currently running workflows + duration
- Failed workflows + error messages
- Recent completions + verification decisions
- Step-level timing and retry counts

### Monitoring Interfaces

1. **CLI Status Command**
   - Real-time status summary
   - JSON output for scripting
   - Detailed workflow inspection

2. **GitHub Actions Summary**
   - Workflow execution summaries
   - Status tables and charts
   - Artifact downloads (state files)

3. **Workflow State Files**
   - Complete history in JSON
   - Machine-readable for analysis
   - Queryable with `jq` or scripts

## Integration Points

### GitHub Actions

Orchestrator integrates with existing workflows:

```yaml
- name: Run orchestrated production
  run: |
    python scripts/workflow_cli.py produce-batch "$SLUGS" \
      --max-parallel 3 \
      --max-retries 3
```

### OpenRouter Client

Reuses existing `dadt_common.py`:

```python
client = dc.OpenRouterClient(
    api_key=api_key,
    model=model,
    max_tokens=max_tokens,
)

content = client.call("step name", prompt)
```

### File System

Follows existing folder structure:

```
case-files/active/
articles/drafts/
articles/final/
publishing/packages/
.workflow-state/  (new)
```

## Performance Considerations

### Bottlenecks

1. **OpenRouter API Calls**
   - Sequential per story
   - Rate limited by provider
   - Mitigation: Parallel story execution

2. **File I/O**
   - State file writes after each step
   - Mitigation: Async I/O (future enhancement)

3. **Memory**
   - Full content kept in workflow metadata
   - Mitigation: Stream large responses (future enhancement)

### Scalability

Current limits:
- Parallel stories: 3-5 recommended
- State files: Thousands (cleanup after 30 days)
- Workflow duration: 10-30 minutes per story

## Security Considerations

### Secrets Management

- API keys via environment variables
- Never logged or persisted to state files
- GitHub Actions secrets for automation

### State File Security

- Contains story content (not sensitive)
- Gitignored by default
- No credentials or API keys

### API Usage

- Rate limiting by OpenRouter
- Cost tracking recommended
- Model selection affects cost

## Future Enhancements

### Planned Features

1. **Web Dashboard**
   - Real-time monitoring
   - Visual workflow progress
   - Interactive retry/cancel

2. **Advanced Analytics**
   - Cost tracking per story
   - Performance profiling
   - Success rate metrics

3. **Dependency Management**
   - Story prerequisites
   - Parallel stage execution
   - Critical path analysis

4. **Notifications**
   - Slack/Discord webhooks
   - Email alerts
   - Failure summaries

5. **Checkpointing**
   - Mid-step resumption
   - Partial retry
   - Incremental progress

## Testing Strategy

### Unit Tests

- State management (`test_workflow_state.py`)
- Serialization/deserialization
- Status transitions
- Retry logic

### Integration Tests

- End-to-end story production
- Parallel execution
- Error recovery
- State persistence

### Manual Testing

```bash
# Single story
python scripts/workflow_cli.py produce test-story

# Parallel stories
python scripts/workflow_cli.py produce-batch "s1,s2,s3"

# Status monitoring
watch -n 5 'python scripts/workflow_cli.py status'
```

## Deployment

### Local Development

```bash
export OPENROUTER_API_KEY="key"
python3 scripts/workflow_cli.py produce my-story
```

### GitHub Actions

Workflows already configured:
- `.github/workflows/orchestrated-production.yml`
- `.github/workflows/workflow-monitor.yml`

### Requirements

- Python 3.11+
- No external dependencies beyond base repository
- OpenRouter API key

## Maintenance

### Cleanup Schedule

```bash
# Weekly cleanup of state files
python scripts/workflow_cli.py cleanup --days 30
```

### Monitoring Schedule

```bash
# Hourly health check (automated via GitHub Actions)
python scripts/workflow_cli.py status
```

### Backup Strategy

State files uploaded as GitHub Actions artifacts (30-day retention).

## References

- [Main Documentation](WORKFLOW_ORCHESTRATOR.md)
- [Quick Start Guide](ORCHESTRATOR_QUICKSTART.md)
- [DADT Repository README](../README.md)
- [DADT Agent Definitions](../AGENTS.md)
