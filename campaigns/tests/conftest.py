"""
Pytest configuration and fixtures for campaign testing.
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from freezegun import freeze_time
from factory import Faker
from campaigns.models import Brand, Campaign, DaypartingSchedule, SpendLog


@pytest.fixture
def brand():
    """Create a test brand."""
    return Brand.objects.create(
        name="Test Brand",
        description="A test brand for testing"
    )


@pytest.fixture
def campaign(brand):
    """Create a test campaign."""
    return Campaign.objects.create(
        name="Test Campaign",
        brand=brand,
        daily_budget=Decimal('100.00'),
        monthly_budget=Decimal('1000.00'),
        start_date=timezone.now().date(),
        status=Campaign.Status.DRAFT
    )


@pytest.fixture
def active_campaign(brand):
    """Create an active test campaign."""
    return Campaign.objects.create(
        name="Active Campaign",
        brand=brand,
        daily_budget=Decimal('100.00'),
        monthly_budget=Decimal('1000.00'),
        start_date=timezone.now().date(),
        status=Campaign.Status.ACTIVE
    )


@pytest.fixture
def dayparting_schedule(campaign):
    """Create a dayparting schedule for a campaign."""
    return DaypartingSchedule.objects.create(
        campaign=campaign,
        day_of_week=1,  # Monday
        start_time="09:00:00",
        end_time="17:00:00",
        is_active=True
    )


@pytest.fixture
def spend_log(campaign):
    """Create a spend log entry."""
    return SpendLog.objects.create(
        campaign=campaign,
        amount=Decimal('50.00'),
        description="Test spend"
    )


@pytest.fixture
@freeze_time("2024-01-15 10:00:00")
def frozen_time():
    """Freeze time for consistent testing."""
    return timezone.now() 