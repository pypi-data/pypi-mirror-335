# ZMP Manual Backend

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-manual_backend-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)

A high-performance backend service for managing manual content from Notion to Docusaurus. Supports real-time progress tracking, multiple language translations, and automated publishing workflows.

## Features

- Exports Notion pages to Markdown/MDX format
- Preserves document structure and formatting
- Supports multiple target languages simultaneously
- Real-time progress tracking with Server-Sent Events
- Automated translation integration
- User-specific notification system for export status
- Docusaurus-compatible output structure
- Job management and monitoring
- Secure authentication with JWT tokens

## API Endpoints

### Authentication

```plaintext
POST /auth/login
- Authenticate user and get access token
- Request body: {"username": "string", "password": "string"}
- Response: {"access_token": "string", "token_type": "bearer"}
```

All other API endpoints require authentication via the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Sidebar

```plaintext
GET /sidebar
- Get information about all available solutions
- Response: {"solutions": [{"name": "string", "solution_type": "string", "root_page_id": "string"}]}
```

### Manual Service

```plaintext
GET /manuals
- Get hierarchical list of manuals and folders
- Optional query param: ?selected_solution=zcp

POST /publish
- Publish a manual by exporting from Notion and translating
- Request body: {
    "notion_page_id": "string",
    "selected_solution": "string",
    "target_languages": ["string"]
  }
- Response: {"job_id": "string"}

GET /watch/{job_id}
- Watch publication progress using Server-Sent Events
- Returns real-time status updates

GET /jobs/{job_id}
- Get current status of a publication job

GET /jobs
- List recent publication jobs
- Query params:
  - status: Filter by job status
  - limit: Number of jobs to return (1-100)
```

### Notifications

```plaintext
GET /notifications
- Get recent notifications for the authenticated user
- User ID is automatically extracted from the authentication token
- Query params:
  - limit: Number of notifications (1-100)
  - include_read: Include read notifications

GET /notifications/latest
- Get only the most recent notification for the authenticated user
- User ID is automatically extracted from the authentication token
- Query params:
  - include_read: Include read notifications

GET /notifications/stream
- Stream notifications in real-time using Server-Sent Events (SSE)
- Establishes a persistent connection for receiving notifications as they happen
- User ID is automatically extracted from the authentication token
- Query params:
  - include_read: Include read notifications
- Returns: SSE stream with notification JSON data

POST /notifications/{notification_id}/read
- Mark a notification as read

POST /notifications/clear
- Clear all notifications
```

## Real-Time Notifications with Server-Sent Events (SSE)

The system provides real-time notifications using Server-Sent Events (SSE), allowing clients to receive notifications as they happen without polling the server.

### SSE Notification Endpoint

```plaintext
GET /notifications/stream
```

This endpoint establishes a persistent connection with the client using SSE. The server will push notifications to the client as they are created.

**Query Parameters:**
- `include_read` (boolean, default: false): Whether to include notifications that have been marked as read.

**Authentication:**
- Requires a valid JWT token in the Authorization header.

**Response:**
- A stream of SSE events, each containing a JSON-serialized notification.
- Each event follows the SSE format: `data: {...JSON notification data...}`

### Client Implementation Examples

#### JavaScript Example

```javascript
// Create and configure EventSource for SSE
const token = "YOUR_JWT_TOKEN";
const eventSource = new EventSource("/notifications/stream", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});

// Handle incoming notifications
eventSource.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log("Received notification:", notification);
  // Handle notification (display in UI, etc.)
};

// Handle connection open
eventSource.onopen = function() {
  console.log("SSE connection established");
};

// Handle errors
eventSource.onerror = function(error) {
  console.error("SSE connection error:", error);
  // Optionally reconnect or report error to user
};

// Close connection when done
function closeConnection() {
  eventSource.close();
}
```

#### Python Example

```python
import asyncio
import aiohttp
import json

async def listen_for_notifications(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://localhost:8000/notifications/stream"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to connect: {response.status}")
                return

            async for line in response.content:
                line = line.decode('utf-8').strip()

                # Parse SSE format: "data: {json}"
                if line.startswith('data: '):
                    data = line[6:]  # Remove "data: " prefix
                    notification = json.loads(data)
                    # Handle notification
                    print(f"New notification: {notification['title']}")
```

### Best Practices for SSE Usage

1. **Always close the connection** when a client no longer needs notifications to free up server resources.
2. **Implement error handling and reconnection logic** in client applications to maintain stable connections.
3. **Use the query parameters** to filter notifications appropriately and reduce unnecessary network traffic.
4. **Consider implementing a maximum connection time** for long-lived connections to prevent resource exhaustion.

## Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in your project root:

