from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Message, DirectMessage


class Command(BaseCommand):
    help = "Delete messages older than 24 hours"

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(hours=24)

        # ルーム内メッセージ削除
        room_qs = Message.objects.filter(created_at__lt=threshold)
        room_deleted, _ = room_qs.delete()

        # DM削除
        dm_qs = DirectMessage.objects.filter(
            created_at__lt=threshold
        )
        dm_deleted, _ = dm_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Deleted {room_deleted + dm_deleted} messages")
        )
