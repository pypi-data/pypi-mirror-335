from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Union, Set, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class SolutionType(str, Enum):
    ZCP = "zcp"
    APIM = "apim"
    AMDP = "amdp"


class ItemType(str, Enum):
    MANUAL = "manual"
    FOLDER = "folder"


class JobState(str, Enum):
    """States that match the flow diagram exactly"""

    STARTED = "started"
    CHECKING_REPO = "checking_repo"
    CLONING = "cloning"
    PULLING = "pulling"
    EXPORTING = "exporting"
    EXPORT_COMMIT = "export_commit"
    TRANSLATING = "translating"
    TRANSLATION_COMMIT = "translation_commit"
    PUSHING = "pushing"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureReason(str, Enum):
    """Specific failure reasons matching diagram decision points"""

    REPO_ACCESS = "repository_access_failed"
    EXPORT_FAILED = "export_failed"
    TRANSLATION_FAILED = "translation_failed"
    GIT_OPERATION_FAILED = "git_operation_failed"


class ManualBase(BaseModel):
    id: str
    title: str
    type: ItemType
    parent_id: Optional[str] = None
    notion_page_id: Optional[str] = None  # Add Notion page ID


class Manual(ManualBase):
    notion_url: HttpUrl
    path: str
    source_language: Optional[str] = "en"


class Folder(ManualBase):
    children: List[Union["Manual", "Folder"]] = []


# New model for Node objects from the exporter
class NodeModel(BaseModel):
    """Pydantic model that maps to Node objects from the exporter."""

    object_id: str
    title: str
    # These fields are optional to accommodate both manual and folder nodes
    parent_id: Optional[str] = None
    children: Optional[List["NodeModel"]] = None
    notion_url: Optional[str] = None
    path: Optional[str] = None

    # Allow extra fields from Node objects
    class Config:
        extra = "allow"


# New response model for the API
class NodeList(BaseModel):
    """API response model that works with Node objects directly."""

    items: List[NodeModel]


class PublishRequest(BaseModel):
    """Request model for publishing a manual.
    When user selects a node from the tree view and clicks publish,
    the frontend will send:
    - notion_page_id: The Notion page ID of the selected node
    - selected_solution: The solution type (ZCP/APIM/AMDP)
    - target_languages: Optional list of target languages for translation
    """

    notion_page_id: str  # Changed from root_page_id to notion_page_id to match frontend
    selected_solution: SolutionType
    target_languages: Optional[Set[str]] = None  # If None, use all configured languages


class PublishStatus(BaseModel):
    """Status of a manual publishing job."""

    job_id: str
    status: JobState
    message: str
    total_progress: float = 0.0  # Overall progress (0-100)
    failure_reason: Optional[FailureReason] = None
    export_progress: float = 0.0  # Export progress (0-100)
    translation_progress: float = 0.0  # Translation progress (0-100)
    total_files: int = 0  # Total number of files to process
    processed_files: int = 0  # Number of files processed
    export_files: int = 0  # Number of files exported from Notion

    def update_status(
        self, status: JobState, message: str, total_progress: Optional[float] = None
    ):
        """Update status while preserving progress values."""
        self.status = status
        self.message = message
        if total_progress is not None:
            self.total_progress = total_progress

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "message": self.message,
            "total_progress": self.total_progress,
            "failure_reason": self.failure_reason.value
            if self.failure_reason
            else None,
            "export_progress": self.export_progress,
            "translation_progress": self.translation_progress,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "export_files": self.export_files,
        }


class ManualList(BaseModel):
    items: List[Union[Manual, Folder]]


class NotificationType(str, Enum):
    """Types of notifications"""

    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    PROCESSING = "processing"


class Notification(BaseModel):
    """Model for notifications shown in the UI."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    title: str
    message: str
    solution: Optional[SolutionType] = None
    user_id: Optional[str] = (
        None  # Add user_id to associate notifications with specific users
    )
    created_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "solution": self.solution.value if self.solution else None,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
        }


class SidebarMenuItem(BaseModel):
    """Model for a sidebar menu item."""

    name: str
    solution_type: SolutionType
    root_page_id: str


class SidebarMenu(BaseModel):
    """Model for the sidebar menu response."""

    solutions: List[SidebarMenuItem]


# This is needed for the forward reference in Folder
Manual.model_rebuild()
Folder.model_rebuild()
NodeModel.model_rebuild()  # For the self-reference in children
