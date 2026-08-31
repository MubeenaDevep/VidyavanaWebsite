from django.core.management.base import BaseCommand, CommandError

from apps.chatbot.rag.vector_store import build_index


class Command(BaseCommand):
    help = "Build the local FAISS index from verified knowledge documents."

    def handle(self, *args, **options):
        try:
            count = build_index()
        except RuntimeError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Indexed {count} knowledge chunks."))
