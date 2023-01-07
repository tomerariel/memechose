import json

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators import csrf, http

from api.decorators import request_handler
from api.services import url_service


@http.require_safe
@request_handler
def health(_) -> HttpResponse:
    return HttpResponse(status=200, content="OK")


@csrf.csrf_exempt
@http.require_POST
@request_handler
def create_url(request: HttpRequest) -> JsonResponse:
    url = json.loads(request.body).get("url")
    short_url = url_service.get_or_create_short_url(url)
    return JsonResponse(
        status=201,
        data={"url": short_url},
    )


@http.require_safe
@request_handler
def redirect_to_original_url(_, url: str) -> HttpResponseRedirect:
    redirect_url = url_service.get_redirect_url(url)
    return HttpResponseRedirect(redirect_to=redirect_url)
