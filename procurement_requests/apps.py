from django.apps import AppConfig

class ProcurementRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'procurement_requests'

    def ready(self):
        # Import and register the signals
        import procurement_requests.signals