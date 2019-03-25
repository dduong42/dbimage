from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.cache import patch_cache_control
from django.views.decorators.http import condition
from django.views.generic import View
from datetime import datetime
from .models import AbstractDBImage, DBImage


def get_last_modified(request: HttpRequest, path: str) -> datetime:
    return DBImage.objects.filter(path=path)\
        .values_list('modified_on', flat=True)\
        .first()


class ServeImageView(View):
    model = DBImage

    # Taken from whitenoise:
    # Ten years is what nginx sets a max age if you use 'expires max;'
    # so we'll follow its lead
    forever = 10*365*24*60*60

    def get(self, request: HttpRequest, path: str) -> HttpResponse:
        image: AbstractDBImage = get_object_or_404(self.model, path=path)
        response = HttpResponse(image.content, content_type=image.content_type)
        # For immutable, it's not in the standards
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#Browser_compatibility
        patch_cache_control(response, public=True, max_age=self.forever, immutable=True)
        response['ETag'] = image.etag
        return response

    @classmethod
    def as_view(cls, **initkwargs):
        return condition(last_modified_func=get_last_modified)(
            super().as_view(**initkwargs))
