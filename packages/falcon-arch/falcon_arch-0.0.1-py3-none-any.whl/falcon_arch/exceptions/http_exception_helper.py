from .http_exception import HTTPException
from dataclasses import dataclass

@dataclass
class ErrorDetail:
    title: str
    description: str

class HTTPExceptionHelper:
    _errors = {
        400: ErrorDetail("Bad Request", "The request could not be processed."),
        401: ErrorDetail("Unauthorized", "You need to be authenticated to access this resource."),
        402: ErrorDetail("Payment Required", "The request cannot be processed until payment is made."),
        403: ErrorDetail("Forbidden", "You do not have permission to access this resource."),
        404: ErrorDetail("Not Found", "The requested resource was not found."),
        405: ErrorDetail("Method Not Allowed", "The request method is not supported for the requested resource."),
        406: ErrorDetail("Not Acceptable", "The requested resource is not available in a format acceptable to the client."),
        407: ErrorDetail("Proxy Authentication Required", "Proxy authentication is required."),
        408: ErrorDetail("Request Timeout", "The server timed out waiting for the request."),
        409: ErrorDetail("Conflict", "There was a conflict with the current state of the resource."),
        410: ErrorDetail("Gone", "The resource is no longer available and will not be available again."),
        411: ErrorDetail("Length Required", "The server requires the Content-Length header field."),
        412: ErrorDetail("Precondition Failed", "A precondition in the request was not met."),
        413: ErrorDetail("Payload Too Large", "The request is larger than the server is willing or able to process."),
        414: ErrorDetail("URI Too Long", "The URI provided was too long for the server to process."),
        415: ErrorDetail("Unsupported Media Type", "The media type of the request is not supported by the server."),
        416: ErrorDetail("Range Not Satisfiable", "The range specified in the request cannot be satisfied."),
        417: ErrorDetail("Expectation Failed", "The server cannot meet the requirements of the Expect request-header field."),
        426: ErrorDetail("Upgrade Required", "The client should switch to a different protocol."),
        428: ErrorDetail("Precondition Required", "The server requires the request to be conditional."),
        429: ErrorDetail("Too Many Requests", "The user has sent too many requests in a given amount of time."),
        431: ErrorDetail("Request Header Fields Too Large", "The server is unwilling to process the request because its header fields are too large."),
        451: ErrorDetail("Unavailable For Legal Reasons", "The resource is unavailable for legal reasons."),
        500: ErrorDetail("Internal Server Error", "An unexpected error occurred on the server."),
        501: ErrorDetail("Not Implemented", "The server does not support the functionality required to fulfill the request."),
        502: ErrorDetail("Bad Gateway", "The server received an invalid response from an upstream server."),
        503: ErrorDetail("Service Unavailable", "The server is currently unable to handle the request due to temporary overload or maintenance."),
        504: ErrorDetail("Gateway Timeout", "The server did not receive a timely response from an upstream server."),
        505: ErrorDetail("HTTP Version Not Supported", "The server does not support the HTTP protocol version that was used in the request."),
        507: ErrorDetail("Insufficient Storage", "The server is unable to store the representation needed to complete the request."),
        508: ErrorDetail("Loop Detected", "The server detected an infinite loop while processing the request."),
        510: ErrorDetail("Not Extended", "Further extensions to the request are required for the server to fulfill it."),
        511: ErrorDetail("Network Authentication Required", "The client needs to authenticate to gain network access."),
    }
    
    _default_error = ErrorDetail("Unknown Error", "An unknown error occurred.")

    @classmethod
    def handle(cls, code: int) -> HTTPException:
        """ Returns an instance of HTTPException for the provided code. """
        error = cls._errors.get(code, cls._default_error)
        return HTTPException(code or 500, error.title, error.description)
