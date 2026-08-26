#!/usr/bin/env python3
"""CLI interface for DADT workflow orchestration.

Provides commands to manage, monitor, and control story production workflows.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

import dadt_common as dc
from workflow_orchestrator import OrchestratorConfig, WorkflowOrchestrator
from workflow_state import WorkflowStatus


def cmd_status(args: argparse.Namespace) -> int:
    """Show workflow status summary."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    orchestrator = WorkflowOrchestrator(config)
    
    summary = orchestrator.get_status_summary()
    
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    
    print("=" * 60)
    print("WORKFLOW STATUS SUMMARY")
    print("=" * 60)
    print(f"\nTotal workflows: {summary['total']}")
    print("\nBy status:")
    for status, count in summary["by_status"].items():
        print(f"  {status:15s}: {count:3d}")
    
    if summary["running"]:
        print(f"\nCurrently running ({len(summary['running'])}):")
        for item in summary["running"]:
            duration = item["duration"] or 0
            print(f"  - {item['slug']} ({duration:.0f}s)")
    
    if summary["failed"]:
        print(f"\nFailed workflows ({len(summary['failed'])}):")
        for item in summary["failed"]:
            print(f"  - {item['slug']}")
            if item.get("error"):
                print(f"    Error: {item['error'][:100]}")
    
    if summary["recent_completions"]:
        print(f"\nRecent completions:")
        for item in summary["recent_completions"]:
            duration = item["duration"] or 0
            status_str = item["status"]
            decisions = []
            if item.get("draft_decision"):
                decisions.append(f"draft:{item['draft_decision']}")
            if item.get("package_decision"):
                decisions.append(f"pkg:{item['package_decision']}")
            decision_str = f" [{', '.join(decisions)}]" if decisions else ""
            print(f"  - {item['slug']:30s} {status_str:10s} {duration:6.0f}s{decision_str}")
    
    print()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List workflows."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    orchestrator = WorkflowOrchestrator(config)
    
    status_filter = None
    if args.status:
        try:
            status_filter = WorkflowStatus(args.status)
        except ValueError:
            print(f"Error: Invalid status '{args.status}'", file=sys.stderr)
            print(f"Valid statuses: {', '.join(s.value for s in WorkflowStatus)}", file=sys.stderr)
            return 1
    
    workflows = orchestrator.registry.list_workflows(
        status=status_filter,
        limit=args.limit,
    )
    
    if args.json:
        print(json.dumps([w.to_dict() for w in workflows], indent=2))
        return 0
    
    if not workflows:
        print("No workflows found.")
        return 0
    
    print(f"{'Slug':<35} {'Status':<12} {'Draft':<8} {'Package':<8} {'Duration':>10}")
    print("-" * 80)
    
    for w in workflows:
        duration_str = f"{w.duration:.0f}s" if w.duration else "N/A"
        draft = w.draft_decision or "-"
        package = w.package_decision or "-"
        print(f"{w.story_slug:<35} {w.status.value:<12} {draft:<8} {package:<8} {duration_str:>10}")
    
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show detailed workflow information."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    orchestrator = WorkflowOrchestrator(config)
    
    workflow = orchestrator.registry.get_workflow(args.slug)
    if not workflow:
        print(f"Error: Workflow not found: {args.slug}", file=sys.stderr)
        return 1
    
    if args.json:
        print(json.dumps(workflow.to_dict(), indent=2))
        return 0
    
    print("=" * 60)
    print(f"WORKFLOW: {workflow.story_slug}")
    print("=" * 60)
    print(f"Status:           {workflow.status.value}")
    print(f"Run ID:           {workflow.run_id}")
    print(f"Run date:         {workflow.run_date}")
    print(f"Draft decision:   {workflow.draft_decision or 'N/A'}")
    print(f"Package decision: {workflow.package_decision or 'N/A'}")
    print(f"Archive eligible: {workflow.archive_eligible}")
    
    if workflow.created_at:
        created = datetime.fromtimestamp(workflow.created_at, tz=timezone.utc)
        print(f"Created at:       {created.isoformat()}")
    
    if workflow.duration:
        print(f"Duration:         {workflow.duration:.1f}s")
    
    if workflow.steps:
        print("\nPipeline steps:")
        print(f"  {'Stage':<25} {'Status':<12} {'Attempts':<10} {'Duration':>10}")
        print("  " + "-" * 60)
        for step_name, step in workflow.steps.items():
            duration_str = f"{step.duration:.0f}s" if step.duration else "N/A"
            attempt_str = f"{step.attempt}/{step.max_attempts}"
            print(f"  {step_name:<25} {step.status.value:<12} {attempt_str:<10} {duration_str:>10}")
            if step.error:
                print(f"    Error: {step.error[:70]}")
    
    if workflow.metadata.get("package_dir"):
        print(f"\nPackage directory: {workflow.metadata['package_dir']}")
    
    return 0


