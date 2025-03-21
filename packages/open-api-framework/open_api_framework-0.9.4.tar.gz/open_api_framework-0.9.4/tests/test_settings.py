def test_sentry_settings():
    """
    test that sentry settings are initialized
    """
    from django.conf import settings

    assert hasattr(settings, "SENTRY_CONFIG") is True
    assert hasattr(settings, "SENTRY_DSN") is True
