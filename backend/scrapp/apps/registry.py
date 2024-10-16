import sys
from collections import Counter, defaultdict
from typing import Optional

from scrapp.core.exceptions import AppRegistryNotReady, ImproperlyConfigured

from .app_config import AppConfig


class Apps:
    """
    A registry that stores the configuration of installed applications.

    It also keeps track of models, e.g. to provide reverse relations.
    """

    def __init__(self, installed_apps=()):
        # installed_apps is set to None when creating the master registry
        # because it cannot be populated at that point. Other registries must
        # provide a list of installed apps and are populated immediately.
        if installed_apps is None and hasattr(sys.modules[__name__], "apps"):
            raise RuntimeError("You must supply an installed_apps argument.")

        # Mapping of app labels => model names => model classes. Every time a
        # model is imported, ModelBase.__new__ calls apps.register_model which
        # creates an entry in all_models. All imported models are registered,
        # regardless of whether they're defined in an installed application
        # and whether the registry has been populated. Since it isn't possible
        # to reimport a module safely (it could reexecute initialization code)
        # all_models is never overridden or reset.
        self.all_models = defaultdict(dict)

        # Mapping of labels to AppConfig instances for installed apps.
        self.app_configs: dict[str, AppConfig] = {}

        # Stack of app_configs. Used to store the current state in
        # set_available_apps and set_installed_apps.
        self.stored_app_configs = []

        # Whether the registry is populated.
        self.apps_ready = self.models_ready = self.ready = False

        # Maps ("app_label", "modelname") tuples to lists of functions to be
        # called when the corresponding model is ready. Used by this class's
        # `lazy_model_operation()` and `do_pending_operations()` methods.
        self._pending_operations = defaultdict(list)

        # Populate apps and models, unless it's the master registry.
        if installed_apps is not None:
            self.populate(installed_apps)

    def populate(self, installed_apps: Optional[list[str | AppConfig]] = None):
        if self.ready:
            return

        if installed_apps is None:
            return

        # Phase 1: initialize app configs and import app modules.
        for entry in installed_apps:
            if isinstance(entry, AppConfig):
                app_config = entry
            else:
                app_config = AppConfig.create(entry)

            if app_config.label in self.app_configs:
                raise ImproperlyConfigured(
                    "Application labels aren't unique, "
                    "duplicates: %s" % app_config.label
                )

            self.app_configs[app_config.label] = app_config
            app_config.apps = self  # type: ignore

        # Check for duplicate app names.
        counts = Counter(app_config.name for app_config in self.app_configs.values())
        duplicates = [name for name, count in counts.most_common() if count > 1]

        if duplicates:
            raise ImproperlyConfigured(
                "Application names aren't unique, "
                "duplicates: %s" % ", ".join(duplicates)
            )

        self.apps_ready = True

        # Phase 2: import models modules.
        for app_config in self.app_configs.values():
            app_config.import_tables()

        self.clear_cache()

        self.models_ready = True

        # Phase 3: run ready() methods of app configs.
        for app_config in self.get_app_configs():
            app_config.ready()

        self.ready = True

    def check_apps_ready(self):
        """Raise an exception if all apps haven't been imported yet."""
        if not self.apps_ready:
            from scrapp.conf import settings

            # If "not ready" is due to unconfigured settings, accessing
            # INSTALLED_APPS raises a more helpful ImproperlyConfigured
            # exception.
            settings.INSTALLED_APPS
            raise AppRegistryNotReady("Apps aren't loaded yet.")

    def check_models_ready(self):
        """Raise an exception if all models haven't been imported yet."""
        if not self.models_ready:
            raise AppRegistryNotReady("Models aren't loaded yet.")

    def get_app_configs(self):
        """Import applications and return an iterable of app configs."""
        self.check_apps_ready()
        return self.app_configs.values()

    def get_app_config(self, app_name: str) -> AppConfig:
        self.check_apps_ready()
        return self.app_configs[app_name]

    def clear_cache(self):
        pass


apps = Apps(installed_apps=None)
