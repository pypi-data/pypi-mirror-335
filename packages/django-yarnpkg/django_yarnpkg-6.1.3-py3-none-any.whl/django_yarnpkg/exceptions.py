from django.core.management.base import CommandError


class YarnNotInstalled(CommandError):
    """Custom command error"""

    def __init__(self):
        super(YarnNotInstalled, self).__init__(
            "Yarn not installed, read instruction here - https://yarnpkg.com/",
        )