def cmd_produce(args: argparse.Namespace) -> int:
    """Produce a single story."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
        max_retries_per_step=args.max_retries,
        log_level=args.log_level,
    )
    orchestrator = WorkflowOrchestrator(config)
    
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        return 1
    
    model = args.model or os.environ.get("OPENROUTER_MODEL", dc.DEFAULT_MODEL)
    run_date = args.run_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_id = args.run_id or f"cli-{int(datetime.now().timestamp())}"
    
    client = dc.OpenRouterClient(
        api_key=api_key,
        model=model,
        referer=os.environ.get("OPENROUTER_SITE_URL", "").strip(),
        title=os.environ.get("OPENROUTER_SITE_NAME", "DADT CLI").strip(),
        max_tokens=int(os.environ.get("OPENROUTER_MAX_TOKENS", dc.DEFAULT_MAX_TOKENS)),
    )
    
    if not dc.is_valid_slug(args.slug):
        print("Error: Invalid slug format", file=sys.stderr)
        return 1

    repo_context = _load_repo_context(config.root_dir, args.slug)
    
    print(f"Producing story: {args.slug}")
    print(f"Model: {model}")
    print(f"Run date: {run_date}")
    print()
    
    workflow = orchestrator.produce_story(
        story_slug=args.slug,
        run_date=run_date,
        run_id=run_id,
        client=client,
        repo_context=repo_context,
    )
    
    print()
    print("=" * 60)
    print(f"Story production complete: {workflow.story_slug}")
    print(f"Status: {workflow.status.value}")
    print(f"Duration: {workflow.duration:.1f}s" if workflow.duration else "Duration: N/A")
    print(f"Draft decision: {workflow.draft_decision or 'N/A'}")
    print(f"Package decision: {workflow.package_decision or 'N/A'}")
    
    if workflow.metadata.get("package_dir"):
        print(f"Package directory: {workflow.metadata['package_dir']}")
    
    return 0 if workflow.status == WorkflowStatus.SUCCESS else 1


def cmd_produce_batch(args: argparse.Namespace) -> int:
    """Produce multiple stories in parallel."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
        max_parallel_stories=args.max_parallel,
        max_retries_per_step=args.max_retries,
        enable_parallel_execution=True,
        log_level=args.log_level,
    )
    orchestrator = WorkflowOrchestrator(config)
    
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        return 1
    
    slugs = [s.strip() for s in args.slugs.split(",")]
    if not all(dc.is_valid_slug(slug) for slug in slugs):
        print("Error: Invalid slug format", file=sys.stderr)
        return 1
    
    model = args.model or os.environ.get("OPENROUTER_MODEL", dc.DEFAULT_MODEL)
    run_date = args.run_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_id = args.run_id or f"cli-batch-{int(datetime.now().timestamp())}"
    
    client = dc.OpenRouterClient(
        api_key=api_key,
        model=model,
        referer=os.environ.get("OPENROUTER_SITE_URL", "").strip(),
        title=os.environ.get("OPENROUTER_SITE_NAME", "DADT CLI").strip(),
        max_tokens=int(os.environ.get("OPENROUTER_MAX_TOKENS", dc.DEFAULT_MAX_TOKENS)),
    )
    
    per_slug_context = {slug: _load_repo_context(config.root_dir, slug) for slug in slugs}
    
    print(f"Producing {len(slugs)} stories in parallel (max {config.max_parallel_stories} concurrent)")
    print(f"Model: {model}")
    print(f"Run date: {run_date}")
    print()
    
    workflows = orchestrator.produce_stories_parallel(
        story_slugs=slugs,
        run_date=run_date,
        run_id=run_id,
        client=client,
        repo_context=None,
        per_slug_context=per_slug_context,
    )
    print("=" * 60)
    print("BATCH PRODUCTION COMPLETE")
    print("=" * 60)
    
    success_count = sum(1 for w in workflows if w.status == WorkflowStatus.SUCCESS)
    print(f"Total: {len(workflows)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(workflows) - success_count}")
    print()
    
    for workflow in workflows:
        status_icon = "✓" if workflow.status == WorkflowStatus.SUCCESS else "✗"
        print(f"{status_icon} {workflow.story_slug:<35} {workflow.status.value}")
    
    return 0 if success_count == len(workflows) else 1


