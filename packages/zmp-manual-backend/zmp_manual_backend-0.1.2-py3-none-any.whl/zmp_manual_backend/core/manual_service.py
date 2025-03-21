import asyncio
import uuid
import os
from typing import Dict, List, Optional, Union, Set, Tuple
from zmp_manual_backend.models.manual import (
    Manual,
    Folder,
    PublishStatus,
    SolutionType,
    JobState,
    FailureReason,
    Notification,
    NotificationType,
)
from zmp_notion_exporter import NotionPageExporter
from zmp_notion_exporter.utility import transform_block_id_to_uuidv4, validate_page_id

# from zmp_notion_exporter.node import Node
from zmp_md_translator import MarkdownTranslator
import git
from dotenv import load_dotenv
import logging
from notion_client import AsyncClient
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

logger = logging.getLogger("appLogger")


class ManualService:
    def __init__(
        self,
        notion_token: str,
        root_page_id: str,
        repo_path: str = "./repo",
        source_dir: str = "docs",
        target_dir: str = "i18n",
        github_repo_url: Optional[str] = None,
        target_languages: Optional[Set[str]] = None,
    ):
        """Initialize ManualService.

        Args:
            notion_token: Notion API token
            root_page_id: ID of the root Notion page for ZCP docs
            repo_path: Path to the local repository
            source_dir: Source directory for documentation in the repo
            target_dir: Target directory for translations in the repo
            github_repo_url: URL of the GitHub repository for pushing changes
            target_languages: Set of target languages for translation
        """
        self.notion_token = notion_token
        self.repo_path = Path(repo_path).absolute()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.github_repo_url = github_repo_url
        self.target_languages = (
            target_languages if target_languages is not None else {"ko", "ja", "zh"}
        )

        # This map holds solutions and their respective root IDs
        self.root_page_ids = {}

        # First try to get solution-specific root page IDs from environment variables
        for solution_type in SolutionType:
            env_var_name = f"{solution_type.value.upper()}_ROOT_PAGE_ID"
            page_id = os.environ.get(env_var_name)
            if page_id:
                self.root_page_ids[solution_type] = page_id
                logger.info(f"Using {env_var_name}: {page_id[:8]}...")

        # For backward compatibility, also check the root_page_id parameter
        if root_page_id and "-" in root_page_id:
            # Format:  zcp:xxxxxx,apim:yyyyyyy,amdp:zzzzz
            for solution_mapping in root_page_id.split(","):
                if ":" in solution_mapping:
                    solution_type, page_id = solution_mapping.split(":", 1)
                    try:
                        solution_enum = SolutionType(solution_type.lower())
                        # Only set if not already set from environment variables
                        if solution_enum not in self.root_page_ids:
                            self.root_page_ids[solution_enum] = page_id
                            logger.info(
                                f"Using {solution_type} from root_page_id parameter: {page_id[:8]}..."
                            )
                    except ValueError as e:
                        logger.warning(
                            f"Invalid solution type in root_page_id: {solution_type}. Error: {str(e)}"
                        )
        elif root_page_id:  # If no mapping, assume it's just the ZCP root ID
            # Only set if not already set from environment variables
            if SolutionType.ZCP not in self.root_page_ids:
                self.root_page_ids[SolutionType.ZCP] = root_page_id
                logger.info(
                    f"Using ZCP root page ID from parameter: {root_page_id[:8]}..."
                )

        if not self.root_page_ids:
            logger.warning("No root page IDs provided for any solution")

        # Notification system
        self.notifications: List[Notification] = []
        self.notification_clients: Dict[str, Tuple[asyncio.Queue, Optional[str]]] = {}

        # Job tracking
        self.active_jobs: Dict[str, PublishStatus] = {}
        self.executor = ThreadPoolExecutor(max_workers=3)

        logger.info(
            f"ManualService initialized with root page IDs: {self.root_page_ids}"
        )

        # Initialize Notion client
        self.notion = AsyncClient(auth=notion_token)

        # Store progress callback for later use
        self._export_progress_callback = self._create_export_progress_callback()

    def _create_translation_progress_callback(self, job_id: str):
        """Creates a translation progress callback for a specific job.

        Args:
            job_id: The ID of the job to update progress for

        Returns:
            An async callback function that can be passed to the translator
        """

        async def translation_progress_callback(progress):
            """Update translation progress for a specific job."""
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]

                if progress.status.value == "preparing":
                    job.message = "0.0%(0/0) - Preparing translation..."
                    job.translation_progress = 0
                    job.processed_files = (
                        job.export_files
                    )  # Start with export files count
                    logger.info(job.message)
                elif progress.status.value == "translating":
                    if progress.total > 0:
                        # Calculate progress percentage for translation
                        progress_percentage = round(
                            (progress.current / progress.total) * 100, 1
                        )
                        job.translation_progress = progress_percentage

                        # Update processed files (export_files + translated files)
                        job.processed_files = job.export_files + progress.current

                        # Format message consistently with export progress
                        message = f"{progress_percentage:.1f}%({progress.current}/{progress.total})"
                        if progress.current_file:
                            message += f" - Translating page: {progress.current_file}"
                        job.message = message

                        # Update total progress based on all files (export + translations)
                        if job.total_files > 0:
                            total_progress = round(
                                (job.processed_files / job.total_files) * 100, 1
                            )
                            job.total_progress = total_progress

                        logger.info(job.message)
                elif progress.status.value == "completed":
                    job.status = JobState.COMPLETED
                    job.message = f"100.0%({progress.total}/{progress.total}) - Translation completed"
                    job.translation_progress = 100.0
                    job.processed_files = job.total_files  # All files processed
                    job.total_progress = 100.0
                    logger.info(job.message)
                elif progress.status.value == "failed":
                    job.status = JobState.FAILED
                    job.failure_reason = FailureReason.TRANSLATION_FAILED
                    job.message = f"0.0%(0/{progress.total}) - {progress.message or 'Translation failed'}"
                    job.total_progress = 0.0
                    logger.info(job.message)

        return translation_progress_callback

    def _format_page_id(self, page_id: str) -> str:
        """Format page ID to match Notion's expected format.

        Args:
            page_id: The page ID to format

        Returns:
            str: Formatted page ID in UUID format

        Raises:
            ValueError: If the page ID is invalid
        """
        try:
            # First transform to UUID format
            formatted_id = transform_block_id_to_uuidv4(page_id)

            # Validate the format
            if not validate_page_id(formatted_id):
                raise ValueError(f"Invalid page ID format: {page_id}")

            return formatted_id
        except Exception as e:
            logger.error(f"Error formatting page ID {page_id}: {str(e)}")
            raise ValueError(f"Invalid page ID: {page_id}")

    async def get_manuals(
        self, selected_solution: SolutionType = SolutionType.ZCP
    ) -> List[Union[Manual, Folder]]:
        """Retrieve the manual list from Notion and organize it into a tree structure.

        Args:
            selected_solution: The solution type selected by the user in the frontend (defaults to ZCP)

        Returns:
            List[Union[Manual, Folder]]: A hierarchical list of manuals and folders

        Raises:
            ValueError: If the root page ID is invalid or not configured
        """
        try:
            # Get the root page ID for the selected solution
            root_page_id = self.root_page_ids.get(selected_solution)
            if not root_page_id:
                error_msg = f"No root page ID configured for solution {selected_solution.value}. Check environment variables."
                logger.error(error_msg)
                logger.error(f"Available solutions: {list(self.root_page_ids.keys())}")
                logger.error(
                    f"Environment variable {selected_solution.value.upper()}_ROOT_PAGE_ID is not set"
                )
                raise ValueError(error_msg)

            # Format and validate the root page ID
            try:
                formatted_root_id = self._format_page_id(root_page_id)
            except ValueError as e:
                error_msg = f"Invalid root page ID for solution {selected_solution.value}: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Create a separate exporter instance for this request
            # This allows concurrent requests to use their own exporters
            request_exporter = NotionPageExporter(
                notion_token=self.notion_token,
                root_page_id=formatted_root_id,
                root_output_dir="repo",
            )

            logger.info(
                f"Using root page ID for {selected_solution.value}: {formatted_root_id}"
            )

            # Get all nodes from the request-specific exporter
            # Run the synchronous get_tree_nodes method in a thread pool to avoid blocking
            try:
                # Use a thread pool to run the synchronous get_tree_nodes method
                # This prevents blocking the event loop for other requests
                nodes = await asyncio.to_thread(request_exporter.get_tree_nodes)

                if not nodes:
                    error_msg = f"No nodes returned for page ID: {formatted_root_id}"
                    logger.error(error_msg)
                    return []
                logger.info(f"Retrieved {len(nodes)} nodes from Notion")
            except Exception as e:
                error_msg = f"Error getting tree nodes: {str(e)}"
                logger.error(error_msg)
                return []

            return nodes

        except Exception as e:
            logger.error(f"Error retrieving manuals from Notion: {str(e)}")
            return []

    async def publish_manual(
        self,
        notion_page_id: str,
        selected_solution: Union[SolutionType, str],
        target_languages: Optional[Set[str]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Publish a manual by exporting it from Notion and translating it.

        Args:
            notion_page_id: The Notion page ID of the selected node to publish
            selected_solution: The solution type (ZCP/APIM/AMDP)
            target_languages: Optional set of target languages for translation
            user_id: Optional user ID to associate with notifications

        Returns:
            str: The job ID for tracking the publication progress

        Raises:
            ValueError: If the notion_page_id is invalid
        """
        # Handle None value for selected_solution
        if selected_solution is None:
            job_id = str(uuid.uuid4())
            self.active_jobs[job_id] = PublishStatus(
                job_id=job_id,
                status=JobState.FAILED,
                message="Solution type cannot be None",
                failure_reason=FailureReason.EXPORT_FAILED,
            )
            return job_id

        # Convert string to SolutionType if needed
        if isinstance(selected_solution, str):
            try:
                selected_solution = SolutionType(selected_solution.lower())
            except ValueError:
                # Handle invalid solution type
                job_id = str(uuid.uuid4())
                self.active_jobs[job_id] = PublishStatus(
                    job_id=job_id,
                    status=JobState.FAILED,
                    message=f"Invalid solution type: {selected_solution}",
                    failure_reason=FailureReason.EXPORT_FAILED,
                )
                return job_id

        # Find the job ID from the active jobs that matches this request
        job_id = None
        for jid, job in self.active_jobs.items():
            if job.status == JobState.STARTED:
                job_id = jid
                break

        if not job_id:
            # If no job found, create a new one (fallback case)
            job_id = str(uuid.uuid4())
            self.active_jobs[job_id] = PublishStatus(
                job_id=job_id,
                status=JobState.STARTED,
                message="Starting publication process",
                progress=0.0,
            )

        # Add a single PROCESSING notification at the start of the publishing process
        self._add_notification(
            type=NotificationType.PROCESSING,
            title=f"Publishing {selected_solution.value.upper()} manual",
            message="Manual publication process has started",
            solution=selected_solution,
            user_id=user_id,
        )

        # Store job context for callbacks
        self._current_job_context = {"job_id": job_id}

        try:
            # Validate and format the notion page ID
            try:
                formatted_page_id = self._format_page_id(notion_page_id)
            except ValueError as e:
                logger.error(f"Invalid notion page ID: {str(e)}")
                job = PublishStatus(
                    job_id=job_id,
                    status=JobState.FAILED,
                    message=f"Invalid notion page ID: {str(e)}",
                    failure_reason=FailureReason.EXPORT_FAILED,
                    progress=0.0,
                )
                self.active_jobs[job_id] = job
                return job_id

            # Check and prepare repository
            self.active_jobs[job_id].status = JobState.CHECKING_REPO
            self.active_jobs[job_id].message = "Checking repository status"

            if not await self._ensure_repository():
                return job_id

            # Clean up old files before export
            try:
                await self._cleanup_old_files(selected_solution)
                logger.info("Cleaned up old files before export")
            except Exception as e:
                logger.error(f"Failed to clean up old files: {str(e)}")
                self.active_jobs[job_id].status = JobState.FAILED
                self.active_jobs[job_id].failure_reason = FailureReason.EXPORT_FAILED
                self.active_jobs[job_id].message = "Failed to clean up old files"
                return job_id

            # Export from Notion
            self.active_jobs[job_id].status = JobState.EXPORTING
            self.active_jobs[job_id].message = "Initializing export from Notion..."
            self.active_jobs[job_id].export_progress = 0.0

            try:
                # Create a new exporter instance for this specific export task
                task_exporter = NotionPageExporter(
                    notion_token=self.notion_token,
                    root_page_id=formatted_page_id,
                    root_output_dir="repo",
                )

                export_path = await asyncio.to_thread(
                    task_exporter.markdownx,  # Use markdownx for MDX file support
                    page_id=formatted_page_id,
                    include_subpages=True,
                    progress_callback=self._export_progress_callback,  # Ensure progress callback is used
                )

                if not export_path or not os.path.exists(export_path):
                    logger.error(
                        f"Export failed: No content was exported for page {formatted_page_id}"
                    )
                    raise ValueError(
                        f"Export failed: No content was exported for page {formatted_page_id}"
                    )

                # Verify the exported files
                self.active_jobs[job_id].message = "Verifying exported files..."
                export_dir = os.path.dirname(export_path)

                # Function to count MDX files
                def count_mdx_files(directory):
                    mdx_count = 0
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if file.endswith(".mdx"):
                                mdx_count += 1
                                logger.info(
                                    f"Found MDX file: {os.path.join(root, file)}"
                                )
                    return mdx_count

                if os.path.exists(export_dir):
                    source_dir = os.path.join(
                        self.repo_path, self.source_dir, selected_solution.value.lower()
                    )
                    # Run file counting in a separate thread to avoid blocking
                    mdx_files = await asyncio.to_thread(count_mdx_files, source_dir)

                export_success = True
                # Calculate total files (export files + translation files)
                target_lang_count = len(target_languages or self.target_languages)
                total_files = mdx_files * (
                    1 + target_lang_count
                )  # Original + translations

                # Update job status with file counts
                self.active_jobs[job_id].total_files = total_files
                self.active_jobs[
                    job_id
                ].export_files = mdx_files  # Store original export files count
                self.active_jobs[
                    job_id
                ].processed_files = mdx_files  # Start with exported files
                self.active_jobs[job_id].export_progress = 100.0
                self.active_jobs[job_id].total_progress = (
                    mdx_files / total_files
                ) * 100
                self.active_jobs[
                    job_id
                ].message = f"Successfully exported {mdx_files} MDX files"
                logger.info(
                    f"Successfully exported {mdx_files} MDX files (Total files to process: {total_files})"
                )
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                export_success = False

            if not export_success:
                self.active_jobs[job_id].status = JobState.FAILED
                self.active_jobs[job_id].failure_reason = FailureReason.EXPORT_FAILED
                self.active_jobs[job_id].message = "Export failed"
                return job_id

            # Commit export changes
            if not await self._commit_export_changes(
                "Update documentation from Notion"
            ):
                return job_id

            # Translate content
            self.active_jobs[job_id].status = JobState.TRANSLATING
            self.active_jobs[job_id].message = "Starting translation"

            # Use the solution-specific source directory (lowercase)
            source_dir = os.path.join(
                self.repo_path, self.source_dir, selected_solution.value.lower()
            )
            logger.info(f"Using source directory for translation: {source_dir}")

            # Call translator with the source directory
            translation_success = await self.translate_repository(
                source_path=source_dir,  # Use solution-specific source directory
                target_dir=os.path.join(self.repo_path, self.target_dir),
                target_languages=target_languages or self.target_languages,
                selected_solution=selected_solution.value,
                job_id=job_id,
            )

            if not translation_success:
                self.active_jobs[job_id].status = JobState.FAILED
                self.active_jobs[
                    job_id
                ].failure_reason = FailureReason.TRANSLATION_FAILED
                self.active_jobs[job_id].message = "Translation failed"
                return job_id

            # Commit translation changes
            if not await self._commit_translation_changes("Update translations"):
                return job_id

            # Push all changes
            if not await self._push_changes():
                return job_id

            # Update final status and add notification
            job = self.active_jobs[job_id]
            job.update_status(
                status=JobState.COMPLETED,
                message="Publication completed successfully",
                total_progress=100.0,
            )

            # Add success notification with user_id
            self._add_notification(
                type=NotificationType.SUCCESS,
                title=f"{selected_solution.value.upper()} manual has been published",
                message="Manual has been successfully exported and translated",
                solution=selected_solution,
                user_id=user_id,
            )

            logger.info(f"Publication completed successfully for job {job_id}")

        except Exception as e:
            logger.error(f"Error during publication: {str(e)}")
            job = self.active_jobs[job_id]
            job.update_status(
                status=JobState.FAILED,
                message=f"Publication failed: {str(e)}",
                total_progress=0.0,
            )

            # Add error notification with user_id
            self._add_notification(
                type=NotificationType.ERROR,
                title=f"{selected_solution.value.upper()} manual publishing was failed",
                message=str(e),
                solution=selected_solution,
                user_id=user_id,
            )

        finally:
            # Clean up job context
            if hasattr(self, "_current_job_context"):
                del self._current_job_context

        return job_id

    async def get_job_status(self, job_id: str) -> Optional[PublishStatus]:
        """Get the status of a publishing job.

        Args:
            job_id: The ID of the job to check

        Returns:
            Optional[PublishStatus]: The job status if found, None otherwise
        """
        return self.active_jobs.get(job_id)

    async def _cleanup_old_files(self, selected_solution: SolutionType) -> None:
        """Clean up old files before export.

        Args:
            selected_solution: The solution type being processed
        """
        try:
            # Define a function to perform file cleanup operations
            def cleanup_directory(directory):
                if not os.path.exists(directory):
                    return

                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        import shutil

                        shutil.rmtree(item_path)
                logger.info(f"Cleaned up directory: {directory}")

            # Clean up source directory
            source_dir = os.path.join(
                self.repo_path, self.source_dir, selected_solution.value.lower()
            )
            await asyncio.to_thread(cleanup_directory, source_dir)

            # Clean up static image directory for the specific solution
            static_img_dir = os.path.join(
                self.repo_path, "static", "img", selected_solution.value.lower()
            )
            await asyncio.to_thread(cleanup_directory, static_img_dir)

            # Clean up target directories for each language
            for lang in self.target_languages:
                target_dir = os.path.join(
                    self.repo_path,
                    self.target_dir,
                    lang,
                    f"docusaurus-plugin-content-docs-{selected_solution.value.lower()}",
                    "current",
                )
                await asyncio.to_thread(cleanup_directory, target_dir)

        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
            raise

    async def _ensure_repository(self) -> bool:
        """Ensure repository exists and is up to date.
        Returns True if successful, False otherwise."""
        try:
            repo_path = Path(self.repo_path)
            should_clone = False

            # Function to check if a directory is a valid git repository
            def is_valid_git_repo(path):
                try:
                    git.Repo(path)
                    return True
                except git.exc.InvalidGitRepositoryError:
                    return False

            # Check if directory exists and is not empty
            if not repo_path.exists():
                should_clone = True
            else:
                # Check if directory is empty
                if not any(repo_path.iterdir()):
                    should_clone = True
                else:
                    # Check if it's a valid git repository (potentially blocking operation)
                    try:
                        is_valid = await asyncio.to_thread(is_valid_git_repo, repo_path)
                        if not is_valid:
                            should_clone = True
                    except Exception:
                        should_clone = True

            if should_clone:
                # Update job status for cloning
                if hasattr(self, "_current_job_context"):
                    job_id = self._current_job_context["job_id"]
                    if job_id in self.active_jobs:
                        current_job = self.active_jobs[job_id]
                        # Create a dictionary of current values excluding the ones we want to update
                        current_values = current_job.model_dump()
                        current_values.update(
                            {
                                "status": JobState.CLONING,
                                "message": f"Cloning repository from {self.github_repo_url}",
                            }
                        )
                        updated_job = PublishStatus(**current_values)
                        self.active_jobs[job_id] = updated_job

                logger.info(f"Cloning repository from {self.github_repo_url}")

                # Remove directory if it exists but is empty or not a valid repo
                if repo_path.exists():
                    import shutil

                    await asyncio.to_thread(shutil.rmtree, repo_path)

                # Clone the entire repository without modifying anything (blocking operation)
                await asyncio.to_thread(
                    git.Repo.clone_from, self.github_repo_url, repo_path
                )

                # Only ensure our working directories exist without affecting others
                work_dirs = [
                    os.path.join(self.repo_path, self.source_dir),
                    os.path.join(self.repo_path, self.target_dir),
                ]

                # Create directories in a non-blocking way
                for directory in work_dirs:
                    if not os.path.exists(directory):
                        await asyncio.to_thread(os.makedirs, directory, exist_ok=True)
                        logger.info(f"Created working directory: {directory}")

                return True

            # If we don't need to clone, update existing repository
            # Update job status for pulling
            if hasattr(self, "_current_job_context"):
                job_id = self._current_job_context["job_id"]
                if job_id in self.active_jobs:
                    current_job = self.active_jobs[job_id]
                    # Create a dictionary of current values excluding the ones we want to update
                    current_values = current_job.model_dump()
                    current_values.update(
                        {
                            "status": JobState.PULLING,
                            "message": "Updating repository (git pull)",
                        }
                    )
                    updated_job = PublishStatus(**current_values)
                    self.active_jobs[job_id] = updated_job

            logger.info("Repository exists, checking develop branch")

            # Function to update the repository
            def update_repo():
                try:
                    repo = git.Repo(repo_path)
                    origin = repo.remotes.origin

                    # Fetch all branches first (required for proper reference handling)
                    logger.info("Fetching branches")
                    origin.fetch()

                    # Check if develop branch exists in remote
                    remote_refs = [ref.name for ref in repo.refs]
                    remote_develop_exists = "origin/develop" in remote_refs

                    # If remote develop doesn't exist, try to create it from main/master
                    if not remote_develop_exists:
                        # Check if main or master exists in remote
                        if "origin/main" in remote_refs:
                            base_branch = "main"
                        elif "origin/master" in remote_refs:
                            base_branch = "master"
                        else:
                            logger.error(
                                "Neither develop, main, nor master branch exists in remote"
                            )
                            raise ValueError("No valid base branch found in remote")

                        # Create and push develop branch from base branch
                        logger.info(f"Creating develop branch from {base_branch}")
                        repo.git.checkout("-b", "develop", f"origin/{base_branch}")
                        repo.git.push("--set-upstream", "origin", "develop")
                        remote_develop_exists = True

                    # Now handle local develop branch
                    if "develop" not in repo.heads:
                        # Create local develop branch tracking remote develop
                        logger.info(
                            "Creating local develop branch tracking origin/develop"
                        )
                        develop = repo.create_head("develop", "origin/develop")
                        develop.set_tracking_branch(origin.refs.develop)
                    else:
                        develop = repo.heads["develop"]
                        # Ensure local develop is tracking remote develop
                        if (
                            not develop.tracking_branch()
                            or develop.tracking_branch().name != "origin/develop"
                        ):
                            develop.set_tracking_branch(origin.refs.develop)

                    # Switch to develop branch if not already on it
                    if repo.active_branch.name != "develop":
                        logger.info("Switching to develop branch")
                        develop.checkout()

                    # Reset local branch to match remote if they're out of sync
                    logger.info("Synchronizing with remote develop branch")
                    repo.git.reset("--hard", "origin/develop")

                    # Pull latest changes
                    logger.info("Pulling latest changes from develop branch")
                    repo.git.pull("origin", "develop")

                    return True
                except git.exc.GitCommandError as e:
                    logger.error(f"Git command failed: {str(e)}")
                    raise e

            # Run update_repo in a thread to avoid blocking
            try:
                return await asyncio.to_thread(update_repo)
            except Exception as e:
                logger.error(f"Repository operation failed: {str(e)}")
                if hasattr(self, "_current_job_context"):
                    job = self.active_jobs[self._current_job_context["job_id"]]
                    job.status = JobState.FAILED
                    job.failure_reason = FailureReason.GIT_OPERATION_FAILED
                    job.message = f"Repository operation failed: {str(e)}"
                return False

        except Exception as e:
            logger.error(f"Repository operation failed: {str(e)}")
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.FAILED
                job.failure_reason = FailureReason.REPO_ACCESS
                job.message = f"Repository operation failed: {str(e)}"
            return False

    async def _commit_export_changes(self, message: str) -> bool:
        """Commit changes after export phase."""
        try:
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.EXPORT_COMMIT
                job.message = "Committing exported files"

            # Define a function to perform all git operations in a thread
            def perform_git_operations():
                repo = git.Repo(self.repo_path)

                # Ensure we're on develop branch
                if repo.active_branch.name != "develop":
                    logger.error("Not on develop branch")
                    raise ValueError("Not on develop branch")

                # Add both documentation and static files
                repo.git.add(os.path.join(self.source_dir, "*"))
                repo.git.add("static")  # Add the entire static directory

                # Check if there are any changes to commit
                if repo.is_dirty(untracked_files=True):
                    repo.index.commit(f"docs: {message}")
                    logger.info("Committed changes to documentation and static files")
                else:
                    logger.info("No changes to commit")

                return True

            # Run git operations in a thread pool
            return await asyncio.to_thread(perform_git_operations)

        except Exception as e:
            logger.error(f"Failed to commit export changes: {str(e)}")
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.FAILED
                job.failure_reason = FailureReason.GIT_OPERATION_FAILED
                job.message = f"Failed to commit export changes: {str(e)}"
            return False

    async def _commit_translation_changes(self, message: str) -> bool:
        """Commit changes after translation phase."""
        try:
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.TRANSLATION_COMMIT
                job.message = "Committing translated files"

            # Define a function to perform all git operations in a thread
            def perform_git_operations():
                repo = git.Repo(self.repo_path)

                # Ensure we're on develop branch
                if repo.active_branch.name != "develop":
                    logger.error("Not on develop branch")
                    raise ValueError("Not on develop branch")

                repo.git.add(os.path.join(self.target_dir, "*"))
                repo.index.commit(f"i18n: {message}")
                return True

            # Run git operations in a thread pool
            return await asyncio.to_thread(perform_git_operations)

        except Exception as e:
            logger.error(f"Failed to commit translation changes: {str(e)}")
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.FAILED
                job.failure_reason = FailureReason.GIT_OPERATION_FAILED
                job.message = f"Failed to commit translation changes: {str(e)}"
            return False

    async def _push_changes(self) -> bool:
        """Push all changes to remote repository."""
        try:
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.PUSHING
                job.message = "Pushing changes to remote repository"

            # Define a function to perform all git operations in a thread
            def perform_git_operations():
                repo = git.Repo(self.repo_path)

                # Ensure we're on develop branch
                if repo.active_branch.name != "develop":
                    logger.error("Not on develop branch")
                    raise ValueError("Not on develop branch")

                # Push specifically to develop branch using git command
                logger.info("Pushing changes to develop branch")
                repo.git.push("origin", "develop")
                return True

            # Run git operations in a thread pool
            return await asyncio.to_thread(perform_git_operations)

        except Exception as e:
            logger.error(f"Failed to push changes: {str(e)}")
            if hasattr(self, "_current_job_context"):
                job = self.active_jobs[self._current_job_context["job_id"]]
                job.status = JobState.FAILED
                job.failure_reason = FailureReason.GIT_OPERATION_FAILED
                job.message = f"Failed to push changes: {str(e)}"
            return False

    def _create_export_progress_callback(self):
        """Create a progress callback for the export process."""

        def progress_callback(current: int, total: int, message: str = None):
            if hasattr(self, "_current_job_context"):
                job_id = self._current_job_context["job_id"]
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    if total > 0:
                        # Calculate progress percentage
                        progress_percentage = round((current / total) * 100, 1)
                        job.export_progress = progress_percentage

                        # Update both export_files and processed_files during export
                        job.export_files = current
                        job.processed_files = current

                        # Format the message with progress
                        job.message = f"{progress_percentage:.1f}%({current}/{total}) - {message if message else f'Exporting page {current}'}"

                        # Update total progress if we have total_files
                        if job.total_files > 0:
                            job.total_progress = round((current / total) * 100, 1)

                        logger.info(job.message)

        return progress_callback

    async def translate_repository(
        self,
        source_path: str,
        target_dir: str | None,
        target_languages: list[str],
        selected_solution: str | None = None,
        job_id: str | None = None,
    ) -> bool:
        """Translate repository content to target languages.

        Args:
            source_path (str): Path to the source content (corresponds to selected Notion page)
            target_dir (str | None): Target directory for translations
            target_languages (list[str]): List of target languages to translate to
            selected_solution (str | None, optional): Selected solution type (ZCP, APIM, AMDP)
            job_id (str | None, optional): Current job ID for tracking progress

        Returns:
            bool: True if translation was successful, False otherwise

        Raises:
            ValueError: If source_path or target_languages is invalid
            NotionError: If there's an error accessing Notion content
        """
        if not source_path or not target_languages:
            raise ValueError("Source path and target languages must be provided")

        # Get the solution type enum from string
        solution = (
            SolutionType(selected_solution.lower()) if selected_solution else None
        )
        if not solution:
            raise ValueError(f"Invalid solution type: {selected_solution}")

        try:
            # Get the manual structure to find the correct page
            manuals = await self.get_manuals(solution)

            # Find the manual/folder with matching path
            selected_node = self._find_node_by_path(manuals, source_path)
            if not selected_node:
                raise ValueError(f"Could not find page with path: {source_path}")

            # Set up the target directory
            if target_dir is None:
                target_dir = "i18n"

            # Create a dedicated exporter for this translation task
            task_exporter = NotionPageExporter(
                notion_token=self.notion_token,
                root_page_id=selected_node.notion_page_id,
                root_output_dir="repo",
            )

            # Export the selected page and its children
            await asyncio.to_thread(
                task_exporter.markdownx,
                selected_node.notion_page_id,
                self.repo_path,
                self.source_dir,
                format="markdownx",
                include_subpages=True,
            )

            # Create a job-specific translator instance with appropriate callback
            translation_progress_callback = None
            if job_id and job_id in self.active_jobs:
                translation_progress_callback = (
                    self._create_translation_progress_callback(job_id)
                )

            # Create a dedicated translator for this task
            task_translator = MarkdownTranslator(
                progress_callback=translation_progress_callback
            )

            # Translate the exported content
            # The translator will handle the solution-specific directory structure
            result = await task_translator.translate_repository(
                source_path=os.path.join(
                    self.repo_path, self.source_dir
                ),  # Use source_dir directly
                target_dir=os.path.join(self.repo_path, target_dir),
                target_languages=target_languages,
                selected_solution=solution.value,
            )

            # Check if translation was successful
            if (
                result
                and hasattr(result, "status")
                and result.status.value == "completed"
            ):
                return True
            else:
                logger.error(
                    f"Translation failed: {getattr(result, 'message', 'Unknown error')}"
                )
                return False

        except Exception as e:
            logger.exception(f"Error during translation: {str(e)}")
            return False

    def _find_node_by_path(
        self, nodes: list[Union[Manual, Folder]], target_path: str
    ) -> Union[Manual, Folder, None]:
        """Find a node (Manual or Folder) by its path in the manual structure.

        Args:
            nodes (list[Union[Manual, Folder]]): List of nodes to search
            target_path (str): Target path to find

        Returns:
            Union[Manual, Folder, None]: Found node or None if not found
        """
        for node in nodes:
            if isinstance(node, Manual):
                if node.path == target_path:
                    return node
            elif isinstance(node, Folder):
                # For folders, check children recursively
                if node.children:
                    found = self._find_node_by_path(node.children, target_path)
                    if found:
                        return found
        return None

    def _add_notification(
        self,
        type: NotificationType,
        title: str,
        message: str,
        solution: Optional[SolutionType] = None,
        user_id: Optional[str] = None,
    ):
        """Add a new notification."""
        notification = Notification(
            type=type,
            title=title,
            message=message,
            solution=solution,
            user_id=user_id,
        )
        self.notifications.append(notification)
        logger.info(
            f"Added notification: {notification.title} - {notification.message} for user: {user_id if user_id else 'all'}"
        )

        # Broadcast to all registered clients
        asyncio.create_task(self._broadcast_notification(notification))

        return notification

    async def _broadcast_notification(self, notification: Notification):
        """Broadcast a notification to all registered clients.

        Args:
            notification: The notification to broadcast
        """
        # Create a copy of the clients to avoid modification during iteration
        clients = list(self.notification_clients.items())

        for client_id, (queue, user_id) in clients:
            # Only send to clients with matching user_id or if notification has no user_id
            if (
                notification.user_id is None
                or user_id is None
                or notification.user_id == user_id
            ):
                try:
                    # Non-blocking put with a timeout
                    await asyncio.wait_for(queue.put(notification), timeout=1.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout broadcasting to client {client_id}")
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                    # Remove client on error
                    await self.unregister_notification_client(client_id)

    async def register_notification_client(
        self, queue: asyncio.Queue, user_id: Optional[str] = None
    ) -> str:
        """Register a new client for notification streaming.

        Args:
            queue: An asyncio Queue where notifications will be sent
            user_id: Optional user ID to filter notifications

        Returns:
            A unique client ID that can be used to unregister
        """
        client_id = str(uuid.uuid4())
        self.notification_clients[client_id] = (queue, user_id)
        logger.info(f"Registered notification client {client_id} for user {user_id}")
        return client_id

    async def unregister_notification_client(self, client_id: str) -> bool:
        """Unregister a client from notification streaming.

        Args:
            client_id: The client ID to unregister

        Returns:
            True if the client was unregistered, False if not found
        """
        if client_id in self.notification_clients:
            queue, _ = self.notification_clients.pop(client_id)
            # Signal to the client that it should stop listening
            try:
                await queue.put(None)
            except Exception:
                pass  # Ignore errors when client is already gone

            logger.info(f"Unregistered notification client {client_id}")
            return True
        return False

    async def unregister_all_clients(self):
        """Unregister all notification clients."""
        client_ids = list(self.notification_clients.keys())
        for client_id in client_ids:
            await self.unregister_notification_client(client_id)

        logger.info(f"Unregistered all {len(client_ids)} notification clients")

    async def get_notifications(
        self,
        limit: int = 50,
        include_read: bool = False,
        user_id: Optional[str] = None,
        latest_only: bool = False,
    ) -> Union[List[Notification], Optional[Notification]]:
        """Get recent notifications.

        Args:
            limit: Maximum number of notifications to return
            include_read: Whether to include read notifications
            user_id: Filter notifications by user_id
            latest_only: If True, return only the latest notification as a single object

        Returns:
            Either a list of notifications or a single latest notification (if latest_only=True)
        """
        # Filter by read status and user_id
        filtered = [
            n
            for n in self.notifications
            if (include_read or not n.is_read)
            and (user_id is None or n.user_id == user_id or n.user_id is None)
        ]

        # Sort by creation time (newest first)
        sorted_notifications = sorted(
            filtered, key=lambda x: x.created_at, reverse=True
        )

        # Return only the latest notification if requested
        if latest_only and sorted_notifications:
            return sorted_notifications[0]
        elif latest_only:
            return None

        # Otherwise return a list limited by the limit parameter
        return sorted_notifications[:limit]

    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.is_read = True
                return True
        return False

    async def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.notifications = []