```env
# Notion Configuration
NOTION_TOKEN=your-notion-token-here
ZCP_ROOT_PAGE_ID=your-root-page-id
APIM_ROOT_PAGE_ID=your-apim-root-page-id
AMDP_ROOT_PAGE_ID=your-amdp-root-page-id

# Repository Configuration
REPO_BASE_PATH=./repo
SOURCE_DIR=docs
TARGET_DIR=i18n
GITHUB_REPO_URL=your-github-repo-url

# Translation Configuration
TARGET_LANGUAGES=ko,ja,zh

# Authentication Configuration
JWT_SECRET_KEY=your-secret-key-keep-it-secure
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENABLE_KEYCLOAK=False
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Quick start using run.sh (recommended)
chmod +x run.sh  # Make script executable (first time only)
./run.sh        # Starts server on port 8001 with auto-reload and debug logging

# Manual server start options
poetry run uvicorn zmp_manual_backend.main:app --reload
poetry run uvicorn zmp_manual_backend.main:app --reload --host 0.0.0.0 --port 8001
```

The `run.sh` script automatically:
- Checks if port 8001 is in use and frees it if needed
- Starts the FastAPI server with:
  - Host: 0.0.0.0 (accessible from other machines)
  - Port: 8001
  - Auto-reload enabled
  - Debug logging enabled

## Authentication

The application uses JWT (JSON Web Tokens) for authentication. All API endpoints (except `/auth/login`) require a valid JWT token in the Authorization header.

The token contains information about the user, including:
- Username
- Roles
- Email
- Full name

This user information is used to filter certain resources, such as notifications, to ensure users only see content that is relevant to them.

## User-Specific Notifications

Notifications can be:
1. **System-wide**: Visible to all users (no user_id specified)
2. **User-specific**: Visible only to a specific user

When retrieving notifications through the `/notifications` or `/notifications/latest` endpoints, the system automatically filters the results based on the user's identity from the authentication token.

## Directory Structure

The service creates a Docusaurus-compatible directory structure:

```
repo/
├── docs/
│   └── [solution]/
│       └── content.mdx
└── i18n/
    ├── ko/
    │   └── docusaurus-plugin-content-docs/
    │       └── current/
    │           └── [solution]/
    │               └── content.mdx
    ├── ja/
    │   └── ...
    └── zh/
        └── ...
```

## Job States

Publication jobs follow a specific workflow with the following states:

| State | Description |
|-------|-------------|
| STARTED | Job has been initiated |
| CHECKING_REPO | Verifying repository access and status |
| CLONING | Cloning the repository if not exists |
| PULLING | Pulling latest changes from repository |
| EXPORTING | Exporting content from Notion |
| EXPORT_COMMIT | Committing exported content |
| TRANSLATING | Translating content to target languages |
| TRANSLATION_COMMIT | Committing translated content |
| PUSHING | Pushing changes to repository |
| COMPLETED | Successfully finished |
| FAILED | Failed to complete |

### Failure Reasons

When a job fails, it can have one of these specific failure reasons:

| Reason | Description |
|--------|-------------|
| REPO_ACCESS | Failed to access or authenticate with the repository |
| EXPORT_FAILED | Failed to export content from Notion |
| TRANSLATION_FAILED | Failed during content translation |
| GIT_OPERATION_FAILED | Failed during a git operation |

## Notification Types

The service provides three types of notifications:

| Type | Description |
|------|-------------|
| SUCCESS | Successful operation notifications |
| ERROR | Error and failure notifications |
| INFO | General information notifications |
| PROCESSING | In-progress operation notifications |

Each notification includes:
- Unique ID
- Type (success/error/info/processing)
- Title
- Message
- Associated solution (optional)
- User ID (optional, for user-specific notifications)
- Creation timestamp
- Read status

## Solution Types

The service supports the following solution types:

| Type | Description |
|------|-------------|
| ZCP | Cloud Z CP Documentation |
| APIM | API Management Documentation |
| AMDP | Application Modernization Documentation |

## Supported Languages

The following language codes are supported:

| Code | Language    |
|------|------------|
| ko   | Korean     |
| fr   | French     |
| ja   | Japanese   |
| es   | Spanish    |
| de   | German     |
| zh   | Chinese    |
| ru   | Russian    |
| it   | Italian    |
| pt   | Portuguese |
| ar   | Arabic     |

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Docker Deployment

For detailed instructions on building a Docker image and deploying to a Kubernetes cluster, see the [Kubernetes Deployment Guide](k8s/README_DEPLOYMENT.md).

Quick start:

1. Build and push the Docker image:
   ```bash
   ./k8s/build-and-push.sh
   ```

2. Deploy the application:
   ```bash
   ./k8s/deploy-app.sh
   ```
