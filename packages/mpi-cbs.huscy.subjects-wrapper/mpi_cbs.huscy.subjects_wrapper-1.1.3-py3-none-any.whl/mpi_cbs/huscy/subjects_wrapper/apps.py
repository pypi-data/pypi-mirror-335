from django.apps import AppConfig


class HuscyApp(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mpi_cbs.huscy.subjects_wrapper'

    class HuscyAppMeta:
        pass
