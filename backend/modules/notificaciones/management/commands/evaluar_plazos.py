from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from backend.modules.notificaciones.infrastructure.scheduled_jobs import (
    run_scheduled_evaluations,
)


class Command(BaseCommand):
    help = "Ejecuta la evaluación de plazos: alertas de vencimiento y registro de mora."

    def handle(self, *args, **options):
        result = run_scheduled_evaluations()
        self.stdout.write(json.dumps(result, ensure_ascii=False))