def cmd_retry(args: argparse.Namespace) -> int:
    """Retry failed workflows."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    orchestrator = WorkflowOrchestrator(config)
    
    workflows = orchestrator.retry_failed_workflows()
    
    print(f"Marked {len(workflows)} workflows for retry:")
    for w in workflows:
        print(f"  - {w.story_slug}")
    
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Clean up old workflow state files."""
    config = OrchestratorConfig(
        root_dir=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    orchestrator = WorkflowOrchestrator(config)
    
    removed = orchestrator.registry.cleanup_old_workflows(days=args.days)
    
    print(f"Removed {removed} workflow state files older than {args.days} days")
    return 0


def _load_repo_context(root_dir: Path, story_slug: str | None) -> dict[str, str]:
    """Load repository context files."""
    def read(rel: str) -> str:
        path = root_dir / rel
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""
    
    repo_rules = "\n\n".join(
        [
            read("README.md"),
            read("AGENTS.md"),
            read("prompts/research-packet.md"),
            read("prompts/outline-builder.md"),
            read("prompts/draft-builder.md"),
            read("prompts/newsletter-builder.md"),
            read("prompts/social-builder.md"),
            read("prompts/thumbnail-brief-generator.md"),
            read("agents/verifier.md"),
            read("agents/publisher.md"),
        ]
    )
    
    selected_context = ""
    if story_slug:
        selected_files = sorted((root_dir / "research/selected").glob("*.md"))
        relevant_selected = []
        for file_path in selected_files:
            text = file_path.read_text(encoding="utf-8")
            if story_slug in text or story_slug in file_path.name:
                relevant_selected.append(f"## {file_path.relative_to(root_dir).as_posix()}\n\n{text}")
        selected_context = "\n\n".join(relevant_selected)
    
    return {
        "repo_rules": repo_rules,
        "selected_context": selected_context,
    }


def _positive_int(value: str) -> int:
    """Argument type that requires a positive integer (>= 1)."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DADT Workflow Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--state-dir",
        default=".workflow-state",
        help="Workflow state directory (default: .workflow-state)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show workflow status summary")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List workflows")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, help="Limit number of results")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show workflow details")
    show_parser.add_argument("slug", help="Story slug")
    show_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Produce command
    produce_parser = subparsers.add_parser("produce", help="Produce a single story")
    produce_parser.add_argument("slug", help="Story slug")
    produce_parser.add_argument("--model", help="OpenRouter model override")
    produce_parser.add_argument("--run-date", help="Run date (ISO format)")
    produce_parser.add_argument("--run-id", help="Run ID")
    produce_parser.add_argument("--max-retries", type=int, default=3, help="Max retries per step")
    produce_parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    # Produce batch command
    batch_parser = subparsers.add_parser("produce-batch", help="Produce multiple stories in parallel")
    batch_parser.add_argument("slugs", help="Comma-separated story slugs")
    batch_parser.add_argument("--max-parallel", type=_positive_int, default=3, help="Max parallel stories")
    batch_parser.add_argument("--model", help="OpenRouter model override")
    batch_parser.add_argument("--run-date", help="Run date (ISO format)")
    batch_parser.add_argument("--run-id", help="Run ID")
    batch_parser.add_argument("--max-retries", type=int, default=3, help="Max retries per step")
    batch_parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    # Retry command
    retry_parser = subparsers.add_parser("retry", help="Retry failed workflows")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old workflow states")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Remove states older than N days")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "status": cmd_status,
        "list": cmd_list,
        "show": cmd_show,
        "produce": cmd_produce,
        "produce-batch": cmd_produce_batch,
        "retry": cmd_retry,
        "cleanup": cmd_cleanup,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
