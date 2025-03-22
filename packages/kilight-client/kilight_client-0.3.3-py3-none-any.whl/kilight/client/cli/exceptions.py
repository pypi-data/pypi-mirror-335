class ConfigurationError(Exception):
    """
    Error with the configuration
    """
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"Configuration error: {self.message}"


class MissingConfigSectionError(ConfigurationError):
    """
    The configuration is missing a required section
    """
    def __init__(self, section: str):
        super().__init__("missing required section: {0}".format(section))


class MissingConfigOptionError(ConfigurationError):
    """
    The configuration is missing a required config option
    """
    def __init__(self, section: str, option: str):
        super().__init__("missing required option {0}.{1}".format(section, option))
