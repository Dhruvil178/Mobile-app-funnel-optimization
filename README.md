# Mobile App Gamification Funnel Optimization (52K+ Events)

## Executive Summary
Discovered a critical platform-specific leak where **24% of Android users** dropped off immediately after completing a community challenge due to an unhandled API error. By building an end-to-end ELT pipeline, this project unmasked 970 hidden server crashes and provided a concrete engineering roadmap to recover lost user retention.

---

## Tech Stack & Architecture
- **Data Engineering:** Python 3, Pandas (Data generation & mock-telemetry modeling)
- **Database Layer:** SQLite3 (Local high-performance transactional DB)
- **Analytics:** Advanced SQL (Conditional aggregation, window functions)
- **Environment:** Jupyter Notebook

---

## The Data Pipeline & Cleaning Decisions
Real-world app telemetry is highly fragmented. The raw dataset contained over 52,000 uncleaned logs with multiple intentional engineering defects. 

Rather than destructive editing, I designed a non-destructive **SQL Master Cleaning View** (`clean_app_events`) to enforce data quality standards automatically:

1. **Deduplication:** Applied `DISTINCT` logic to filter out artificial transaction inflation caused by rapid user "double-tapping."
2. **Timestamp Normalization:** Constructed a structural `CASE WHEN` conditional query to dynamically catch and parse raw Unix Epoch numbers into consistent ISO-8601 strings.
3. **Event Standardization:** Normalized inconsistent front-end string entries (e.g., merging `clck_reward` and `ap_open` typos into explicit funnel phases).

```sql
-- Snippet of the Master Pipeline View
CREATE VIEW clean_app_events AS
SELECT DISTINCT
    CASE 
        WHEN timestamp LIKE '%-%' THEN timestamp
        ELSE datetime(CAST(timestamp AS INT), 'unixepoch')
    END AS clean_timestamp,
    user_id, session_id, device_os,
    CASE 
        WHEN event_name = 'ap_open' THEN 'app_open'
        WHEN event_name = 'view_tasklist' THEN 'view_task_list'
        WHEN event_name = 'clck_reward' THEN 'claim_points'
        ELSE event_name 
    END AS clean_event_name
FROM staging_app_events;