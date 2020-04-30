import traceback
import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.utils import OperationalError, ConnectionHandler
from django.core.exceptions import ImproperlyConfigured

from core.models import User


class Command(BaseCommand):
    help = "Performs safe checks on the Shynet setup"

    def check_migrations(self):
        from django.db.migrations.executor import MigrationExecutor
        try:
            executor = MigrationExecutor(connections[DEFAULT_DB_ALIAS])
        except OperationalError:
            # DB_NAME database not found?
            return True
        except ImproperlyConfigured:
            # No databases are configured (or the dummy one)
            return True
        
        if executor.migration_plan(executor.loader.graph.leaf_nodes()):
            return True
        
        return False
    
    
    def handle(self, *args, **options):
        migration = self.check_migrations()

        admin, hostname, whitelabel = [True] * 3
        if not migration:
            admin = not User.objects.all().exists()
            hostname = not Site.objects.filter(domain__isnull=False).exclude(domain__exact="").exclude(domain__exact="example.com").exists()
            whitelabel = not Site.objects.filter(name__isnull=False).exclude(name__exact="").exclude(name__exact="example.com").exists()

        self.stdout.write(
            self.style.SUCCESS(
                f"{migration} {admin} {hostname} {whitelabel}"
            )
        )
