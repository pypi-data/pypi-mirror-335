import logging

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from django_redis import get_redis_connection

from .azure_helper import get_db_password, get_redis_credentials

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == settings.HEALTH_CHECK_PATH:
            # Update the database credentials if needed
            if settings.AZURE_DB_PASSWORD:
                try:
                    settings.DATABASES["default"]["PASSWORD"] = get_db_password()
                except Exception as e:
                    logger.error("Failed to update database credentials: %s", str(e))
                    return HttpResponse(status=503)

            # Update the Redis credentials if needed
            if settings.AZURE_REDIS_CREDENTIALS:
                try:
                    redis_credentials = get_redis_credentials()
                    # Re-authenticate the Redis connection
                    redis_connection = get_redis_connection("default")
                    redis_connection.execute_command("AUTH", redis_credentials.username, redis_credentials.password)
                    settings.CACHES["default"]["OPTIONS"]["PASSWORD"] = redis_credentials.password
                except Exception as e:
                    logger.error("Failed to update Redis credentials: %s", str(e))
                    return HttpResponse(status=503)

            try:
                # Test the database connection
                connection.ensure_connection()
                logger.debug("Database connection check passed")

                # Test the Redis connection
                cache.set("health_check", "test")
                logger.debug("Redis connection check passed")

                return HttpResponse("OK")

            except OperationalError as e:
                logger.error("Database connection failed: %s", str(e))
                return HttpResponse(status=503)
            except Exception as e:
                logger.error("Health check failed with unexpected error: %s", str(e))
                return HttpResponse(status=503)

        return self.get_response(request)
