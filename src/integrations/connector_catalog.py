"""Runtime connector catalog and fail-closed configuration checks.

This catalog makes integrations discoverable without pretending that a catalog
entry is a live adapter. Actual provider operations must be implemented by a
typed adapter and explicitly enabled after authentication and smoke tests.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


@dataclass(frozen=True)
class ConnectorSpec:
    name: str
    category: str
    required_env: tuple[str, ...]
    capabilities: tuple[str, ...]
    side_effects: bool = True


# Kept in Python so runtime validation does not depend on a YAML parser.
# Credentials are referenced by name only and are never read into this catalog.
CONNECTORS: tuple[ConnectorSpec, ...] = (
    ConnectorSpec("openai", "model_provider", ("OPENAI_API_KEY",), ("chat", "structured_output", "embeddings", "speech"), False),
    ConnectorSpec("google_gemini", "model_provider", ("GEMINI_API_KEY",), ("chat", "multimodal", "embeddings"), False),
    ConnectorSpec("xai", "model_provider", ("XAI_API_KEY",), ("chat",), False),
    ConnectorSpec("github", "developer_tools", ("GITHUB_TOKEN",), ("repository_read", "pull_request_draft", "issue_management", "ci_status")),
    ConnectorSpec("vercel", "deployment", ("VERCEL_TOKEN",), ("deployment_status", "logs_read")),
    ConnectorSpec("supabase", "data_platform", ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"), ("database_read", "migrations", "vector_search")),
    ConnectorSpec("replit", "development", ("REPLIT_API_TOKEN",), ("project_management",)),
    ConnectorSpec("google_workspace", "productivity", ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET"), ("gmail_draft", "calendar_read", "calendar_write", "drive_search")),
    ConnectorSpec("microsoft_365", "productivity", ("MICROSOFT_CLIENT_ID", "MICROSOFT_CLIENT_SECRET"), ("outlook_draft", "calendar_read", "calendar_write", "onedrive_search")),
    ConnectorSpec("notion", "knowledge", ("NOTION_API_KEY",), ("search_pages", "read_pages", "create_page")),
    ConnectorSpec("asana", "project_management", ("ASANA_ACCESS_TOKEN",), ("task_read", "task_create", "task_update")),
    ConnectorSpec("stripe", "payments", ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"), ("subscription_read", "checkout_session_create", "webhook_verify")),
    ConnectorSpec("shopify", "commerce", ("SHOPIFY_STORE_DOMAIN", "SHOPIFY_ACCESS_TOKEN"), ("products_read", "orders_read", "draft_order_create")),
    ConnectorSpec("zapier", "workflow_automation", ("ZAPIER_MCP_OR_WEBHOOK_CREDENTIALS",), ("approved_workflow_trigger",)),
    ConnectorSpec("twilio", "communications", ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"), ("sms_draft", "voice_call")),
    ConnectorSpec("resend", "communications", ("RESEND_API_KEY",), ("email_draft", "approved_email_send")),
    ConnectorSpec("telegram", "notifications", ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"), ("approved_notification",)),
    ConnectorSpec("canva", "creative", ("CANVA_ACCESS_TOKEN",), ("design_search", "design_export")),
    ConnectorSpec("figma", "creative", ("FIGMA_ACCESS_TOKEN",), ("file_read", "design_context")),
    ConnectorSpec("heygen", "media_generation", ("HEYGEN_API_KEY",), ("avatar_video_generation",)),
    ConnectorSpec("veed", "media_generation", ("VEED_API_KEY",), ("video_generation",)),
    ConnectorSpec("ai_voice_generator", "media_generation", ("AI_VOICE_GENERATOR_CREDENTIALS",), ("text_to_speech",)),
    ConnectorSpec("mcp_servers", "tool_protocol", ("MCP_SERVER_CONFIG",), ("discover_tools", "invoke_allowlisted_tools")),
    ConnectorSpec("web_research", "research", ("WEB_SEARCH_API_KEY",), ("search", "retrieve", "cite_sources"), False),
)


def connector_status(spec: ConnectorSpec, environ: Mapping[str, str] | None = None) -> dict[str, object]:
    """Return non-secret readiness metadata; never activates or invokes a connector."""
    env = os.environ if environ is None else environ
    missing = [key for key in spec.required_env if not str(env.get(key, "")).strip()]
    return {
        "name": spec.name,
        "category": spec.category,
        "capabilities": list(spec.capabilities),
        "configured": not missing,
        "missing_environment": missing,
        "enabled": False,
        "status": "configured_not_enabled" if not missing else "unconfigured",
        "side_effects": spec.side_effects,
    }


def connector_readiness(environ: Mapping[str, str] | None = None) -> dict[str, object]:
    """Summarize catalog readiness without exposing secret values."""
    statuses = [connector_status(spec, environ) for spec in CONNECTORS]
    return {
        "total": len(statuses),
        "configured": sum(bool(item["configured"]) for item in statuses),
        "enabled": 0,
        "connectors": statuses,
    }
