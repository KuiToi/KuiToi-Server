import asyncio
from asyncio import CancelledError

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

import core.utils
from . import utils

# from .models import SecretKey

web_app = FastAPI()
log = core.utils.get_logger("web")

uvserver = None
data_pool = []
data_run = [True]

LOGGING_CONFIG["formatters"]["default"]['fmt'] = core.utils.log_format
LOGGING_CONFIG["formatters"]["access"]["fmt"] = core.utils.log_format_access
LOGGING_CONFIG["formatters"].update({
    "file_default": {
        "fmt": core.utils.log_format
    },
    "file_access": {
        "fmt": core.utils.log_format_access
    }
})
LOGGING_CONFIG["handlers"]["default"]['stream'] = "ext://sys.stdout"
LOGGING_CONFIG["handlers"].update({
    "file_default": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "webserver.log"
    },
    "file_access": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "webserver.log"
    }
})
LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("file_default")
LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"].append("file_access")


def response(data=None, code=status.HTTP_200_OK, error_code=0, error_message=None):
    if 200 >= code <= 300:
        return JSONResponse(content={"result": data, "error": None}, status_code=code)
    return JSONResponse(
        content={"error": {"code": error_code if error_code else code, "message": f"{error_message}"}, "result": None},
        status_code=code)


@web_app.get("/")
async def index():
    log.debug("Request IndexPage;")
    return response("Index page")


@web_app.get("/method/{method}")
async def _method(method, secret_key: str = None):
    # log.debug(f"Request method; kwargs: {kwargs}")
    is_auth = secret_key == config.WebAPI["secret_key"]
    spl = method.split(".")
    if len(spl) != 2:
        raise StarletteHTTPException(405)
    api_class, api_method = spl
    match api_class:
        case "events":
            match api_method, is_auth:
                case "get", False:
                    return response(data_pool)
    raise StarletteHTTPException(404)


async def _stop():
    await asyncio.sleep(1)
    uvserver.should_exit = True
    data_run[0] = False


@web_app.get("/stop")
async def stop(secret_key: str):
    log.debug(f"Request stop; secret key: {secret_key}")
    if secret_key == config.WebAPI["secret_key"]:
        log.info("Stopping Web server")
        asyncio.create_task(_stop())
        return response("Web server stopped")


@web_app.exception_handler(HTTPException)
async def default_exception_handler(request: Request, exc: HTTPException):
    return response(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=exc.status_code, error_message=f"Internal Server Error: {exc.status_code}"
    )


@web_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = exc.status_code
    if code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return response(code=code, error_message="Method Not Allowed")
    if code == status.HTTP_404_NOT_FOUND:
        return response(code=code, error_message="Method not Found")
    return response(code=code, error_message="Unhandled error..")


@web_app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return response(code=code, error_message="Request Validation Error")


utils.hack_fastapi()

if __name__ == '__main__':
    try:
        uvconfig = uvicorn.Config(web_app,
                                  host=config.WebAPI["server_ip"],
                                  port=config.WebAPI["server_port"],
                                  loop="asyncio")
        uvserver = uvicorn.Server(uvconfig)
        uvserver.run()
    except KeyboardInterrupt or CancelledError:
        pass
