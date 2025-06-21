"""
Django models for the ad agency campaign management system.
"""

from decimal import Decimal
from typing import Optional
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Brand(models.Model):
    name: str = models.CharField(max_length=200, unique=True)
    description: Optional[str] = models.TextField(blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_active: bool = models.BooleanField(default=True)

    class Meta:
        db_table = 'brands'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def get_total_daily_spend(self) -> Decimal:
        return sum(campaign.daily_spend for campaign in self.campaigns.all())

    def get_total_monthly_spend(self) -> Decimal:
        return sum(campaign.monthly_spend for campaign in self.campaigns.all())

class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        DRAFT = 'draft', 'Draft'

    name: str = models.CharField(max_length=200)
    brand: Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='campaigns')
    status: str = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    daily_budget: Decimal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    monthly_budget: Decimal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    daily_spend: Decimal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monthly_spend: Decimal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    start_date: models.DateField = models.DateField()
    end_date: Optional[models.DateField] = models.DateField(null=True, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']
        unique_together = ['name', 'brand']

    def __str__(self) -> str:
        return f"{self.brand.name} - {self.name}"

    def is_within_budget(self) -> bool:
        return self.daily_spend <= self.daily_budget and self.monthly_spend <= self.monthly_budget

    def can_be_activated(self) -> bool:
        today = timezone.now().date()
        return (
            self.status == self.Status.DRAFT and
            self.start_date <= today and
            (self.end_date is None or self.end_date >= today) and
            self.is_within_budget()
        )

    def pause_campaign(self) -> None:
        if self.status == self.Status.ACTIVE:
            self.status = self.Status.PAUSED
            self.save(update_fields=['status', 'updated_at'])

    def activate_campaign(self) -> None:
        if self.can_be_activated():
            self.status = self.Status.ACTIVE
            self.save(update_fields=['status', 'updated_at'])

    def add_spend(self, amount: Decimal) -> None:
        self.daily_spend += amount
        self.monthly_spend += amount
        self.save(update_fields=['daily_spend', 'monthly_spend', 'updated_at'])
        if not self.is_within_budget():
            self.pause_campaign()

class DaypartingSchedule(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'
        SUNDAY = 7, 'Sunday'

    campaign: Campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='dayparting_schedules')
    day_of_week: int = models.IntegerField(choices=DayOfWeek.choices)
    start_time: models.TimeField = models.TimeField()
    end_time: models.TimeField = models.TimeField()
    is_active: bool = models.BooleanField(default=True)

    class Meta:
        db_table = 'dayparting_schedules'
        unique_together = ['campaign', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self) -> str:
        return f"{self.campaign.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def is_within_schedule(self, current_time: Optional[timezone.datetime] = None) -> bool:
        if not self.is_active:
            return False
        if current_time is None:
            current_time = timezone.now()
        if current_time.isoweekday() != self.day_of_week:
            return False
        current_time_only = current_time.time()
        return self.start_time <= current_time_only <= self.end_time

class SpendLog(models.Model):
    campaign: Campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='spend_logs')
    amount: Decimal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    timestamp: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    description: Optional[str] = models.TextField(blank=True)

    class Meta:
        db_table = 'spend_logs'
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f"{self.campaign.name} - ${self.amount} at {self.timestamp}" 