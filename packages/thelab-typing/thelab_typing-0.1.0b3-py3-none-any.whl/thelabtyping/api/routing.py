from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from functools import reduce
from operator import or_
from typing import Concatenate, NewType

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponseBase, HttpResponseNotAllowed
from django.urls import URLPattern, path


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


URLPatternStr = NewType("URLPatternStr", str)
AllowedMethods = set[HttpMethod]

type ViewFn[**P, R: HttpResponseBase] = Callable[Concatenate[HttpRequest, P], R]

ALL_METHODS: AllowedMethods = {
    HttpMethod.GET,
    HttpMethod.POST,
    HttpMethod.PUT,
    HttpMethod.PATCH,
    HttpMethod.DELETE,
}


@dataclass
class RegisteredView[**P, R: HttpResponseBase]:
    methods: AllowedMethods
    fn: ViewFn[P, R]


@dataclass
class Route:
    name: str
    views: list[RegisteredView[[], HttpResponseBase]]

    def __init__(self, name: str) -> None:
        self.name = name
        self.views = []

    def get[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        return self.register({HttpMethod.GET})(fn)

    def post[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        return self.register({HttpMethod.POST})(fn)

    def put[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        return self.register({HttpMethod.PUT})(fn)

    def patch[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        return self.register({HttpMethod.PATCH})(fn)

    def delete[**P, R: HttpResponseBase](self, fn: ViewFn[P, R]) -> ViewFn[P, R]:
        return self.register({HttpMethod.DELETE})(fn)

    def register[**P, R: HttpResponseBase](
        self,
        methods: AllowedMethods = ALL_METHODS,
    ) -> Callable[
        [ViewFn[P, R]],
        ViewFn[P, R],
    ]:
        def decorator(view_fn: ViewFn[P, R]) -> ViewFn[P, R]:
            self.add_view(view_fn, methods)
            return view_fn

        return decorator

    def add_view[**P, R: HttpResponseBase](
        self,
        view_fn: ViewFn[P, R],
        methods: AllowedMethods,
    ) -> None:
        conflicts = self.allowed_methods & methods
        if conflicts:
            raise ImproperlyConfigured(
                f"Cannot {view_fn} for methods {conflicts}. Views already "
                "exist for these methods."
            )
        self.views.append(
            RegisteredView(
                methods=methods,
                fn=view_fn,
            )
        )

    def dispatch(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponseBase:
        for view in self.views:
            if request.method in view.methods:
                return view.fn(request, *args, **kwargs)

        return HttpResponseNotAllowed(self.allowed_methods)

    @property
    def allowed_methods(self) -> AllowedMethods:
        return reduce(or_, (view.methods for view in self.views), set())


type RouteMap = dict[URLPatternStr, Route]


class Router:
    basename: str | None = None
    routes: RouteMap

    def __init__(self, basename: str | None = None) -> None:
        self.basename = basename
        self.routes: RouteMap = {}

    def route[**P, R: HttpResponseBase](
        self,
        url_pattern: str,
        name: str,
        get: ViewFn[P, R] | None = None,
        post: ViewFn[P, R] | None = None,
        put: ViewFn[P, R] | None = None,
        patch: ViewFn[P, R] | None = None,
        delete: ViewFn[P, R] | None = None,
    ) -> Route:
        _pattern = URLPatternStr(url_pattern)
        if _pattern in self.routes:
            raise ImproperlyConfigured(
                f"Cannot add route {_pattern} to router. Route already exists."
            )
        # Create route
        name = f"{self.basename}-{name}" if self.basename is not None else name
        route = Route(name)
        # Register any provided views
        views: dict[HttpMethod, ViewFn[P, R] | None] = {
            HttpMethod.GET: get,
            HttpMethod.POST: post,
            HttpMethod.PUT: put,
            HttpMethod.PATCH: patch,
            HttpMethod.DELETE: delete,
        }
        for method, view in views.items():
            if view is not None:
                route.register({method})(view)
        # Save and return the view
        self.routes[_pattern] = route
        return self.routes[_pattern]

    @property
    def urls(self) -> list[URLPattern]:
        return [
            path(pattern, route.dispatch, name=route.name)
            for pattern, route in self.routes.items()
        ]
