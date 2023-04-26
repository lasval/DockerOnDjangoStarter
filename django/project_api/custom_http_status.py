from enum import IntEnum

from django.utils.translation import ugettext_lazy

__all__ = ["HTTPStatus"]


class HTTPStatus(IntEnum):
    """HTTP status codes and reason phrases

    Status codes from the following RFCs are all observed:

        * RFC 7231: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616
        * RFC 6585: Additional HTTP Status Codes
        * RFC 3229: Delta encoding in HTTP
        * RFC 4918: HTTP Extensions for WebDAV, obsoletes 2518
        * RFC 5842: Binding Extensions to WebDAV
        * RFC 7238: Permanent Redirect
        * RFC 2295: Transparent Content Negotiation in HTTP
        * RFC 2774: An HTTP Extension Framework
        * RFC 7540: Hypertext Transfer Protocol Version 2 (HTTP/2)
    """

    def __new__(cls, value, phrase, description=""):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    # informational
    CONTINUE = 100, "Continue", "Request received, please continue"
    SWITCHING_PROTOCOLS = (
        101,
        "Switching Protocols",
        "Switching to new protocol; obey Upgrade header",
    )
    PROCESSING = 102, "Processing"

    # success
    OK = 200, "OK", "Request fulfilled, document follows"
    CREATED = 201, "Created", "Document created, URL follows"
    ACCEPTED = (
        202,
        "Accepted",
        "Request accepted, processing continues off-line",
    )
    NON_AUTHORITATIVE_INFORMATION = (
        203,
        "Non-Authoritative Information",
        "Request fulfilled from cache",
    )
    NO_CONTENT = 204, "No Content", "Request fulfilled, nothing follows"
    RESET_CONTENT = 205, "Reset Content", "Clear input form for further input"
    PARTIAL_CONTENT = 206, "Partial Content", "Partial content follows"
    MULTI_STATUS = 207, "Multi-Status"
    ALREADY_REPORTED = 208, "Already Reported"
    IM_USED = 226, "IM Used"

    # redirection
    MULTIPLE_CHOICES = (
        300,
        "Multiple Choices",
        "Object has several resources -- see URI list",
    )
    MOVED_PERMANENTLY = (
        301,
        "Moved Permanently",
        "Object moved permanently -- see URI list",
    )
    FOUND = 302, "Found", "Object moved temporarily -- see URI list"
    SEE_OTHER = 303, "See Other", "Object moved -- see Method and URL list"
    NOT_MODIFIED = (
        304,
        "Not Modified",
        "Document has not changed since given time",
    )
    USE_PROXY = (
        305,
        "Use Proxy",
        "You must use proxy specified in Location to access this resource",
    )
    TEMPORARY_REDIRECT = (
        307,
        "Temporary Redirect",
        "Object moved temporarily -- see URI list",
    )
    PERMANENT_REDIRECT = (
        308,
        "Permanent Redirect",
        "Object moved temporarily -- see URI list",
    )

    # client error
    BAD_REQUEST = (
        400,
        "Bad Request",
        ugettext_lazy("Bad request syntax or unsupported method"),
    )
    UNAUTHORIZED = (
        401,
        "Unauthorized",
        ugettext_lazy("No permission"),
    )
    PAYMENT_REQUIRED = (
        402,
        "Payment Required",
        ugettext_lazy("No payment"),
    )
    FORBIDDEN = (
        403,
        "Forbidden",
        ugettext_lazy("Request forbidde"),
    )
    NOT_FOUND = (
        404,
        "Not Found",
        ugettext_lazy("Nothing matches the given URI"),
    )
    METHOD_NOT_ALLOWED = (
        405,
        "Method Not Allowed",
        ugettext_lazy("Specified method is invalid for this resource"),
    )
    NOT_ACCEPTABLE = (
        406,
        "Not Acceptable",
        ugettext_lazy("URI not available in preferred format"),
    )
    PROXY_AUTHENTICATION_REQUIRED = (
        407,
        "Proxy Authentication Required",
        ugettext_lazy("Proxy Authentication Required"),
    )
    REQUEST_TIMEOUT = (
        408,
        "Request Timeout",
        ugettext_lazy("Request timed out; try again later"),
    )
    CONFLICT = 409, "Conflict", ugettext_lazy("Request conflict")
    GONE = (
        410,
        "Gone",
        ugettext_lazy("URI no longer exists and has been permanently removed"),
    )
    LENGTH_REQUIRED = (
        411,
        "Length Required",
        ugettext_lazy("Client must specify Content-Length"),
    )
    PRECONDITION_FAILED = (
        412,
        "Precondition Failed",
        ugettext_lazy("Precondition in headers is false"),
    )
    REQUEST_ENTITY_TOO_LARGE = (
        413,
        "Request Entity Too Large",
        ugettext_lazy("Entity is too large"),
    )
    REQUEST_URI_TOO_LONG = (
        414,
        "Request-URI Too Long",
        ugettext_lazy("URI is too long"),
    )
    UNSUPPORTED_MEDIA_TYPE = (
        415,
        "Unsupported Media Type",
        ugettext_lazy("Unsupported Media Type"),
    )
    REQUESTED_RANGE_NOT_SATISFIABLE = (
        416,
        "Requested Range Not Satisfiable",
        ugettext_lazy("Requested Range Not Satisfiable"),
    )
    EXPECTATION_FAILED = (
        417,
        "Expectation Failed",
        ugettext_lazy("Expectation Failed"),
    )
    MISDIRECTED_REQUEST = (
        421,
        "Misdirected Request",
        ugettext_lazy("Misdirected Request"),
    )
    UNPROCESSABLE_ENTITY = 422, ugettext_lazy("Unprocessable Entity")
    LOCKED = 423, ugettext_lazy("Locked")
    FAILED_DEPENDENCY = 424, ugettext_lazy("Failed Dependency")
    UPGRADE_REQUIRED = 426, ugettext_lazy("Upgrade Required")
    PRECONDITION_REQUIRED = (
        428,
        "Precondition Required",
        ugettext_lazy("Precondition Required"),
    )
    TOO_MANY_REQUESTS = (
        429,
        "Too Many Requests",
        ugettext_lazy("Too Many Requests"),
    )
    REQUEST_HEADER_FIELDS_TOO_LARGE = (
        431,
        "Request Header Fields Too Large",
        ugettext_lazy("Request Header Fields Too Large"),
    )

    # server errors
    INTERNAL_SERVER_ERROR = (
        500,
        "Internal Server Error",
        "Server got itself in trouble",
    )
    NOT_IMPLEMENTED = (
        501,
        "Not Implemented",
        "Server does not support this operation",
    )
    BAD_GATEWAY = (
        502,
        "Bad Gateway",
        "Invalid responses from another server/proxy",
    )
    SERVICE_UNAVAILABLE = (
        503,
        "Service Unavailable",
        "The server cannot process the request due to a high load",
    )
    GATEWAY_TIMEOUT = (
        504,
        "Gateway Timeout",
        "The gateway server did not receive a timely response",
    )
    HTTP_VERSION_NOT_SUPPORTED = (
        505,
        "HTTP Version Not Supported",
        "Cannot fulfill request",
    )
    VARIANT_ALSO_NEGOTIATES = 506, "Variant Also Negotiates"
    INSUFFICIENT_STORAGE = 507, "Insufficient Storage"
    LOOP_DETECTED = 508, "Loop Detected"
    NOT_EXTENDED = 510, "Not Extended"
    NETWORK_AUTHENTICATION_REQUIRED = (
        511,
        "Network Authentication Required",
        "The client needs to authenticate to gain network access",
    )
