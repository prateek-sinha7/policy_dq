# Validation Report

| Rule | Field | Message | Row |
|------|-------|---------|-----|
| email_required | email | field is required | 1 |
| email_format | email | regex failed | 2 |
| age_range | age | value out of range | 1 |
| unique_customer | customer_id | duplicate value | 1 |
| unique_customer | customer_id | duplicate value | 2 |
| valid_dates | start_date,end_date | invalid cross-field rule | 0 |
| valid_dates | start_date,end_date | invalid cross-field rule | 1 |
| valid_dates | start_date,end_date | invalid cross-field rule | 2 |