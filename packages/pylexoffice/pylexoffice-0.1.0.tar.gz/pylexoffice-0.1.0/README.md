# pylexoffice

A Python SDK for the Lexoffice API. This library provides a simple and intuitive way to interact with the Lexoffice API.

## Installation

```bash
pip install pylexoffice
```

## Quick Start

```python
from lexoffice import LexofficeClient

# Initialize the client
client = LexofficeClient(api_key="your_api_key_here")

# Create a contact
contact_data = {
    "version": 0,
    "roles": {
        "customer": {}
    },
    "company": {
        "name": "Sample Company GmbH"
    },
    "addresses": {
        "billing": [{
            "street": "Sample Street 42",
            "zip": "12345",
            "city": "Sample City",
            "countryCode": "DE"
        }]
    }
}

contact = client.contacts.create(contact_data)

# Create an invoice
invoice_data = {
    "voucherDate": "2024-02-22T00:00:00.000+01:00",
    "address": {
        "name": "Sample Company GmbH",
        "street": "Sample Street 42",
        "city": "Sample City",
        "zip": "12345",
        "countryCode": "DE"
    },
    "lineItems": [
        {
            "type": "custom",
            "name": "Product A",
            "quantity": 1,
            "unitName": "Piece",
            "unitPrice": {
                "currency": "EUR",
                "netAmount": 100,
                "taxRatePercentage": 19
            }
        }
    ],
    "totalPrice": {
        "currency": "EUR"
    },
    "taxConditions": {
        "taxType": "net"
    }
}

# Create a draft invoice
invoice = client.invoices.create(invoice_data)

# Create and finalize an invoice
finalized_invoice = client.invoices.create(invoice_data, finalize=True)
```

## Features

- Full support for Lexoffice API endpoints
- Rate limiting handling
- Type hints for better IDE support
- Intuitive resource-based interface
- Comprehensive error handling

## Available Resources

- Contacts
- Invoices
- Articles
- Credit Notes
- Vouchers

## Rate Limiting

The Lexoffice API has a rate limit of 2 requests per second. This SDK automatically handles rate limiting by adding appropriate delays between requests.

## Error Handling

The SDK provides detailed error handling with custom exceptions:

```python
from lexoffice import LexofficeApiError, RateLimitExceeded

try:
    contact = client.contacts.get("invalid-id")
except RateLimitExceeded:
    print("Rate limit exceeded, please wait")
except LexofficeApiError as e:
    print(f"API error: {e}")
```

## Documentation

For detailed API documentation, please visit the [Lexoffice API Documentation](https://developers.lexoffice.io/docs/).

## Requirements

- Python 3.10+
- requests>=2.25.0
- pandas>=2.0.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue on GitHub. 