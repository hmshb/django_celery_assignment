# Django + Celery Budget Management System - Architecture Pseudo-code

## System Overview
This document provides a high-level, language-agnostic overview of the ad agency campaign management system architecture, including data models, business logic, and key operational workflows.

## Data Models

### 1. Brand Entity
```
BRAND:
  - id: unique_identifier
  - name: string (unique, max 200 chars)
  - description: optional_text
  - created_at: timestamp
  - updated_at: timestamp
  - is_active: boolean (default: true)
  
  METHODS:
    - get_total_daily_spend(): returns sum of all campaign daily_spend
    - get_total_monthly_spend(): returns sum of all campaign monthly_spend
```

### 2. Campaign Entity
```
CAMPAIGN:
  - id: unique_identifier
  - name: string (max 200 chars)
  - brand_id: foreign_key_to_brand
  - status: enum (DRAFT, ACTIVE, PAUSED, COMPLETED)
  - daily_budget: decimal (min 0.01)
  - monthly_budget: decimal (min 0.01)
  - daily_spend: decimal (default 0.00)
  - monthly_spend: decimal (default 0.00)
  - start_date: date
  - end_date: optional_date
  - created_at: timestamp
  - updated_at: timestamp
  
  METHODS:
    - is_within_budget(): returns daily_spend <= daily_budget AND monthly_spend <= monthly_budget
    - can_be_activated(): returns true if DRAFT status, within date range, and within budget
    - pause_campaign(): sets status to PAUSED if currently ACTIVE
    - activate_campaign(): sets status to ACTIVE if can_be_activated() returns true
    - add_spend(amount): increments daily_spend and monthly_spend, pauses if over budget
```

### 3. DaypartingSchedule Entity
```
DAYPARTING_SCHEDULE:
  - id: unique_identifier
  - campaign_id: foreign_key_to_campaign
  - day_of_week: integer (1-7, Monday-Sunday)
  - start_time: time
  - end_time: time
  - is_active: boolean (default: true)
  
  METHODS:
    - is_within_schedule(current_time): returns true if current time falls within schedule
```

### 4. SpendLog Entity
```
SPEND_LOG:
  - id: unique_identifier
  - campaign_id: foreign_key_to_campaign
  - amount: decimal (min 0.01)
  - timestamp: timestamp
  - description: optional_text
```

## Key Business Logic

### 1. Spend Tracking Logic
```
FUNCTION add_campaign_spend(campaign_id, amount, description):
  BEGIN_TRANSACTION
    campaign = GET_CAMPAIGN_BY_ID(campaign_id)
    IF campaign EXISTS:
      campaign.daily_spend += amount
      campaign.monthly_spend += amount
      SAVE campaign
      
      CREATE spend_log:
        campaign_id = campaign_id
        amount = amount
        description = description
        timestamp = CURRENT_TIMESTAMP
      
      IF NOT campaign.is_within_budget():
        campaign.pause_campaign()
      
      RETURN success_message
    ELSE:
      RETURN error_message
  END_TRANSACTION
```

### 2. Budget Enforcement Logic
```
FUNCTION check_campaign_budgets():
  active_campaigns = GET_ALL_CAMPAIGNS_WITH_STATUS('ACTIVE')
  paused_count = 0
  
  FOR EACH campaign IN active_campaigns:
    IF NOT campaign.is_within_budget():
      campaign.pause_campaign()
      paused_count += 1
      LOG("Paused campaign {campaign.name} due to budget limits")
  
  RETURN {
    checked_count: active_campaigns.count,
    paused_count: paused_count
  }
```

### 3. Dayparting Check Logic
```
FUNCTION enforce_dayparting():
  current_time = GET_CURRENT_TIME()
  enabled_count = 0
  disabled_count = 0
  
  campaigns_with_schedules = GET_CAMPAIGNS_WITH_DAYPARTING_SCHEDULES()
  
  FOR EACH campaign IN campaigns_with_schedules:
    active_schedules = GET_ACTIVE_SCHEDULES_FOR_CAMPAIGN(campaign.id)
    
    IF active_schedules EXISTS:
      is_within_schedule = FALSE
      
      FOR EACH schedule IN active_schedules:
        IF schedule.is_within_schedule(current_time):
          is_within_schedule = TRUE
          BREAK
      
      IF is_within_schedule:
        IF campaign.status == 'PAUSED' AND campaign.can_be_activated():
          campaign.activate_campaign()
          enabled_count += 1
      ELSE:
        IF campaign.status == 'ACTIVE':
          campaign.pause_campaign()
          disabled_count += 1
  
  RETURN {
    enabled_count: enabled_count,
    disabled_count: disabled_count
  }
```

