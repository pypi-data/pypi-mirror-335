from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from zmp_manual_backend.api.manual_router import router as manual_router
from zmp_manual_backend.api.auth_router import router as auth_router
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from logging.config import fileConfig
from typing import Dict
from fastapi import APIRouter

# Try to import and initialize KeyCloak
try:
    from zmp_manual_backend.api.oauth2_keycloak import initialize_keycloak

    KEYCLOAK_ENABLED = os.environ.get("ENABLE_KEYCLOAK", "").lower() == "true"
except ImportError:
    initialize_keycloak = None
    KEYCLOAK_ENABLED = False

# Load environment variables from the project root directory
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"

# Parse VSCODE_ENV_REPLACE for environment variables
vscode_env = os.environ.get("VSCODE_ENV_REPLACE", "")
if vscode_env:
    # Split by : and parse each key=value pair
    env_pairs = vscode_env.split(":")
    for pair in env_pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            # Only set if the value is not empty
            if value:
                os.environ[key] = value.replace("\\x3a", ":")  # Fix escaped colons

# Load .env file as fallback
load_dotenv(dotenv_path=env_path)

# Configure logging with absolute path
logging_conf_path = os.path.join(os.path.dirname(__file__), "..", "logging.conf")
if os.path.exists(logging_conf_path):
    fileConfig(logging_conf_path)
else:
    logging.basicConfig(level=logging.INFO)
    logging.warning(
        f"Logging config not found at {logging_conf_path}, using basic configuration"
    )

logger = logging.getLogger("appLogger")


def get_env_settings() -> Dict[str, str]:
    """Get environment settings with validation"""
    settings = {
        "HOST": os.environ.get("HOST", "0.0.0.0"),
        "PORT": os.environ.get("PORT", "8000"),
        "REPO_BASE_PATH": os.environ.get("REPO_BASE_PATH", "./repo"),
        "SOURCE_DIR": os.environ.get("SOURCE_DIR", "docs"),
        "TARGET_DIR": os.environ.get("TARGET_DIR", "i18n"),
        "DEBUG": os.environ.get("DEBUG", "True"),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "info"),
        "ALLOWED_ORIGINS": os.environ.get("ALLOWED_ORIGINS", "*"),
        "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", ""),
        "ENABLE_KEYCLOAK": os.environ.get("ENABLE_KEYCLOAK", "False"),
    }

    return settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup
        logger.info("Starting ZMP Manual Backend service")
        settings = get_env_settings()

        # Log configuration
        logger.info("Server configuration:")
        for key, value in settings.items():
            # Don't log sensitive values
            if key in ["JWT_SECRET_KEY"]:
                logger.info(f"- {key}: {'*' * 8 if value else 'Not set'}")
            else:
                logger.info(f"- {key}: {value}")

        # Log environment variables status
        logger.info("Environment variables status:")
        logger.info(f"- .env file location: {env_path}")
        logger.info(f"- .env file exists: {env_path.exists()}")
        logger.info(
            f"- NOTION_TOKEN set: {'Yes' if os.environ.get('NOTION_TOKEN') else 'No'}"
        )

        # Log root page IDs for all solutions
        for solution in ["ZCP", "APIM", "AMDP"]:
            env_var = f"{solution}_ROOT_PAGE_ID"
            logger.info(
                f"- {env_var} set: {'Yes' if os.environ.get(env_var) else 'No'}"
            )

        # Initialize KeyCloak if enabled and the module was loaded
        if KEYCLOAK_ENABLED and initialize_keycloak:
            logger.info("Initializing KeyCloak authentication...")
            keycloak_success = initialize_keycloak()
            if keycloak_success:
                logger.info("KeyCloak authentication initialized successfully")
            else:
                logger.warning(
                    "KeyCloak initialization failed, using fallback authentication"
                )
        elif KEYCLOAK_ENABLED:
            logger.warning(
                "KeyCloak enabled but module not loaded, using fallback authentication"
            )
        else:
            logger.info("Using basic authentication (KeyCloak disabled)")

        # Log CORS configuration
        origins = settings["ALLOWED_ORIGINS"].split(",")
        logger.info(f"CORS configuration: allowing origins: {origins}")

        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down ZMP Manual Backend service")

        # Clean up notification clients
        from zmp_manual_backend.api.manual_router import manual_service

        try:
            # Use asyncio.run_until_complete to run the coroutine in the synchronous context
            import asyncio

            loop = asyncio.get_event_loop()
            if manual_service:
                loop.run_until_complete(manual_service.unregister_all_clients())
                logger.info("All notification clients unregistered")
        except Exception as e:
            logger.error(f"Error cleaning up notification clients: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="ZMP Manual Backend",
    description="Backend service for ZMP manual management",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_env_settings()
allowed_origins = settings["ALLOWED_ORIGINS"].split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Add basic health checks here
        repo_path = Path(settings["REPO_BASE_PATH"])
        if not repo_path.exists():
            raise HTTPException(
                status_code=503, detail="Repository directory not accessible"
            )

        return {
            "status": "healthy",
            "version": "0.1.0",
            "repository_path": str(repo_path.absolute()),
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))


# Create a prefixed API router
api_router = APIRouter(prefix="/api/manual/v1")


# Add duplicated health check to the API router
@api_router.get("/health")
async def api_health_check():
    """Health check endpoint with prefix"""
    return await health_check()


# Include routers with the API prefix
api_router.include_router(manual_router, tags=["manuals"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Include the API router in the app
app.include_router(api_router)

if __name__ == "__main__":
    try:
        settings = get_env_settings()
        uvicorn.run(
            "zmp_manual_backend.main:app",
            host=settings["HOST"],
            port=int(settings["PORT"]),
            reload=bool(settings["DEBUG"].lower() == "true"),
            log_level=settings["LOG_LEVEL"].lower(),
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
