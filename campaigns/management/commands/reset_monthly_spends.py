"""
Django management command to reset monthly spends for all campaigns.
"""
from decimal import Decimal
from typing import Any
from django.core.management.base import BaseCommand
from django.db import transaction
from campaigns.models import Campaign
from campaigns.tasks import reset_monthly_spends

class Command(BaseCommand):
    help = 'Reset monthly spend for all campaigns and reactivate eligible ones'
    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--async', action='store_true', help='Run the reset asynchronously using Celery')
    def handle(self, *args: Any, **options: Any) -> None:
        if options['async']:
            result = reset_monthly_spends.delay()
            self.stdout.write(self.style.SUCCESS(f'Monthly spend reset task queued with ID: {result.id}'))
        else:
            with transaction.atomic():
                updated_count = Campaign.objects.update(monthly_spend=Decimal('0.00'))
                reactivated_count = 0
                paused_campaigns = Campaign.objects.filter(status=Campaign.Status.PAUSED)
                for campaign in paused_campaigns:
                    if campaign.can_be_activated():
                        campaign.activate_campaign()
                        reactivated_count += 1
                        self.stdout.write(f'Reactivated campaign: {campaign.name}')
            self.stdout.write(self.style.SUCCESS(f'Successfully reset monthly spend for {updated_count} campaigns. Reactivated {reactivated_count} campaigns.')) 