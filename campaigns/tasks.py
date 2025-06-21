"""
Celery tasks for campaign management and budget control.
"""

import logging
from decimal import Decimal
from typing import List, Optional
from django.utils import timezone
from django.db import transaction
from celery import shared_task
from .models import Campaign, Brand, DaypartingSchedule, SpendLog

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def check_campaign_budgets(self) -> dict[str, int]:
    logger.info("Starting campaign budget check")
    active_campaigns = Campaign.objects.filter(status=Campaign.Status.ACTIVE)
    paused_count = 0
    checked_count = active_campaigns.count()
    for campaign in active_campaigns:
        if not campaign.is_within_budget():
            campaign.pause_campaign()
            paused_count += 1
            logger.info(f"Paused campaign {campaign.name} due to budget limits")
    logger.info(f"Budget check completed: {checked_count} campaigns checked, {paused_count} paused")
    return {'checked_count': checked_count, 'paused_count': paused_count}

@shared_task(bind=True)
def reset_daily_spends(self) -> dict[str, int]:
    logger.info("Starting daily spend reset")
    with transaction.atomic():
        updated_count = Campaign.objects.update(daily_spend=Decimal('0.00'))
        reactivated_count = 0
        paused_campaigns = Campaign.objects.filter(status=Campaign.Status.PAUSED)
        for campaign in paused_campaigns:
            if campaign.can_be_activated():
                campaign.activate_campaign()
                reactivated_count += 1
                logger.info(f"Reactivated campaign {campaign.name} after daily reset")
    logger.info(f"Daily reset completed: {updated_count} campaigns reset, {reactivated_count} reactivated")
    return {'reset_count': updated_count, 'reactivated_count': reactivated_count}

@shared_task(bind=True)
def reset_monthly_spends(self) -> dict[str, int]:
    logger.info("Starting monthly spend reset")
    with transaction.atomic():
        updated_count = Campaign.objects.update(monthly_spend=Decimal('0.00'))
        reactivated_count = 0
        paused_campaigns = Campaign.objects.filter(status=Campaign.Status.PAUSED)
        for campaign in paused_campaigns:
            if campaign.can_be_activated():
                campaign.activate_campaign()
                reactivated_count += 1
                logger.info(f"Reactivated campaign {campaign.name} after monthly reset")
    logger.info(f"Monthly reset completed: {updated_count} campaigns reset, {reactivated_count} reactivated")
    return {'reset_count': updated_count, 'reactivated_count': reactivated_count}

@shared_task(bind=True)
def enforce_dayparting(self) -> dict[str, int]:
    logger.info("Starting dayparting enforcement")
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
                logger.info(f"Enabled campaign {campaign.name} due to dayparting schedule")
        else:
            if campaign.status == Campaign.Status.ACTIVE:
                campaign.pause_campaign()
                disabled_count += 1
                logger.info(f"Disabled campaign {campaign.name} due to dayparting schedule")
    logger.info(f"Dayparting enforcement completed: {enabled_count} enabled, {disabled_count} disabled")
    return {'enabled_count': enabled_count, 'disabled_count': disabled_count}

@shared_task(bind=True)
def add_campaign_spend(self, campaign_id: int, amount: Decimal, description: str = "") -> dict[str, str]:
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        with transaction.atomic():
            campaign.add_spend(amount)
            SpendLog.objects.create(
                campaign=campaign,
                amount=amount,
                description=description or f"Spend added via task"
            )
        logger.info(f"Added ${amount} spend to campaign {campaign.name}")
        return {'status': 'success', 'message': f'Successfully added ${amount} spend to campaign {campaign.name}'}
    except Campaign.DoesNotExist:
        error_msg = f"Campaign with ID {campaign_id} not found"
        logger.error(error_msg)
        return {'status': 'error', 'message': error_msg}
    except Exception as e:
        error_msg = f"Error adding spend to campaign {campaign_id}: {str(e)}"
        logger.error(error_msg)
        return {'status': 'error', 'message': error_msg}

@shared_task(bind=True)
def activate_eligible_campaigns(self) -> dict[str, int]:
    logger.info("Starting campaign activation check")
    activated_count = 0
    draft_campaigns = Campaign.objects.filter(status=Campaign.Status.DRAFT)
    for campaign in draft_campaigns:
        if campaign.can_be_activated():
            campaign.activate_campaign()
            activated_count += 1
            logger.info(f"Activated campaign {campaign.name}")
    logger.info(f"Campaign activation completed: {activated_count} campaigns activated")
    return {'activated_count': activated_count}

@shared_task(bind=True)
def generate_spend_report(self, brand_id: Optional[int] = None) -> dict[str, any]:
    logger.info("Generating spend report")
    campaigns = Campaign.objects.all()
    if brand_id:
        campaigns = campaigns.filter(brand_id=brand_id)
    total_daily_spend = sum(campaign.daily_spend for campaign in campaigns)
    total_monthly_spend = sum(campaign.monthly_spend for campaign in campaigns)
    active_campaigns = campaigns.filter(status=Campaign.Status.ACTIVE).count()
    paused_campaigns = campaigns.filter(status=Campaign.Status.PAUSED).count()
    report = {
        'total_campaigns': campaigns.count(),
        'active_campaigns': active_campaigns,
        'paused_campaigns': paused_campaigns,
        'total_daily_spend': float(total_daily_spend),
        'total_monthly_spend': float(total_monthly_spend),
        'generated_at': timezone.now().isoformat()
    }
    logger.info(f"Spend report generated: {report}")
    return report 