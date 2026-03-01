# Django Billing System

## Features

- Product management using Django Admin
- Billing generation with tax calculation
- Denomination-based change calculation
- Rounding logic for unsupported denomination values
- Async email sending (console backend)
- Transaction safe operations

## Assumptions

- Denominations available are multiples of 10
- Change is rounded down to nearest available denomination
- Stock cannot go negative
- Paid amount must be >= total bill amount

## Setup Instructions

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
