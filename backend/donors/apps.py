from django.apps import AppConfig


class DonorsConfig(AppConfig):
    name = 'donors'

    def ready(self):
        import donors.signals  # noqa: F401 – registers post_save signal handler
