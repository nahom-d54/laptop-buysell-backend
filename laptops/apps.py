from django.apps import AppConfig


class LaptopsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "laptops"

    def ready(self):
        from laptops import tasks

        tasks.start_scheduler()
