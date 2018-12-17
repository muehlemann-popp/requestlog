from django.core.management import BaseCommand

from ...utils import delete_old_entries


class Command(BaseCommand):
    help = 'Delete entries in the requestlog older than one month'

    def handle(self, *args, **options):
        delete_old_entries(self.stdout, older_than_days=30)
