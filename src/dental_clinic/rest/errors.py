from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi import status
from fastapi.responses import JSONResponse


class RestErrorDetails(BaseModel):
    field: str
    issue: str
    location: str


class ResponseError(BaseModel):
    namespace: str
    informationLink: str
    code: str
    correlationId: Optional[str]
    debugId: str
    message: str
    name: str
    details: Optional[RestErrorDetails]


def build_error_response(request, exc):
    if not isinstance(exc, RestError):
        exc = RestError(exc, request=request)
    headers = {}
    if exc.headers:
        for header, value in exc.headers.items():
            headers[header] = value
    headers['Content-Type'] = 'application/json'
    return JSONResponse(
        exc.error.dict(),
        headers=headers,
        status_code=exc.statusCode
    )


class RestError(Exception):
    namespace = 'rest-sample'

    def __init__(self, error, request=None, details=None):
        super().__init__()
        try:
            self.message = error.message
        except AttributeError:
            try:
                self.message = str(error.errors())
            except AttributeError:
                self.message = None
        error_data = get_error_data_by_error_type(error)
        self.error = ResponseError(
            namespace=self.namespace,
            informationLink=error_data['informationLink'],
            code=error_data['code'],
            correlationId= request.headers.get('Traceparent', None) if request.headers else None,
            debugId=request.state.debug_id,
            message=self.message if self.message else 'Internal server error',
            name=error_data['name'],
            details=None
        )
        if details:
            self.error.details = details
        self.statusCode = error_data['status_code']
        self.headers = error_data['headers']


class ValidationError(RestError):

    def __init__(self, message, validation_data):
        self.message = message
        super().__init__(self, details=validation_data)


def get_error_data_by_error_type(error):
    try:
        exception = exception_mapping[type(error)]
        if type(error) == HTTPException:
            return exception[error.status_code]
        else:
            return exception
    # Internal server error
    except KeyError:
        return {
            'informationLink': 'http://localhost',
            'name': 'INTERNAL_ERROR',
            'code': 'IE001',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'headers': None
        }


exception_mapping = {
        RequestValidationError: {
            'informationLink': 'http://localhost',
            'name': 'VALIDATION_ERROR',
            'code': 'VL001',
            'status_code': status.HTTP_400_BAD_REQUEST,
            'headers': None
        },
        HTTPException: {
            404:
                {
                    'informationLink': 'http://localhost',
                    'name': 'NOT_FOUND',
                    'code': 'NF001',
                    'status_code': status.HTTP_404_NOT_FOUND,
                    'headers': None
                },
            405:
                {
                    'informationLink': 'http://localhost',
                    'name': 'METHOD_NOT_ALLOWED',
                    'code': 'MT001',
                    'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
                    'headers': None
                }
        }
    }
