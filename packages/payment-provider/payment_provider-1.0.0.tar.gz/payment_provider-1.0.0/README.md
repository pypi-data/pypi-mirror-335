# PaymentProvider Python SDK client


[![Downloads](https://pepy.tech/badge/payment_provider)](https://pepy.tech/project/payment_provider)
[![Downloads](https://pepy.tech/badge/payment_provider/month)](https://pepy.tech/project/payment_provider)
[![Downloads](https://pepy.tech/badge/payment_provider/week)](https://pepy.tech/project/payment_provider)

## Payment provider
A payment service provider (PSP) enables businesses to accept electronic payments through various methods, including credit cards, direct debits, bank transfers, and real-time online banking transactions. Typically operating under a software-as-a-service (SaaS) model, PSPs serve as a unified payment gateway, connecting merchants to multiple payment options.[read more](https://en.wikipedia.org/wiki/Payment_service_provider)

Requirements
------------
- Python (2.4, 2.7, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)

Dependencies
------------
- requests
- six

Installation
------------
```bash
pip install payment_provider
```
### Simple start

```python
from payment_provider import Api, Checkout
api = Api(merchant_id=1700001,
          secret_key='test')
checkout = Checkout(api=api)
data = {
    "currency": "UAH",
    "amount": 200000
}
url = checkout.url(data).get('checkout_url')
```

Tests
-----------------
First, install `tox` `<http://tox.readthedocs.org/en/latest/>`

To run testing:

```bash
tox
```

This will run all tests, against all supported Python versions.