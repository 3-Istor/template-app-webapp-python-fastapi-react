from app.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.app_name
    assert settings.resolved_database_url.startswith("postgresql+psycopg://")
