def setup():
    from scrapp.apps import apps
    from scrapp.conf import settings

    apps.populate(settings.INSTALLED_APPS)
