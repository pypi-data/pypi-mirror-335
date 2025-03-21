"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from jsonschema import ValidationError

from fastapi import status, Request, FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError, StarletteHTTPException

from nomenclators_archetype.infrastructure.http.exceptions import ConflictException, NotFoundException
from nomenclators_archetype.domain.exceptions import BusinessIntegrityError
from nomenclators_archetype.domain.repository.commons import RepositoryMissingElementError


def init_error_handler(app: FastAPI, config_errors):
    """ Init error handler """

    @app.exception_handler(Exception)
    async def internal_server_error_handle(_req: Request, exc: Exception):
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'title': type(exc).__name__,
                'description': f'{str(exc)}',
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(RequestValidationError)
    async def request_exception_handle(_req: Request, exc: RequestValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'title': 'invalid:data',
                'description': 'wrong value',
                'extra': exc.errors(),
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handle(req: Request, exc: StarletteHTTPException):
        if exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            return await validation_exception_handler(req, ValidationError('Error en la validación del schema'))
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            return await request_exception_handle(req, RequestValidationError('Error en la petición'))
        elif exc.status_code == status.HTTP_409_CONFLICT:
            return await conflict_exception_handler(req, ConflictException('Error de conflicto'))
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            return await not_found_exception_handler(req, ValidationError(exc.detail))
        return await internal_server_error_handle(req, exc)

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_request: Request, exc: ValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'title': 'Invalid:format',
                'description': f"Validation error: {exc.message}",
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(_req: Request, exc: ConflictException):
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                'title': 'conflict:error',
                'description': exc.detail,
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(ValidationError)
    async def not_found_exception_handler(_request: Request, exc: ValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'title': 'NotFound:data',
                'description': f"Not Found: {exc.message}",
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(BusinessIntegrityError)
    async def business_integrity_exception_handler(_request: Request, exc: BusinessIntegrityError):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'title': 'Business Errors:data',
                'description': f"Errors: {exc.errors}",
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_update_handler(_request: Request, exc: NotFoundException):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'title': 'Errors :data',
                'description': f"Errors: {exc.detail}",
                'admin_email': config_errors.get('email')
            }
        )

    @app.exception_handler(RepositoryMissingElementError)
    async def repository_missing_element_error_handler(_request: Request, exc: RepositoryMissingElementError):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'title': 'Errors :data',
                'description': f"Errors: {exc}",
                'admin_email': config_errors.get('email')
            }
        )
