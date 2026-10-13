"""Celery configuration tests without requiring a running broker."""
from src.integrations.celery_app import celery_app
from src.integrations.tasks import healthcheck


def test_celery_uses_json_serialization_and_utc() -> None:
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.enable_utc is True


def test_healthcheck_task_is_registered() -> None:
    assert healthcheck.name == "saphira.healthcheck"
