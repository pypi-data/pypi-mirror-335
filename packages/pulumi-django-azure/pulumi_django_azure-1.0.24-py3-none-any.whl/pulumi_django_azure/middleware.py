from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django_redis import get_redis_connection

from .azure_helper import get_db_password, get_redis_credentials


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == settings.HEALTH_CHECK_PATH:
            # Update the database credentials if needed
            if settings.AZURE_DB_PASSWORD:
                settings.DATABASES["default"]["PASSWORD"] = get_db_password()

            # Update the Redis credentials if needed
            if settings.AZURE_REDIS_CREDENTIALS:
                redis_credentials = get_redis_credentials()

                # Re-authenticate the Redis connection
                redis_connection = get_redis_connection("default")
                redis_connection.execute_command("AUTH", redis_credentials.username, redis_credentials.password)

                settings.CACHES["default"]["OPTIONS"]["PASSWORD"] = redis_credentials.password

            try:
                # Test the database connection
                connection.ensure_connection()

                # Test the Redis connection
                cache.set("health_check", "test")

                return HttpResponse("OK")

            except OperationalError:
                return HttpResponse(status=503)

        return self.get_response(request)
