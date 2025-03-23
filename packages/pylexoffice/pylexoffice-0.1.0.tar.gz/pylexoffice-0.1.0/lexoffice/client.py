import time
import requests
from typing import Optional, Dict, Any
from .exceptions import LexofficeApiError, RateLimitExceeded, ValidationError, AuthenticationError, ResourceNotFoundError, OptimisticLockingError
from .http import HTTPStatus

class LexofficeClient:
    """Main client class for interacting with the Lexoffice API"""
    
    BASE_URL = "https://api.lexoffice.io/v1"
    RATE_LIMIT_PER_SECOND = 2  # API allows 2 requests per second
    
    def __init__(self, api_key: str):
        """Initialize the Lexoffice client
        
        Args:
            api_key (str): Your Lexoffice API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self._last_request_time = 0
        
        # Initialize resources
        from .resources.invoices import InvoicesResource
        from .resources.contacts import ContactsResource
        from .resources.articles import ArticlesResource
        from .resources.vouchers import VouchersResource
        from .resources.credit_notes import CreditNotesResource
        from .resources.countries import CountriesResource
        from .resources.delivery_notes import DeliveryNotesResource
        from .resources.dunnings import DunningsResource
        from .resources.down_payment_invoices import DownPaymentInvoicesResource
        from .resources.event_subscriptions import EventSubscriptionsResource
        from .resources.files import FilesResource
        from .resources.payments import PaymentsResource
        from .resources.order_confirmations import OrderConfirmationsResource
        from .resources.payment_conditions import PaymentConditionsResource
        from .resources.posting_categories import PostingCategoriesResource
        from .resources.profile import ProfileResource
        from .resources.print_layouts import PrintLayoutsResource
        from .resources.quotations import QuotationsResource
        from .resources.recurring_templates import RecurringTemplatesResource
        from .resources.voucherlist import VoucherListResource
        
        self.invoices = InvoicesResource(self)
        self.contacts = ContactsResource(self)
        self.articles = ArticlesResource(self)
        self.vouchers = VouchersResource(self)
        self.credit_notes = CreditNotesResource(self)
        self.countries = CountriesResource(self)
        self.delivery_notes = DeliveryNotesResource(self)
        self.dunnings = DunningsResource(self)
        self.down_payment_invoices = DownPaymentInvoicesResource(self)
        self.event_subscriptions = EventSubscriptionsResource(self)
        self.files = FilesResource(self)
        self.payments = PaymentsResource(self)
        self.order_confirmations = OrderConfirmationsResource(self)
        self.payment_conditions = PaymentConditionsResource(self)
        self.posting_categories = PostingCategoriesResource(self)
        self.profile = ProfileResource(self)
        self.print_layouts = PrintLayoutsResource(self)
        self.quotations = QuotationsResource(self)
        self.recurring_templates = RecurringTemplatesResource(self)
        self.voucherlist = VoucherListResource(self)
        
    def _handle_rate_limit(self):
        """Handle rate limiting by adding delay if needed"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        if elapsed < (1.0 / self.RATE_LIMIT_PER_SECOND):
            time.sleep((1.0 / self.RATE_LIMIT_PER_SECOND) - elapsed)
            
        self._last_request_time = time.time()
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Lexoffice API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, etc)
            endpoint (str): API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            ResourceNotFoundError: If resource not found
            OptimisticLockingError: If resource version conflict
            RateLimitExceeded: If rate limit exceeded
            LexofficeApiError: For other API errors
        """
        self._handle_rate_limit()
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle specific status codes
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitExceeded(response=response.json() if response.content else None)
                
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise AuthenticationError(response=response.json() if response.content else None)
                
            if response.status_code == HTTPStatus.NOT_ACCEPTABLE:
                raise ValidationError(
                    "Request validation failed",
                    response=response.json() if response.content else None
                )
                
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise ResourceNotFoundError(
                    endpoint,
                    response=response.json() if response.content else None
                )
                
            if response.status_code == HTTPStatus.CONFLICT:
                raise OptimisticLockingError(
                    response=response.json() if response.content else None
                )
                
            response.raise_for_status()
            
            if response.status_code == HTTPStatus.NO_CONTENT:
                return {}
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'json'):
                error_data = e.response.json()
                raise LexofficeApiError(
                    f"API request failed: {error_data.get('message', str(e))}",
                    status_code=e.response.status_code,
                    response=error_data
                )
            raise LexofficeApiError(f"API request failed: {str(e)}") 