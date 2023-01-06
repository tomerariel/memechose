import json
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators import http, csrf
from api.services import url_service
from api.utils import request_handler


@http.require_safe
@request_handler
def health(_) -> HttpResponse:
    return HttpResponse(status=200, content="OK")


@csrf.csrf_exempt
@http.require_POST
@request_handler
def create_url(request: HttpRequest) -> JsonResponse:
    url = json.loads(request.body).get("url")
    short_url = url_service.create_short_url(url)
    return JsonResponse(
        status=201,
        data={"url": short_url},
    )


@http.require_safe
@request_handler
def redirect_to_original_url(_, url: str) -> HttpResponseRedirect:
    redirect_url = url_service.get_redirect_url(url)
    return HttpResponseRedirect(redirect_to=redirect_url)
