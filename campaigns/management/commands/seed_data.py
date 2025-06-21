"""
Enhanced seed data command for the ad agency system.
Creates comprehensive test data including brands, campaigns, dayparting schedules, and spend logs.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from typing import List, Tuple
import random
from datetime import time, timedelta

from campaigns.models import Brand, Campaign, DaypartingSchedule, SpendLog


class Command(BaseCommand):
    help = 'Seed the database with comprehensive test data for the ad agency system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brands',
            type=int,
            default=5,
            help='Number of brands to create (default: 5)'
        )
        parser.add_argument(
            '--campaigns-per-brand',
            type=int,
            default=3,
            help='Number of campaigns per brand (default: 3)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed database with test data...')
        
        # Create brands
        brands = self._create_brands(options['brands'])
        
        # Create campaigns for each brand
        campaigns = self._create_campaigns(brands, options['campaigns_per_brand'])
        
        # Create dayparting schedules
        self._create_dayparting_schedules(campaigns)
        
        # Create spend logs
        self._create_spend_logs(campaigns)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(brands)} brands\n'
                f'- {len(campaigns)} campaigns\n'
                f'- Dayparting schedules for all campaigns\n'
                f'- Spend logs for all campaigns'
            )
        )

    def _create_brands(self, count: int) -> List[Brand]:
        """Create test brands."""
        brands = []
        brand_names = [
            'TechCorp', 'FashionForward', 'FoodieDelight', 'SportsMax', 'HomeStyle',
            'BeautyGlow', 'AutoDrive', 'TravelWise', 'HealthPlus', 'EduSmart'
        ]
        
        for i in range(min(count, len(brand_names))):
            brand, created = Brand.objects.get_or_create(
                name=brand_names[i],
                defaults={
                    'description': f'Leading {brand_names[i].lower()} company with innovative products and services.',
                    'is_active': True
                }
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        return brands

    def _create_campaigns(self, brands: List[Brand], campaigns_per_brand: int) -> List[Campaign]:
        """Create test campaigns with various states and budgets."""
        campaigns = []
        campaign_types = [
            ('Brand Awareness', 200.00, 5000.00),
            ('Lead Generation', 150.00, 3000.00),
            ('Product Launch', 300.00, 8000.00),
            ('Seasonal Sale', 100.00, 2000.00),
            ('Retargeting', 75.00, 1500.00),
        ]
        
        statuses = [Campaign.Status.ACTIVE, Campaign.Status.PAUSED, Campaign.Status.DRAFT]
        
        for brand in brands:
            for i in range(campaigns_per_brand):
                campaign_type, daily_budget, monthly_budget = campaign_types[i % len(campaign_types)]
                
                # Vary the status and spend to create realistic scenarios
                status = statuses[i % len(statuses)]
                daily_spend = Decimal('0.00')
                monthly_spend = Decimal('0.00')
                
                if status == Campaign.Status.ACTIVE:
                    # Some active campaigns have spent money
                    if random.choice([True, False]):
                        daily_spend = Decimal(str(random.uniform(10.00, daily_budget * 0.8)))
                        monthly_spend = Decimal(str(random.uniform(100.00, monthly_budget * 0.7)))
                elif status == Campaign.Status.PAUSED:
                    # Paused campaigns likely exceeded budget
                    daily_spend = Decimal(str(daily_budget)) + Decimal(str(random.uniform(1.00, 50.00)))
                    monthly_spend = Decimal(str(monthly_budget)) + Decimal(str(random.uniform(10.00, 500.00)))
                
                # Set date range
                start_date = timezone.now().date() - timedelta(days=random.randint(0, 30))
                end_date = None
                if random.choice([True, False]):
                    end_date = start_date + timedelta(days=random.randint(30, 90))
                
                campaign, created = Campaign.objects.get_or_create(
                    name=f"{campaign_type} - {brand.name}",
                    brand=brand,
                    defaults={
                        'status': status,
                        'daily_budget': daily_budget,
                        'monthly_budget': monthly_budget,
                        'daily_spend': daily_spend,
                        'monthly_spend': monthly_spend,
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                )
                campaigns.append(campaign)
                if created:
                    self.stdout.write(f'Created campaign: {campaign.name} (Status: {status})')
        
        return campaigns

    def _create_dayparting_schedules(self, campaigns: List[Campaign]) -> None:
        """Create dayparting schedules for campaigns."""
        # Common business hours
        business_hours = [
            (time(9, 0), time(17, 0)),   # 9 AM - 5 PM
            (time(8, 0), time(18, 0)),   # 8 AM - 6 PM
            (time(10, 0), time(16, 0)),  # 10 AM - 4 PM
        ]
        
        # Extended hours for some campaigns
        extended_hours = [
            (time(6, 0), time(22, 0)),   # 6 AM - 10 PM
            (time(0, 0), time(23, 59)),  # 24 hours
        ]
        
        for campaign in campaigns:
            # Skip some campaigns to have variety
            if random.choice([True, False, False]):  # 33% chance to skip
                continue
                
            # Choose hours based on campaign type
            if 'Brand Awareness' in campaign.name or 'Product Launch' in campaign.name:
                hours_list = business_hours + extended_hours
            else:
                hours_list = business_hours
            
            # Create schedules for weekdays (Monday-Friday)
            for day in range(1, 6):  # Monday = 1, Friday = 5
                if random.choice([True, True, False]):  # 66% chance to create schedule
                    start_time, end_time = random.choice(hours_list)
                    
                    # Add some variation to start/end times
                    start_minutes = random.randint(-30, 30)
                    end_minutes = random.randint(-30, 30)
                    
                    adjusted_start = time(
                        (start_time.hour + (start_time.minute + start_minutes) // 60) % 24,
                        (start_time.minute + start_minutes) % 60
                    )
                    adjusted_end = time(
                        (end_time.hour + (end_time.minute + end_minutes) // 60) % 24,
                        (end_time.minute + end_minutes) % 60
                    )
                    
                    DaypartingSchedule.objects.get_or_create(
                        campaign=campaign,
                        day_of_week=day,
                        defaults={
                            'start_time': adjusted_start,
                            'end_time': adjusted_end,
                            'is_active': True
                        }
                    )
            
            # Some campaigns also run on weekends
            if random.choice([True, False]):
                for day in [6, 7]:  # Saturday, Sunday
                    if random.choice([True, False]):
                        start_time, end_time = random.choice(business_hours)
                        DaypartingSchedule.objects.get_or_create(
                            campaign=campaign,
                            day_of_week=day,
                            defaults={
                                'start_time': start_time,
                                'end_time': end_time,
                                'is_active': True
                            }
                        )

    def _create_spend_logs(self, campaigns: List[Campaign]) -> None:
        """Create spend logs for campaigns."""
        for campaign in campaigns:
            # Create 1-5 spend logs per campaign
            num_logs = random.randint(1, 5)
            
            for i in range(num_logs):
                # Generate realistic spend amounts
                if campaign.daily_budget > 0:
                    max_amount = min(Decimal(str(campaign.daily_budget)) * Decimal('0.3'), Decimal('50.00'))
                    amount = Decimal(str(random.uniform(1.00, float(max_amount))))
                else:
                    amount = Decimal(str(random.uniform(1.00, 25.00)))
                
                # Generate timestamp within the last 30 days
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                timestamp = timezone.now() - timedelta(
                    days=days_ago,
                    hours=hours_ago,
                    minutes=minutes_ago
                )
                
                descriptions = [
                    'Google Ads spend',
                    'Facebook Ads spend',
                    'Display advertising',
                    'Search advertising',
                    'Social media advertising',
                    'Retargeting campaign',
                    'Influencer marketing',
                    'Video advertising',
                ]
                
                SpendLog.objects.create(
                    campaign=campaign,
                    amount=amount,
                    timestamp=timestamp,
                    description=random.choice(descriptions)
                )