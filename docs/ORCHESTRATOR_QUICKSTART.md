# Workflow Orchestrator - Quick Start Guide

Get started with the DADT Workflow Orchestrator in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key
- DADT repository cloned locally

## Setup

### 1. Verify Python Version

```bash
python --version
# Should output: Python 3.11.x or higher
```

### 2. Set Environment Variables

```bash
export OPENROUTER_API_KEY="your-api-key-here"
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"  # Optional
```

Or create a `.env` file:

```bash
cat > .env <<'EOF'
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=https://didaidothat.com
OPENROUTER_SITE_NAME=DID AI DO THAT?!
EOF

# Load environment
set -a; source .env; set +a
```

### 3. Test the CLI

```bash
# Check if CLI works
python scripts/workflow_cli.py --help
```

You should see the help output with all available commands.

## First Story Production

### Single Story (Local)

Produce one story locally:

```bash
python scripts/workflow_cli.py produce my-test-story \
  --log-level INFO
```

The orchestrator will:
1. Create a workflow state file
2. Execute all pipeline stages (research → outline → draft → verification → etc)
3. Retry failed steps automatically (up to 3 times per step)
4. Save output files to the appropriate folders
5. Track progress in `.workflow-state/my-test-story.json`

### Check Status

```bash
# View overall status
python scripts/workflow_cli.py status

# List all workflows
python scripts/workflow_cli.py list

# View details for specific workflow
python scripts/workflow_cli.py show my-test-story
```

### Multiple Stories in Parallel

Produce 3 stories concurrently:

```bash
python scripts/workflow_cli.py produce-batch "story-1,story-2,story-3" \
  --max-parallel 2 \
  --max-retries 3
```

This will:
- Run 2 stories at a time (max parallel)
- Queue the third story until a slot opens
- Retry each step up to 3 times on failure
- Track state for all stories independently

## GitHub Actions Integration

### Manual Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Orchestrated story production**
4. Click **Run workflow**
5. Enter story slugs: `test-story-one,test-story-two`
6. Set max parallel: `2`
7. Click **Run workflow**

### View Results

After the workflow completes:

1. Check the **Summary** tab for the status report
2. View committed files in the repository
3. Download workflow state artifact for analysis

## Common Commands

### Production

```bash
# Single story
python scripts/workflow_cli.py produce my-story

# Multiple stories in parallel
python scripts/workflow_cli.py produce-batch "s1,s2,s3" --max-parallel 3

# With custom model
python scripts/workflow_cli.py produce my-story --model "anthropic/claude-3-haiku"
```

### Monitoring

```bash
# Status summary
python scripts/workflow_cli.py status

# List workflows
python scripts/workflow_cli.py list
python scripts/workflow_cli.py list --status failed
python scripts/workflow_cli.py list --status running

# Detailed view
python scripts/workflow_cli.py show my-story
python scripts/workflow_cli.py show my-story --json
```

### Maintenance

```bash
# Retry failed workflows
python scripts/workflow_cli.py retry

# Clean up old state files (older than 30 days)
python scripts/workflow_cli.py cleanup --days 30
```

## Example Workflow

Complete example from discovery to publication:

```bash
# 1. Set up environment
export OPENROUTER_API_KEY="your-key"

# 2. Check current status
python scripts/workflow_cli.py status

# 3. Produce a test story
python scripts/workflow_cli.py produce test-ai-incident \
  --log-level INFO

# 4. Monitor progress (in another terminal)
watch -n 5 'python scripts/workflow_cli.py show test-ai-incident'

# 5. Check final status
python scripts/workflow_cli.py show test-ai-incident

# 6. View generated assets
ls -lh articles/drafts/test-ai-incident-*
ls -lh publishing/packages/test-ai-incident/
```

## Troubleshooting

### "OPENROUTER_API_KEY environment variable not set"

Set your API key:

```bash
export OPENROUTER_API_KEY="your-key-here"
```

### "Workflow not found"

The story slug may not exist. Check available workflows:

```bash
python scripts/workflow_cli.py list
```

### Story production fails immediately

Check the error in the workflow details:

```bash
python scripts/workflow_cli.py show my-story
```

Common issues:
- Invalid story slug format (must be lowercase kebab-case)
- No research/selected files for the story
- API rate limits exceeded

### Retry a failed story

```bash
# Retry all failed workflows
python scripts/workflow_cli.py retry

# Or start fresh
rm .workflow-state/my-story.json
python scripts/workflow_cli.py produce my-story
```

## Next Steps

- Read the [full documentation](WORKFLOW_ORCHESTRATOR.md)
- Review workflow state files in `.workflow-state/`
- Set up GitHub Actions for automated production
- Configure monitoring for production use

## Tips

1. **Start small**: Test with 1-2 stories before scaling up
2. **Monitor costs**: Track OpenRouter usage in their dashboard
3. **Use retries wisely**: Default 3 retries works well for most cases
4. **Check state regularly**: Use `status` command to monitor health
5. **Clean up old state**: Run `cleanup` weekly to save disk space

## Getting Help

If you encounter issues:

1. Check `.workflow-state/[slug].json` for detailed state
2. Review logs with `--log-level DEBUG`
3. Verify environment variables are set correctly
4. Check OpenRouter API status
5. Consult the [full documentation](WORKFLOW_ORCHESTRATOR.md)
