"""Workflow orchestrator for DADT production pipeline.

Coordinates story production workflows with enhanced error handling, retry logic,
parallel execution management, and state tracking.
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from workflow_state import (
    StepState,
    StoryStage,
    StoryWorkflow,
    WorkflowRegistry,
    WorkflowStatus,
)

try:
    import dadt_common as dc
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    import dadt_common as dc


logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """Configuration for workflow orchestrator."""
    root_dir: Path = field(default_factory=lambda: Path.cwd())
    state_dir: Path = field(default_factory=lambda: Path(".workflow-state"))
    max_parallel_stories: int = 3
    max_retries_per_step: int = 3
    retry_delay_seconds: int = 60
    enable_parallel_execution: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Configure logging."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


@dataclass
class StepExecutor:
    """Executes individual workflow steps with retry logic."""
    config: OrchestratorConfig
    registry: WorkflowRegistry
    
    def execute_step(
        self,
        workflow: StoryWorkflow,
        stage: StoryStage,
        executor_fn: Callable[[], tuple[str, str]],
    ) -> bool:
        """Execute a workflow step with retry logic.
        
        Args:
            workflow: The story workflow
            stage: The pipeline stage
            executor_fn: Function that returns (content, output_path)
            
        Returns:
            True if step succeeded, False otherwise
        """
        step = workflow.get_step(stage)
        
        while True:
            step.start()
            self.registry.save_workflow(workflow)
            
            logger.info(
                f"[{workflow.story_slug}] Starting {stage.value} "
                f"(attempt {step.attempt}/{step.max_attempts})"
            )
            
            try:
                content, output_path = executor_fn()
                step.succeed(output_path=output_path)
                self.registry.save_workflow(workflow)
                logger.info(
                    f"[{workflow.story_slug}] Completed {stage.value} "
                    f"in {step.duration:.1f}s -> {output_path}"
                )
                return True
                
            except Exception as exc:
                error_msg = f"{type(exc).__name__}: {exc}"
                step.fail(error_msg)
                self.registry.save_workflow(workflow)
                
                logger.error(
                    f"[{workflow.story_slug}] Failed {stage.value}: {error_msg}"
                )
                
                if step.can_retry():
                    step.retry()
                    self.registry.save_workflow(workflow)
                    logger.warning(
                        f"[{workflow.story_slug}] Retrying {stage.value} "
                        f"in {self.config.retry_delay_seconds}s..."
                    )
                    time.sleep(self.config.retry_delay_seconds)
                else:
                    logger.error(
                        f"[{workflow.story_slug}] Max retries exceeded for {stage.value}"
                    )
                    return False


class WorkflowOrchestrator:
    """Orchestrates the complete story production pipeline."""
    
    def __init__(self, config: OrchestratorConfig | None = None):
        """Initialize orchestrator."""
        self.config = config or OrchestratorConfig()
        self.registry = WorkflowRegistry(state_dir=self.config.state_dir)
        self.executor = StepExecutor(config=self.config, registry=self.registry)
        
    def create_workflow(self, story_slug: str, run_date: str, run_id: str) -> StoryWorkflow:
        """Create a new story workflow."""
        workflow = StoryWorkflow(
            story_slug=story_slug,
            run_date=run_date,
            run_id=run_id,
        )
        self.registry.add_workflow(workflow)
        logger.info(f"Created workflow for story: {story_slug}")
        return workflow
    
    def produce_story(
        self,
        story_slug: str,
        run_date: str,
        run_id: str,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> StoryWorkflow:
        """Execute complete story production workflow.
        
        Args:
            story_slug: Story identifier
            run_date: ISO date of production run
            run_id: Unique run identifier
            client: OpenRouter API client
            repo_context: Dictionary of repository context files
            
        Returns:
            Completed StoryWorkflow
        """
        workflow = self.registry.get_workflow(story_slug)
        if workflow is None:
            workflow = self.create_workflow(story_slug, run_date, run_id)
        
        workflow.start()
        self.registry.save_workflow(workflow)
        
        logger.info(f"Starting story production: {story_slug}")
        
        try:
            if not self._execute_research_phase(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if not self._execute_outline_phase(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if not self._execute_draft_phase(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if not self._execute_draft_verification(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if workflow.draft_decision != "PUBLISH":
                logger.warning(
                    f"[{story_slug}] Draft gate returned {workflow.draft_decision}, "
                    "stopping pipeline"
                )
                workflow.status = WorkflowStatus.SKIPPED
                workflow.completed_at = time.time()
                self.registry.save_workflow(workflow)
                return workflow
            
            if not self._execute_derivative_content(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if not self._execute_package_verification(workflow, client, repo_context):
                workflow.fail()
                self.registry.save_workflow(workflow)
                return workflow
            
            if workflow.package_decision == "PUBLISH":
                if not self._execute_publishing_phase(workflow, client, repo_context):
                    workflow.fail()
                    self.registry.save_workflow(workflow)
                    return workflow
                workflow.archive_eligible = True
            
            workflow.succeed()
            self.registry.save_workflow(workflow)
            logger.info(f"Story production complete: {story_slug}")
            
        except Exception as exc:
            logger.exception(f"[{story_slug}] Workflow failed with exception")
            workflow.fail()
            self.registry.save_workflow(workflow)
        
        return workflow
    
    def _execute_research_phase(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute research packet generation."""
        def executor():
            prompt = textwrap.dedent(f"""
                Today's UTC date is {workflow.run_date}.
                Target slug: {workflow.story_slug}.
                
                Repository rules:
                {repo_context.get("repo_rules", "")}
                
                Selected story context:
                {repo_context.get("selected_context", "")}
                
                Return markdown only for /case-files/active/{workflow.story_slug}-research-packet.md.
                Use the repository's required research packet sections.
            """).strip()
            
            content = client.call("research packet", prompt)
            output_path = self._save_file(
                f"case-files/active/{workflow.story_slug}-research-packet.md",
                content,
            )
            workflow.metadata["research_packet"] = content
            return content, output_path
        
        return self.executor.execute_step(workflow, StoryStage.RESEARCH, executor)
    
    def _execute_outline_phase(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute article outline generation."""
        def executor():
            prompt = textwrap.dedent(f"""
                Today's UTC date is {workflow.run_date}.
                Target slug: {workflow.story_slug}.
                
                Repository rules:
                {repo_context.get("repo_rules", "")}
                
                Research packet:
                {workflow.metadata.get("research_packet", "")}
                
                Return markdown only for /articles/outlines/{workflow.story_slug}-outline.md.
                Use the repository's outline structure and keep the story evidence-first.
            """).strip()
            
            content = client.call("article outline", prompt)
            output_path = self._save_file(
                f"articles/outlines/{workflow.story_slug}-outline.md",
                content,
            )
            workflow.metadata["outline"] = content
            return content, output_path
        
        return self.executor.execute_step(workflow, StoryStage.OUTLINE, executor)
    
    def _execute_draft_phase(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute article draft generation."""
        def executor():
            prompt = textwrap.dedent(f"""
                Today's UTC date is {workflow.run_date}.
                Target slug: {workflow.story_slug}.
                
                Repository rules:
                {repo_context.get("repo_rules", "")}
                
                Research packet:
                {workflow.metadata.get("research_packet", "")}
                
                Outline:
                {workflow.metadata.get("outline", "")}
                
                Return markdown only for /articles/drafts/{workflow.story_slug}-draft.md.
                Write a 3500-4500 word investigative article with sourced claims and explicit uncertainty.
            """).strip()
            
            max_tokens = int(os.environ.get("OPENROUTER_DRAFT_MAX_TOKENS", "16000"))
            content = client.call("article draft", prompt, max_tokens=max_tokens)
            output_path = self._save_file(
                f"articles/drafts/{workflow.story_slug}-draft.md",
                content,
            )
            workflow.metadata["draft"] = content
            return content, output_path
        
        return self.executor.execute_step(workflow, StoryStage.DRAFT, executor)
    
    def _execute_draft_verification(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute draft verification."""
        def executor():
            prompt = textwrap.dedent(f"""
                Today's UTC date is {workflow.run_date}.
                Target slug: {workflow.story_slug}.
                
                Repository rules:
                {repo_context.get("repo_rules", "")}
                
                Research packet:
                {workflow.metadata.get("research_packet", "")}
                
                Draft article:
                {workflow.metadata.get("draft", "")}
                
                Return markdown only for /publishing/reports/{workflow.story_slug}-draft-verification-report.md.
                End the report with these exact lines:
                FINAL GRADE: <A|B|C|D>
                FINAL DECISION: <PUBLISH|HOLD|REJECT>
            """).strip()
            
            content = client.call("draft verification", prompt)
            output_path = self._save_file(
                f"publishing/reports/{workflow.story_slug}-draft-verification-report.md",
                content,
            )
            workflow.draft_decision = dc.parse_decision(content)
            workflow.metadata["draft_report"] = content
            return content, output_path
        
        return self.executor.execute_step(workflow, StoryStage.DRAFT_VERIFICATION, executor)
    
    def _execute_derivative_content(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute derivative content generation (newsletter, social, etc)."""
        workflow.metadata["derivative_paths"] = {}

        def executor():
            self._generate_newsletter(workflow, client, repo_context)
            self._generate_social_content(workflow, client, repo_context)
            self._generate_visual_briefs(workflow, client, repo_context)
            self._generate_prompt_pad(workflow, client, repo_context)
            return "", ""

        return self.executor.execute_step(workflow, StoryStage.DERIVATIVE_CONTENT, executor)
    
    def _generate_newsletter(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> None:
        """Generate newsletter content."""
        prompt = textwrap.dedent(f"""
            Today's UTC date is {workflow.run_date}.
            Target slug: {workflow.story_slug}.
            
            Repository rules:
            {repo_context.get("repo_rules", "")}
            
            Approved investigation:
            {workflow.metadata.get("draft", "")}
            
            Draft verification report:
            {workflow.metadata.get("draft_report", "")}
            
            Return markdown only for /newsletter/drafts/{workflow.story_slug}-newsletter.md.
        """).strip()
        
        content = client.call("newsletter draft", prompt)
        output_path = self._save_file(
            f"newsletter/drafts/{workflow.story_slug}-newsletter.md",
            content,
        )
        workflow.metadata["newsletter"] = content
        workflow.metadata["derivative_paths"]["newsletter"] = output_path
    
    def _generate_social_content(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> None:
        """Generate social media content."""
        prompt = textwrap.dedent(f"""
            Today's UTC date is {workflow.run_date}.
            Target slug: {workflow.story_slug}.
            
            Repository rules:
            {repo_context.get("repo_rules", "")}
            
            Approved investigation:
            {workflow.metadata.get("draft", "")}
            
            Draft verification report:
            {workflow.metadata.get("draft_report", "")}
            
            Return markdown with these exact top-level headings only:
            # LINKEDIN
            # X THREADS
            # SHORTS
            # TIKTOKS
            # CTA BANK
            # HOOK BANK
        """).strip()
        
        content = client.call("social bundle", prompt)
        sections = dc.split_sections(
            content,
            ["LINKEDIN", "X THREADS", "SHORTS", "TIKTOKS", "CTA BANK", "HOOK BANK"],
        )
        
        paths = {}
        paths["linkedin"] = self._save_file(
            f"social/linkedin/{workflow.story_slug}-linkedin.md",
            sections["LINKEDIN"],
        )
        paths["x_threads"] = self._save_file(
            f"social/x-threads/{workflow.story_slug}-x-threads.md",
            sections["X THREADS"],
        )
        paths["shorts"] = self._save_file(
            f"video/shorts/{workflow.story_slug}-shorts.md",
            sections["SHORTS"],
        )
        paths["tiktoks"] = self._save_file(
            f"video/tiktoks/{workflow.story_slug}-tiktoks.md",
            sections["TIKTOKS"],
        )
        paths["banks"] = self._save_file(
            f"social/{workflow.story_slug}-cta-hook-bank.md",
            sections["CTA BANK"] + "\n\n" + sections["HOOK BANK"],
        )
        
        workflow.metadata["social_sections"] = sections
        workflow.metadata["derivative_paths"].update(paths)
    
    def _generate_visual_briefs(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> None:
        """Generate visual content briefs."""
        prompt = textwrap.dedent(f"""
            Today's UTC date is {workflow.run_date}.
            Target slug: {workflow.story_slug}.
            
            Repository rules:
            {repo_context.get("repo_rules", "")}
            
            Approved investigation:
            {workflow.metadata.get("draft", "")}
            
            Return markdown with these exact top-level headings only:
            # THUMBNAIL BRIEF
            # SOCIAL IMAGE BRIEF
        """).strip()
        
        content = client.call("visual briefs", prompt)
        sections = dc.split_sections(content, ["THUMBNAIL BRIEF", "SOCIAL IMAGE BRIEF"])
        
        paths = {}
        paths["thumbnail"] = self._save_file(
            f"assets/thumbnails/{workflow.story_slug}-thumbnail-brief.md",
            sections["THUMBNAIL BRIEF"],
        )
        paths["social_brief"] = self._save_file(
            f"assets/social/{workflow.story_slug}-social-brief.md",
            sections["SOCIAL IMAGE BRIEF"],
        )
        
        workflow.metadata["visual_sections"] = sections
        workflow.metadata["derivative_paths"].update(paths)
    
    def _generate_prompt_pad(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> None:
        """Generate prompt pad."""
        prompt = textwrap.dedent(f"""
            Today's UTC date is {workflow.run_date}.
            Target slug: {workflow.story_slug}.
            
            Approved investigation:
            {workflow.metadata.get("draft", "")}
            
            Create a reusable prompt pad for follow-up reporting, interviews, fact-checking, and derivative content on this story.
            Return markdown only for /prompt-pads/{workflow.story_slug}-prompt-pad.md.
        """).strip()
        
        content = client.call("prompt pad", prompt)
        output_path = self._save_file(
            f"prompt-pads/{workflow.story_slug}-prompt-pad.md",
            content,
        )
        workflow.metadata["prompt_pad"] = content
        workflow.metadata["derivative_paths"]["prompt_pad"] = output_path
    
    def _execute_package_verification(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute package verification."""
        def executor():
            social = workflow.metadata.get("social_sections", {})
            visual = workflow.metadata.get("visual_sections", {})
            
            prompt = textwrap.dedent(f"""
                Today's UTC date is {workflow.run_date}.
                Target slug: {workflow.story_slug}.
                
                Repository rules:
                {repo_context.get("repo_rules", "")}
                
                Investigation:
                {workflow.metadata.get("draft", "")}
                
                Newsletter:
                {workflow.metadata.get("newsletter", "")}
                
                LinkedIn:
                {social.get("LINKEDIN", "")}
                
                X Threads:
                {social.get("X THREADS", "")}
                
                Shorts:
                {social.get("SHORTS", "")}
                
                TikToks:
                {social.get("TIKTOKS", "")}
                
                Thumbnail brief:
                {visual.get("THUMBNAIL BRIEF", "")}
                
                Social image brief:
                {visual.get("SOCIAL IMAGE BRIEF", "")}
                
                Prompt pad:
                {workflow.metadata.get("prompt_pad", "")}
                
                Return markdown only for /publishing/reports/{workflow.story_slug}-package-verification-report.md.
                End the report with these exact lines:
                FINAL GRADE: <A|B|C|D>
                FINAL DECISION: <PUBLISH|HOLD|REJECT>
            """).strip()
            
            content = client.call("package verification", prompt)
            output_path = self._save_file(
                f"publishing/reports/{workflow.story_slug}-package-verification-report.md",
                content,
            )
            workflow.package_decision = dc.parse_decision(content)
            workflow.metadata["package_report"] = content
            return content, output_path
        
        return self.executor.execute_step(workflow, StoryStage.PACKAGE_VERIFICATION, executor)
    
    def _execute_publishing_phase(
        self,
        workflow: StoryWorkflow,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> bool:
        """Execute publishing package generation."""
        logger.info(f"[{workflow.story_slug}] Generating publishing package")
        
        try:
            self._generate_metadata(workflow, client)
            self._generate_seo_package(workflow, client)
            self._generate_youtube_package(workflow, client)
            self._generate_distribution_plan(workflow, client)
            self._generate_executive_summary(workflow, client)
            self._create_publishing_package(workflow)
            return True
        except Exception as exc:
            logger.error(f"[{workflow.story_slug}] Publishing phase failed: {exc}")
            return False
    
    def _generate_metadata(self, workflow: StoryWorkflow, client: dc.OpenRouterClient) -> None:
        """Generate publication metadata."""
        prompt = textwrap.dedent(f"""
            Target slug: {workflow.story_slug}.
            Using the approved investigation and both verification reports, create publication metadata.
            Return markdown only with the heading '# Publication Metadata' and fields for title, slug, deck, author, content type, status, prepared date, draft verification, package verification, estimated reading time, primary category, secondary categories, featured-image alt text, and disclosure.
            
            Investigation:
            {workflow.metadata.get("draft", "")}
            
            Draft verification report:
            {workflow.metadata.get("draft_report", "")}
            
            Package verification report:
            {workflow.metadata.get("package_report", "")}
        """).strip()
        
        workflow.metadata["metadata"] = client.call("metadata package", prompt)
    
    def _generate_seo_package(self, workflow: StoryWorkflow, client: dc.OpenRouterClient) -> None:
        """Generate SEO package."""
        prompt = textwrap.dedent(f"""
            Target slug: {workflow.story_slug}.
            Create an SEO/GEO package for the approved investigation.
            Return markdown only with the heading '# SEO Package' and sections for title options, GEO title, meta description, slug, tags, categories, schema suggestions, and internal-link ideas.
            
            Investigation:
            {workflow.metadata.get("draft", "")}
        """).strip()
        
        workflow.metadata["seo"] = client.call("seo package", prompt)
    
    def _generate_youtube_package(self, workflow: StoryWorkflow, client: dc.OpenRouterClient) -> None:
        """Generate YouTube package."""
        visual = workflow.metadata.get("visual_sections", {})
        prompt = textwrap.dedent(f"""
            Target slug: {workflow.story_slug}.
            Create a YouTube package for the approved investigation.
            Return markdown only with the heading '# YouTube Package' and sections for title options, description, chapter suggestions, tags, and thumbnail recommendations.
            
            Investigation:
            {workflow.metadata.get("draft", "")}
            
            Thumbnail brief:
            {visual.get("THUMBNAIL BRIEF", "")}
        """).strip()
        
        workflow.metadata["youtube"] = client.call("youtube package", prompt)
    
    def _generate_distribution_plan(self, workflow: StoryWorkflow, client: dc.OpenRouterClient) -> None:
        """Generate distribution plan."""
        social = workflow.metadata.get("social_sections", {})
        prompt = textwrap.dedent(f"""
            Target slug: {workflow.story_slug}.
            Create a package-only distribution schedule. Do not authorize publication.
            Return markdown only with the heading '# Distribution Plan' and a schedule covering Day 0 through Day 7 plus prepublication requirements.
            
            Investigation:
            {workflow.metadata.get("draft", "")}
            
            Newsletter:
            {workflow.metadata.get("newsletter", "")}
            
            Social summaries:
            {social.get("LINKEDIN", "")}
        """).strip()
        
        workflow.metadata["distribution"] = client.call("distribution package", prompt)
    
    def _generate_executive_summary(self, workflow: StoryWorkflow, client: dc.OpenRouterClient) -> None:
        """Generate executive summary."""
        prompt = textwrap.dedent(f"""
            Target slug: {workflow.story_slug}.
            Create an executive summary for the approved package.
            Return markdown only with the heading '# Executive Summary' and sections for story name, publication status, asset count, distribution schedule, future follow-ups, and unresolved limitations.
            
            Investigation:
            {workflow.metadata.get("draft", "")}
            
            Package verification report:
            {workflow.metadata.get("package_report", "")}
        """).strip()
        
        workflow.metadata["executive_summary"] = client.call("executive summary", prompt)
    
    def _create_publishing_package(self, workflow: StoryWorkflow) -> None:
        """Create complete publishing package directory."""
        import json
        
        package_dir = dc.next_dir(self.config.root_dir, f"publishing/packages/{workflow.story_slug}")
        package_dir.mkdir(parents=True, exist_ok=True)
        
        self._save_file(f"articles/final/{workflow.story_slug}.md", workflow.metadata["draft"])
        self._save_file(
            f"newsletter/final/{workflow.story_slug}-newsletter.md",
            workflow.metadata["newsletter"],
        )
        self._save_file(
            f"case-files/published/{workflow.story_slug}-research-packet.md",
            workflow.metadata["research_packet"],
        )
        
        social = workflow.metadata.get("social_sections", {})
        visual = workflow.metadata.get("visual_sections", {})
        
        package_files = {
            "article.md": workflow.metadata["draft"],
            "newsletter.md": workflow.metadata["newsletter"],
            "linkedin.md": social.get("LINKEDIN", ""),
            "x-threads.md": social.get("X THREADS", ""),
            "shorts.md": social.get("SHORTS", ""),
            "tiktoks.md": social.get("TIKTOKS", ""),
            "thumbnail-brief.md": visual.get("THUMBNAIL BRIEF", ""),
            "social-brief.md": visual.get("SOCIAL IMAGE BRIEF", ""),
            "prompt-pad.md": workflow.metadata.get("prompt_pad", ""),
            "seo.md": workflow.metadata.get("seo", ""),
            "youtube.md": workflow.metadata.get("youtube", ""),
            "distribution.md": workflow.metadata.get("distribution", ""),
            "executive-summary.md": workflow.metadata.get("executive_summary", ""),
            "metadata.md": workflow.metadata.get("metadata", ""),
            "research-packet.md": workflow.metadata.get("research_packet", ""),
            "draft-verification-report.md": workflow.metadata.get("draft_report", ""),
            "package-verification-report.md": workflow.metadata.get("package_report", ""),
            "validation-report.md": (
                "# Validation Summary\n\n"
                f"- Draft gate: {workflow.draft_decision}\n"
                f"- Package gate: {workflow.package_decision}\n"
            ),
        }
        
        for filename, content in package_files.items():
            (package_dir / filename).write_text(content.strip() + "\n", encoding="utf-8")
        
        (package_dir / "workflow-status.json").write_text(
            json.dumps(workflow.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
        
        workflow.metadata["package_dir"] = str(package_dir.relative_to(self.config.root_dir))
        logger.info(f"[{workflow.story_slug}] Publishing package created at {package_dir}")
    
    def _save_file(self, rel_path: str, content: str) -> str:
        """Save file and return relative path."""
        path = dc.save_file(self.config.root_dir, rel_path, content)
        return str(path.relative_to(self.config.root_dir))
    
    def produce_stories_parallel(
        self,
        story_slugs: list[str],
        run_date: str,
        run_id: str,
        client: dc.OpenRouterClient,
        repo_context: dict[str, str],
    ) -> list[StoryWorkflow]:
        """Produce multiple stories in parallel.
        
        Args:
            story_slugs: List of story slugs to produce
            run_date: ISO date of production run
            run_id: Unique run identifier
            client: OpenRouter API client
            repo_context: Dictionary of repository context files
            
        Returns:
            List of completed workflows
        """
        if not self.config.enable_parallel_execution or len(story_slugs) == 1:
            return [
                self.produce_story(slug, run_date, run_id, client, repo_context)
                for slug in story_slugs
            ]
        
        logger.info(
            f"Starting parallel production of {len(story_slugs)} stories "
            f"(max parallel: {self.config.max_parallel_stories})"
        )
        
        workflows = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_parallel_stories
        ) as executor:
            futures = {
                executor.submit(
                    self.produce_story,
                    slug,
                    run_date,
                    run_id,
                    client,
                    repo_context,
                ): slug
                for slug in story_slugs
            }
            
            for future in concurrent.futures.as_completed(futures):
                slug = futures[future]
                try:
                    workflow = future.result()
                    workflows.append(workflow)
                    logger.info(f"Completed parallel production: {slug}")
                except Exception as exc:
                    logger.exception(f"Parallel production failed for {slug}")
        
        return workflows
    
    def retry_failed_workflows(self) -> list[StoryWorkflow]:
        """Retry all failed workflows."""
        failed = self.registry.get_failed_workflows()
        logger.info(f"Retrying {len(failed)} failed workflows")
        
        results = []
        for workflow in failed:
            logger.info(f"Retrying workflow: {workflow.story_slug}")
            workflow.status = WorkflowStatus.RETRYING
            self.registry.save_workflow(workflow)
            results.append(workflow)
        
        return results
    
    def get_status_summary(self) -> dict[str, Any]:
        """Get summary of all workflow statuses."""
        all_workflows = self.registry.list_workflows()
        
        summary = {
            "total": len(all_workflows),
            "by_status": {},
            "running": [],
            "failed": [],
            "recent_completions": [],
        }
        
        for status in WorkflowStatus:
            count = sum(1 for w in all_workflows if w.status == status)
            summary["by_status"][status.value] = count
        
        summary["running"] = [
            {"slug": w.story_slug, "duration": w.duration}
            for w in all_workflows
            if w.status == WorkflowStatus.RUNNING
        ]
        
        summary["failed"] = [
            {"slug": w.story_slug, "error": w.metadata.get("error")}
            for w in all_workflows
            if w.status == WorkflowStatus.FAILED
        ]
        
        recent = sorted(
            [w for w in all_workflows if w.is_complete],
            key=lambda w: w.completed_at or 0,
            reverse=True,
        )[:10]
        
        summary["recent_completions"] = [
            {
                "slug": w.story_slug,
                "status": w.status.value,
                "duration": w.duration,
                "draft_decision": w.draft_decision,
                "package_decision": w.package_decision,
            }
            for w in recent
        ]
        
        return summary