### 4. Daily Spend Reset Logic
```
FUNCTION reset_daily_spends():
  BEGIN_TRANSACTION
    UPDATE_ALL_CAMPAIGNS SET daily_spend = 0.00
    reactivated_count = 0
    
    paused_campaigns = GET_CAMPAIGNS_WITH_STATUS('PAUSED')
    
    FOR EACH campaign IN paused_campaigns:
      IF campaign.can_be_activated():
        campaign.activate_campaign()
        reactivated_count += 1
    
    RETURN {
      reset_count: total_campaigns_updated,
      reactivated_count: reactivated_count
    }
  END_TRANSACTION
```

### 5. Monthly Spend Reset Logic
```
FUNCTION reset_monthly_spends():
  BEGIN_TRANSACTION
    UPDATE_ALL_CAMPAIGNS SET monthly_spend = 0.00
    reactivated_count = 0
    
    paused_campaigns = GET_CAMPAIGNS_WITH_STATUS('PAUSED')
    
    FOR EACH campaign IN paused_campaigns:
      IF campaign.can_be_activated():
        campaign.activate_campaign()
        reactivated_count += 1
    
    RETURN {
      reset_count: total_campaigns_updated,
      reactivated_count: reactivated_count
    }
  END_TRANSACTION
```

## Scheduled Tasks & Automation

### 1. Budget Monitoring Task
```
SCHEDULED_TASK check_campaign_budgets():
  FREQUENCY: Every 15 minutes
  PURPOSE: Monitor active campaigns and pause those exceeding budgets
  EXECUTION: check_campaign_budgets()
```

### 2. Dayparting Enforcement Task
```
SCHEDULED_TASK enforce_dayparting():
  FREQUENCY: Every 5 minutes
  PURPOSE: Enable/disable campaigns based on dayparting schedules
  EXECUTION: enforce_dayparting()
```

### 3. Daily Reset Task
```
SCHEDULED_TASK reset_daily_spends():
  FREQUENCY: Daily at 00:00
  PURPOSE: Reset daily spend counters and reactivate eligible campaigns
  EXECUTION: reset_daily_spends()
```

### 4. Monthly Reset Task
```
SCHEDULED_TASK reset_monthly_spends():
  FREQUENCY: Monthly on 1st day at 00:00
  PURPOSE: Reset monthly spend counters and reactivate eligible campaigns
  EXECUTION: reset_monthly_spends()
```

## System Workflows

### 1. Campaign Activation Workflow
```
FUNCTION activate_eligible_campaigns():
  draft_campaigns = GET_CAMPAIGNS_WITH_STATUS('DRAFT')
  activated_count = 0
  
  FOR EACH campaign IN draft_campaigns:
    IF campaign.can_be_activated():
      campaign.activate_campaign()
      activated_count += 1
  
  RETURN { activated_count: activated_count }
```

### 2. Spend Reporting Workflow
```
FUNCTION generate_spend_report(brand_id = null):
  campaigns = GET_ALL_CAMPAIGNS()
  
  IF brand_id IS NOT NULL:
    campaigns = FILTER_CAMPAIGNS_BY_BRAND(campaigns, brand_id)
  
  total_daily_spend = SUM(campaigns.daily_spend)
  total_monthly_spend = SUM(campaigns.monthly_spend)
  active_campaigns = COUNT_CAMPAIGNS_WITH_STATUS(campaigns, 'ACTIVE')
  paused_campaigns = COUNT_CAMPAIGNS_WITH_STATUS(campaigns, 'PAUSED')
  
  RETURN {
    total_campaigns: campaigns.count,
    active_campaigns: active_campaigns,
    paused_campaigns: paused_campaigns,
    total_daily_spend: total_daily_spend,
    total_monthly_spend: total_monthly_spend,
    generated_at: CURRENT_TIMESTAMP
  }
```

## Data Integrity & Constraints

### 1. Budget Constraints
- Daily spend cannot exceed daily budget
- Monthly spend cannot exceed monthly budget
- Campaigns are automatically paused when budgets are exceeded

### 2. Date Constraints
- Campaign start_date must be <= current date for activation
- Campaign end_date (if set) must be >= current date for activation

### 3. Status Transitions
- DRAFT → ACTIVE: Only if can_be_activated() returns true
- ACTIVE → PAUSED: When budget exceeded or outside dayparting schedule
- PAUSED → ACTIVE: When budgets reset and within dayparting schedule

### 4. Dayparting Constraints
- Multiple schedules can exist per campaign
- Schedules are evaluated in real-time
- Campaigns are automatically paused outside scheduled times
