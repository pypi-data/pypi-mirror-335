from enum import IntEnum

class HTTPStatus(IntEnum):
    """HTTP status codes used by the Lexoffice API"""
    
    # Success codes
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client error codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    CONFLICT = 409
    UNSUPPORTED_MEDIA_TYPE = 415
    TOO_MANY_REQUESTS = 429
    
    # Server error codes
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

class HTTPStatusMessages:
    """HTTP status messages for Lexoffice API responses"""
    
    MESSAGES = {
        HTTPStatus.OK: "Standard response for a successful request",
        HTTPStatus.CREATED: "Resource successfully created",
        HTTPStatus.ACCEPTED: "Request accepted, further processing needed",
        HTTPStatus.NO_CONTENT: "Resource successfully deleted",
        HTTPStatus.BAD_REQUEST: "Malformed syntax or bad query",
        HTTPStatus.UNAUTHORIZED: "Authentication required",
        HTTPStatus.PAYMENT_REQUIRED: "Action not accessible due to contract issue",
        HTTPStatus.FORBIDDEN: "Insufficient permissions",
        HTTPStatus.NOT_FOUND: "Resource does not exist",
        HTTPStatus.METHOD_NOT_ALLOWED: "Method not allowed on resource",
        HTTPStatus.NOT_ACCEPTABLE: "Validation issues due to invalid data",
        HTTPStatus.CONFLICT: "Request conflicts with resource state (e.g. outdated version)",
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE: "Unsupported Content-Type",
        HTTPStatus.TOO_MANY_REQUESTS: "Rate limit exceeded",
        HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error",
        HTTPStatus.NOT_IMPLEMENTED: "HTTP operation not supported",
        HTTPStatus.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
        HTTPStatus.GATEWAY_TIMEOUT: "Gateway timeout, request may have succeeded"
    }
    
    @classmethod
    def get_message(cls, status_code: int) -> str:
        """Get the message for a status code
        
        Args:
            status_code (int): HTTP status code
            
        Returns:
            str: Status message
        """
        return cls.MESSAGES.get(status_code, "Unknown status code") 