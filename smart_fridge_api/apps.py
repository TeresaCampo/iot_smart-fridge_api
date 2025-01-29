from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError


class SmartFridgeApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'smart_fridge_api'