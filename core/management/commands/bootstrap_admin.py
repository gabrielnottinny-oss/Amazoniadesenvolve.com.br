"""Create the first administrator from a Render-generated secret, never reset users."""
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            return
        password = os.environ.get('INITIAL_ADMIN_PASSWORD')
        if not password:
            raise CommandError('Configure INITIAL_ADMIN_PASSWORD in Render before first startup.')
        username = 'administrador'
        if User.objects.filter(username=username).exists():
            raise CommandError('Administrator username is already in use; resolve manually.')
        try:
            validate_password(password, User(username=username))
        except ValidationError:
            raise CommandError('Initial administrator password does not meet security requirements.')
        with transaction.atomic():
            User.objects.create_superuser(username=username, email='', password=password)
        self.stdout.write('Initial administrator created. Change the password after first login.')
