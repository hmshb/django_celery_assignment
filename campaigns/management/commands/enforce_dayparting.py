"""
Django management command to enforce dayparting schedules for campaigns.
"""
from typing import Any
from django.core.management.base import BaseCommand
from django.utils import timezone
from campaigns.models import Campaign
from campaigns.tasks import enforce_dayparting

class Command(BaseCommand):
    help = 'Enforce dayparting schedules for all campaigns'
    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--async', action='store_true', help='Run the enforcement asynchronously using Celery')
    def handle(self, *args: Any, **options: Any) -> None:
        if options['async']:
            result = enforce_dayparting.delay()
            self.stdout.write(self.style.SUCCESS(f'Dayparting enforcement task queued with ID: {result.id}'))
        else:
            current_time = timezone.now()
            enabled_count = 0
            disabled_count = 0
            campaigns_with_schedules = Campaign.objects.filter(dayparting_schedules__isnull=False).distinct()
            for campaign in campaigns_with_schedules:
                schedules = campaign.dayparting_schedules.filter(is_active=True)
                if not schedules.exists():
                    continue
                is_within_schedule = any(schedule.is_within_schedule(current_time) for schedule in schedules)
                if is_within_schedule:
                    if campaign.status == Campaign.Status.PAUSED and campaign.can_be_activated():
                        campaign.activate_campaign()
                        enabled_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Enabled campaign {campaign.name} due to dayparting schedule'))
                else:
                    if campaign.status == Campaign.Status.ACTIVE:
                        campaign.pause_campaign()
                        disabled_count += 1
                        self.stdout.write(self.style.WARNING(f'Disabled campaign {campaign.name} due to dayparting schedule'))
            self.stdout.write(self.style.SUCCESS(f'Dayparting enforcement completed: {enabled_count} enabled, {disabled_count} disabled')) 