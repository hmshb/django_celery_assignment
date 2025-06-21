"""
Django management command to check campaign budgets and pause over-budget campaigns.
"""
from typing import Any
from django.core.management.base import BaseCommand
from campaigns.models import Campaign
from campaigns.tasks import check_campaign_budgets

class Command(BaseCommand):
    help = 'Check all active campaigns and pause those that exceed their budgets'
    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--async', action='store_true', help='Run the check asynchronously using Celery')
    def handle(self, *args: Any, **options: Any) -> None:
        if options['async']:
            result = check_campaign_budgets.delay()
            self.stdout.write(self.style.SUCCESS(f'Budget check task queued with ID: {result.id}'))
        else:
            active_campaigns = Campaign.objects.filter(status=Campaign.Status.ACTIVE)
            paused_count = 0
            checked_count = active_campaigns.count()
            for campaign in active_campaigns:
                if not campaign.is_within_budget():
                    campaign.pause_campaign()
                    paused_count += 1
                    self.stdout.write(self.style.WARNING(f'Paused campaign {campaign.name} due to budget limits'))
            self.stdout.write(self.style.SUCCESS(f'Budget check completed: {checked_count} campaigns checked, {paused_count} paused')) 