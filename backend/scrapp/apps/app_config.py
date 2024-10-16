import inspect
from importlib import import_module
from types import ModuleType

from scrapp.core.exceptions import ImproperlyConfigured
from scrapp.scraper.web_scraper import BaseWebScraper
from scrapp.utils.module_loading import import_string, module_has_submodule

APPS_MODULE_NAME = "apps"
TABLES_MODULE_NAME = "tables"
SCRAPERS_MODULE_NAME = "scrapers"


class AppConfig:

    def __init__(self, app_name: str, app_module: ModuleType):
        # Full Python path to the application e.g. 'django.contrib.admin'.
        self.name: str = app_name

        # Root module for the application e.g. <module 'django.contrib.admin'
        # from 'django/contrib/admin/__init__.py'>.
        self.module: ModuleType = app_module

        # Reference to the Apps registry that holds this AppConfig. Set by the
        # registry when it registers the AppConfig instance.
        self.apps = None

        # The following attributes could be defined at the class level in a
        # subclass, hence the test-and-set pattern.

        # Last component of the Python path to the application e.g. 'admin'.
        # This value must be unique across a Django project.
        if not hasattr(self, "label"):
            self.label = app_name.rpartition(".")[2]
        if not self.label.isidentifier():
            raise ImproperlyConfigured(
                "The app label '%s' is not a valid Python identifier." % self.label
            )

        # Human-readable name for the application e.g. "Admin".
        if not hasattr(self, "verbose_name"):
            self.verbose_name = self.label.title()

        # Filesystem path to the application directory e.g.
        # '/path/to/django/contrib/admin'.
        # if not hasattr(self, "path"):
        #     self.path = self._path_from_module(app_module)

        # Module containing models e.g. <module 'django.contrib.admin.models'
        # from 'django/contrib/admin/models.py'>. Set by import_models().
        # None if the application doesn't have a models module.
        self.models_module = None

        # Mapping of lowercase model names to model classes. Initially set to
        # None to prevent accidental access before import_models() runs.
        self.models = None

    @classmethod
    def create(cls, entry: str) -> "AppConfig":
        # create() eventually returns app_config_class(app_name, app_module).
        app_config_class = None
        app_config_name = None
        app_name = None
        app_module = None

        # If import_module succeeds, entry points to the app module.
        try:
            app_module = import_module(entry)
        except Exception:
            pass
        else:
            # If app_module has an apps submodule that defines a single
            # AppConfig subclass, use it automatically.
            # To prevent this, an AppConfig subclass can declare a class
            # variable default = False.
            # If the apps module defines more than one AppConfig subclass,
            # the default one can declare default = True.
            if module_has_submodule(app_module, APPS_MODULE_NAME):
                mod_path = "%s.%s" % (entry, APPS_MODULE_NAME)
                mod = import_module(mod_path)
                # Check if there's exactly one AppConfig candidate,
                # excluding those that explicitly define default = False.
                app_configs = [
                    (name, candidate)
                    for name, candidate in inspect.getmembers(mod, inspect.isclass)
                    if (
                        issubclass(candidate, cls)
                        and candidate is not cls
                        and getattr(candidate, "default", True)
                    )
                ]

                # If there is just one app config, use that config.
                if len(app_configs) == 1:
                    app_config_class = app_configs[0][1]
                    app_config_name = "%s.%s" % (mod_path, app_configs[0][0])
                else:
                    # Check if there's exactly one AppConfig subclass,
                    # among those that explicitly define default = True.
                    app_configs = [
                        (name, candidate)
                        for name, candidate in app_configs
                        if getattr(candidate, "default", False)
                    ]
                    if len(app_configs) > 1:
                        candidates = [repr(name) for name, _ in app_configs]
                        raise RuntimeError(
                            "%r declares more than one default AppConfig: "
                            "%s." % (mod_path, ", ".join(candidates))
                        )
                    elif len(app_configs) == 1:
                        app_config_class = app_configs[0][1]
                        app_config_name = "%s.%s" % (mod_path, app_configs[0][0])

        if app_config_class is None:
            try:
                app_config_class = import_string(entry)
            except Exception:
                pass
        # If both import_module and import_string failed, it means that entry
        # doesn't have a valid value.

        if app_module is None and app_config_class is None:
            # If the last component of entry starts with an uppercase letter,
            # then it was likely intended to be an app config class; if not,
            # an app module. Provide a nice error message in both cases.
            mod_path, _, cls_name = entry.rpartition(".")
            if mod_path and cls_name[0].isupper():
                # We could simply re-trigger the string import exception, but
                # we're going the extra mile and providing a better error
                # message for typos in INSTALLED_APPS.
                # This may raise ImportError, which is the best exception
                # possible if the module at mod_path cannot be imported.
                mod = import_module(mod_path)
                candidates = [
                    repr(name)
                    for name, candidate in inspect.getmembers(mod, inspect.isclass)
                    if issubclass(candidate, cls) and candidate is not cls
                ]
                msg = "Module '%s' does not contain a '%s' class." % (
                    mod_path,
                    cls_name,
                )
                if candidates:
                    msg += " Choices are: %s." % ", ".join(candidates)

                raise ImportError(msg)
            else:
                # Re-trigger the module import exception.
                import_module(entry)

        # Obtain app name here rather than in AppClass.__init__ to keep
        # all error checking for entries in INSTALLED_APPS in one place.
        if app_name is None:
            try:
                app_name = app_config_class.name  # type: ignore
            except AttributeError:
                raise ImproperlyConfigured("'%s' must supply a name attribute." % entry)

        # Ensure app_name points to a valid module.
        try:
            app_module = import_module(app_name)
        except ImportError:
            raise ImproperlyConfigured(
                "Cannot import '%s'. Check that '%s.%s.name' is correct."
                % (
                    app_name,
                    app_config_class.__module__,
                    app_config_class.__qualname__,
                )
            )

        # Entry is a path to an app config class.
        return app_config_class(app_name, app_module)  # type: ignore

    def import_tables(self):
        # Dictionary of models for this app, primarily maintained in the
        # 'all_models' attribute of the Apps this AppConfig is attached to.
        self.models = self.apps.all_models[self.label]  # type: ignore

        if module_has_submodule(self.module, TABLES_MODULE_NAME):
            models_module_name = "%s.%s" % (self.name, TABLES_MODULE_NAME)
            self.models_module = import_module(models_module_name)

    def import_scrapers(self):
        from scrapp.scraper import ScraperManager

        # Extract the scrapers from the Scrapers module and register them.
        if module_has_submodule(self.module, SCRAPERS_MODULE_NAME):
            models_module_name = "%s.%s" % (self.name, SCRAPERS_MODULE_NAME)
            self.scrapers_module = import_module(models_module_name)

            # Get all scrapers that have already been initialized
            scrapers = [
                (name, candidate)
                for name, candidate in inspect.getmembers(
                    self.scrapers_module, lambda c: isinstance(c, BaseWebScraper)
                )
            ]

            app_scraper_manager = ScraperManager.get_instance(self.name)

            # Register each of the found scrapers to the appropriate manager instance
            for scraper in scrapers:
                app_scraper_manager.register(scraper[1])

    def ready(self):
        """
        Override to perform actions after an app is loaded.
        """
        pass
