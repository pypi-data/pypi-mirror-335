# Base exception class for errors implementing RFC9457 (problem details).
class ProblemDetail(Exception):

    def __init__(self, title, status, detail=None, type_uri=None, instance=None, extensions=None):
        super().__init__(title)
        self.title = title
        self.status = status
        self.detail = detail
        self.type_uri = type_uri or f"about:blank"
        self.instance = instance
        self.extensions = extensions or {}

    # Convert the error to a dictionary following RFC9457 format.
    def to_dict(self):
        problem_detail = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status,
        }

        if self.detail:
            problem_detail["detail"] = self.detail
        if self.instance:
            problem_detail["instance"] = self.instance

        # Add any custom extensions
        problem_detail.update(self.extensions)

        return problem_detail

# 4xx Client Errors
class BadRequestError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Bad Request",
            status=400,
            detail=detail,
            instance=instance
        )

class AuthenticationError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Unauthorized",
            status=401,
            detail=detail,
            instance=instance
        )

class PaymentRequiredError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Payment Required",
            status=402,
            detail=detail,
            instance=instance
        )

class AuthorizationError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Forbidden",
            status=403,
            detail=detail,
            instance=instance
        )

class NotFoundError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Not Found",
            status=404,
            detail=detail,
            instance=instance
        )

class MethodNotAllowedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Method Not Allowed",
            status=405,
            detail=detail,
            instance=instance
        )

class NotAcceptableError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Not Acceptable",
            status=406,
            detail=detail,
            instance=instance
        )

class ProxyAuthenticationError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Proxy Authentication Required",
            status=407,
            detail=detail,
            instance=instance
        )

class RequestTimeoutError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Request Timeout",
            status=408,
            detail=detail,
            instance=instance
        )

class ConflictError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Conflict",
            status=409,
            detail=detail,
            instance=instance
        )

class GoneError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Gone",
            status=410,
            detail=detail,
            instance=instance
        )

class LengthRequiredError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Length Required",
            status=411,
            detail=detail,
            instance=instance
        )

class PreconditionFailedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Precondition Failed",
            status=412,
            detail=detail,
            instance=instance
        )

class PayloadTooLargeError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Payload Too Large",
            status=413,
            detail=detail,
            instance=instance
        )

class URITooLongError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="URI Too Long",
            status=414,
            detail=detail,
            instance=instance
        )

class UnsupportedMediaTypeError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Unsupported Media Type",
            status=415,
            detail=detail,
            instance=instance
        )

class RangeNotSatisfiableError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Range Not Satisfiable",
            status=416,
            detail=detail,
            instance=instance
        )

class ExpectationFailedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Expectation Failed",
            status=417,
            detail=detail,
            instance=instance
        )

class TeapotError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="I'm a teapot",
            status=418,
            detail=detail,
            instance=instance
        )

class MisdirectedRequestError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Misdirected Request",
            status=421,
            detail=detail,
            instance=instance
        )

class UnprocessableEntityError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Unprocessable Entity",
            status=422,
            detail=detail,
            instance=instance
        )

class LockedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Locked",
            status=423,
            detail=detail,
            instance=instance
        )

class FailedDependencyError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Failed Dependency",
            status=424,
            detail=detail,
            instance=instance
        )

class TooEarlyError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Too Early",
            status=425,
            detail=detail,
            instance=instance
        )

class UpgradeRequiredError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Upgrade Required",
            status=426,
            detail=detail,
            instance=instance
        )

class PreconditionRequiredError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Precondition Required",
            status=428,
            detail=detail,
            instance=instance
        )

class TooManyRequestsError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Too Many Requests",
            status=429,
            detail=detail,
            instance=instance
        )

class RequestHeaderFieldsTooLargeError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Request Header Fields Too Large",
            status=431,
            detail=detail,
            instance=instance
        )

class UnavailableForLegalReasonsError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Unavailable For Legal Reasons",
            status=451,
            detail=detail,
            instance=instance
        )


# 5xx Server Errors
class InternalServerError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Internal Server Error",
            status=500,
            detail=detail,
            instance=instance
        )

class NotImplementedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Not Implemented",
            status=501,
            detail=detail,
            instance=instance
        )

class BadGatewayError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Bad Gateway",
            status=502,
            detail=detail,
            instance=instance
        )

class ServiceUnavailableError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Service Unavailable",
            status=503,
            detail=detail,
            instance=instance
        )

class GatewayTimeoutError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Gateway Timeout",
            status=504,
            detail=detail,
            instance=instance
        )

class HTTPVersionNotSupportedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="HTTP Version Not Supported",
            status=505,
            detail=detail,
            instance=instance
        )

class VariantAlsoNegotiatesError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Variant Also Negotiates",
            status=506,
            detail=detail,
            instance=instance
        )

class InsufficientStorageError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Insufficient Storage",
            status=507,
            detail=detail,
            instance=instance
        )

class LoopDetectedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Loop Detected",
            status=508,
            detail=detail,
            instance=instance
        )

class NotExtendedError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Not Extended",
            status=510,
            detail=detail,
            instance=instance
        )

class NetworkAuthenticationRequiredError(ProblemDetail):
    def __init__(self, detail=None, instance=None):
        super().__init__(
            title="Network Authentication Required",
            status=511,
            detail=detail,
            instance=instance
        )
