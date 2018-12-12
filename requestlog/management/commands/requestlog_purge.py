from datetime import datetime, timedelta

from django.core.management import BaseCommand

from ...models import RequestLog


class Command(BaseCommand):
    help = 'Delete entries in the requestlog older than one month'

    def handle(self, *args, **options):
        since = datetime.now() - timedelta(days=30)
        entries = RequestLog.objects.filter(timestamp__lte = since)
        self.stdout.write(f"Remove {entries.count()} Old Requestlog entries older than {since.strftime('%d.%m.%Y')}")
        entries.delete()
