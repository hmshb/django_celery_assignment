"""
Django admin interface for the campaigns app.
"""

from decimal import Decimal
from typing import Any
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString
from .models import Brand, Campaign, DaypartingSchedule, SpendLog

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_active', 'total_daily_spend', 'total_monthly_spend', 'campaign_count', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def total_daily_spend(self, obj: Brand) -> str:
        return f"${obj.get_total_daily_spend():.2f}"
    total_daily_spend.short_description = 'Total Daily Spend'

    def total_monthly_spend(self, obj: Brand) -> str:
        return f"${obj.get_total_monthly_spend():.2f}"
    total_monthly_spend.short_description = 'Total Monthly Spend'

    def campaign_count(self, obj: Brand) -> int:
        return obj.campaigns.count()
    campaign_count.short_description = 'Campaigns'

class DaypartingScheduleInline(admin.TabularInline):
    model = DaypartingSchedule
    extra = 1
    fields = ['day_of_week', 'start_time', 'end_time', 'is_active']

class SpendLogInline(admin.TabularInline):
    model = SpendLog
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['amount', 'timestamp', 'description']
    can_delete = False
    def has_add_permission(self, request: Any, obj: Any = None) -> bool:
        return False

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'status', 'daily_budget_progress', 'monthly_budget_progress', 'start_date', 'end_date'
    ]
    list_filter = ['status', 'brand', 'start_date', 'end_date']
    search_fields = ['name', 'brand__name']
    readonly_fields = ['created_at', 'updated_at', 'daily_spend', 'monthly_spend']
    inlines = [DaypartingScheduleInline, SpendLogInline]
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'brand', 'status', 'start_date', 'end_date')}),
        ('Budget Information', {'fields': ('daily_budget', 'monthly_budget', 'daily_spend', 'monthly_spend')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    actions = ['activate_campaigns', 'pause_campaigns', 'reset_daily_spend', 'reset_monthly_spend']

    def daily_budget_progress(self, obj: Campaign) -> SafeString:
        daily_spend = float(obj.daily_spend)
        daily_budget = float(obj.daily_budget)
        
        if daily_budget > 0:
            percentage = (daily_spend / daily_budget) * 100
        else:
            percentage = 0.0
        
        color = 'red' if percentage > 100 else 'orange' if percentage > 80 else 'green'
        width = min(percentage, 100)
        percentage_str = f"{percentage:.1f}%"
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: {}; border-radius: 3px; '
            'display: flex; align-items: center; justify-content: center; color: white; '
            'font-size: 10px;">{}</div></div>',
            width, color, percentage_str
        )
    daily_budget_progress.short_description = 'Daily Budget'

    def monthly_budget_progress(self, obj: Campaign) -> SafeString:
        monthly_spend = float(obj.monthly_spend)
        monthly_budget = float(obj.monthly_budget)
        
        if monthly_budget > 0:
            percentage = (monthly_spend / monthly_budget) * 100
        else:
            percentage = 0.0
        
        color = 'red' if percentage > 100 else 'orange' if percentage > 80 else 'green'
        width = min(percentage, 100)
        percentage_str = f"{percentage:.1f}%"
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: {}; border-radius: 3px; '
            'display: flex; align-items: center; justify-content: center; color: white; '
            'font-size: 10px;">{}</div></div>',
            width, color, percentage_str
        )
    monthly_budget_progress.short_description = 'Monthly Budget'

    def activate_campaigns(self, request: Any, queryset: Any) -> None:
        activated_count = 0
        for campaign in queryset:
            if campaign.can_be_activated():
                campaign.activate_campaign()
                activated_count += 1
        self.message_user(request, f'Successfully activated {activated_count} campaigns.')
    activate_campaigns.short_description = 'Activate selected campaigns'

    def pause_campaigns(self, request: Any, queryset: Any) -> None:
        paused_count = 0
        for campaign in queryset:
            if campaign.status == Campaign.Status.ACTIVE:
                campaign.pause_campaign()
                paused_count += 1
        self.message_user(request, f'Successfully paused {paused_count} campaigns.')
    pause_campaigns.short_description = 'Pause selected campaigns'

    def reset_daily_spend(self, request: Any, queryset: Any) -> None:
        updated_count = queryset.update(daily_spend=Decimal('0.00'))
        self.message_user(request, f'Successfully reset daily spend for {updated_count} campaigns.')
    reset_daily_spend.short_description = 'Reset daily spend'

    def reset_monthly_spend(self, request: Any, queryset: Any) -> None:
        updated_count = queryset.update(monthly_spend=Decimal('0.00'))
        self.message_user(request, f'Successfully reset monthly spend for {updated_count} campaigns.')
    reset_monthly_spend.short_description = 'Reset monthly spend'

@admin.register(DaypartingSchedule)
class DaypartingScheduleAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'campaign__brand']
    search_fields = ['campaign__name', 'campaign__brand__name']
    ordering = ['campaign__brand__name', 'campaign__name', 'day_of_week']

@admin.register(SpendLog)
class SpendLogAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'amount', 'timestamp', 'description']
    list_filter = ['timestamp', 'campaign__brand', 'campaign__status']
    search_fields = ['campaign__name', 'campaign__brand__name', 'description']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    def has_add_permission(self, request: Any) -> bool:
        return False 