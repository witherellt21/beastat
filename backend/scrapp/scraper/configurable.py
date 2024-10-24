class NotConfiguredException(Exception):
    def __init__(self, class_name: str, *args, **kwargs) -> None:
        message: str = f"{class_name} is not configured."

        super().__init__(message, *args, **kwargs)


class Configurable:

    def __init__(self):
        self.__configured: bool = False

    @property
    def configured(self):
        return self.__configured

    def check_configuration(self):
        if not self.__configured:
            raise NotConfiguredException(self.__class__.__name__)

    def configure(self):
        self.__configured = True
