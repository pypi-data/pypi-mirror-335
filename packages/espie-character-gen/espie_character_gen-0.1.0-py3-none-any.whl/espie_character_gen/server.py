import os
from typing import Type, TypeVar
from fastapi import Depends, FastAPI, HTTPException, Request
from importlib.metadata import version

from fastapi.responses import JSONResponse, RedirectResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from espie_character_gen import configs
from espie_character_gen.rest_app.authentication import (
    get_verifier,
    token_auth_scheme,
)
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend

from espie_character_gen.rest_app.model import AppSession
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException


class BasicVerifier(SessionVerifier[UUID, AppSession]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, AppSession],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: AppSession) -> bool:
        """If the session exists, it is valid"""
        return True


backend = InMemoryBackend[UUID, AppSession]()
verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=False,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="pookie",
    identifier="general_verifier",
    auto_error=False,
    secret_key=configs.secret_key,
    cookie_params=cookie_params,
)

try:
    _version = version("espie_character_gen")
except:  # pragma: no cover
    _version = "dev"

fastapi_app = FastAPI(
    title="Espie Character Gen API",
    version=_version,
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.cors_origins,
    allow_credentials=configs.cors_allow_credentials,
    allow_methods=configs.cors_methods,
    allow_headers=configs.cors_headers,
)


@fastapi_app.middleware("http")
async def hydrate_user(
    request: Request,
    call_next,
):
    try:
        token = await token_auth_scheme(request)
    except HTTPException as e:
        if e.detail == "Not authenticated":
            return await call_next(request)
        return JSONResponse(
            {"status": "error", "message": "Not Authenticated"}, status_code=401
        )

    result = get_verifier().verify(token.credentials)

    if result.get("status"):
        return JSONResponse(result, status_code=403)
    request.state.user = result
    return await call_next(request)


@fastapi_app.get("/healthz")
def healthz():
    return {"o": "k"}


@fastapi_app.get("/version")
def version():
    return {"version": _version}


@fastapi_app.get("/me")
def get_me(request: Request):
    return getattr(request.state, "user", None)


templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


def link(url: str, name: str):
    return {"url": url, "name": name}


SHARED_LINKS = [
    link("/", "Home"),
    link("/about", "About"),
    link("/contact", "Contact"),
]

LOGGED_OUT_LINKS = [
    *SHARED_LINKS,
    link("/login", "Login"),
]

LOGGED_IN_LINKS = [
    *SHARED_LINKS,
    link("/logout", "Logout"),
]


def context(*, is_logged_in: bool = False, **kwargs):
    return {
        **kwargs,
        "links": LOGGED_IN_LINKS if is_logged_in else LOGGED_OUT_LINKS,
    }


@fastapi_app.get("/", dependencies=[Depends(cookie)])
def index(request: Request, data: AppSession = Depends(verifier)):
    print(data)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context(
            name=getattr(data, "username", "Billy Ichiban"),
            is_logged_in=data is not None,
        ),
    )


class LoginCreds(BaseModel):
    username: str
    password: str


_TModel = TypeVar("_TModel", bound=BaseModel)


def form_or_json(model: Type[_TModel]) -> _TModel:
    async def form_or_json_inner(request: Request) -> _TModel:
        type_ = request.headers["Content-Type"].split(";", 1)[0]
        if type_ == "application/json":
            data = await request.json()
        elif type_ == "application/x-www-form-urlencoded":
            data = await request.form()
        else:
            raise HTTPException(400)
        return model.model_validate(data)

    return Depends(form_or_json_inner)


@fastapi_app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=context(is_logged_in=False),
    )


@fastapi_app.post("/login")
async def login(request: Request, login_request: LoginCreds = form_or_json(LoginCreds)):
    if not login_request.password or login_request.password == "failure":
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    session = uuid4()
    data = AppSession(
        username=login_request.username,
    )
    await backend.create(session, data)

    if request.headers["Content-Type"] == "application/json":
        response = JSONResponse({"session": str(session)})
    else:
        response = RedirectResponse("/", status_code=302)

    cookie.attach_to_response(response, session)
    return response


@fastapi_app.get("/logout")
async def logout(session_id: UUID = Depends(cookie)):
    response = RedirectResponse("/", status_code=302)
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return response


@fastapi_app.get("/{path:path}")
def catch_all(path: str):
    return RedirectResponse(url="/", status_code=302)
