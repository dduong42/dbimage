from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.utils.cache import patch_cache_control

from .models import AbstractDBImage, DBImage


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
        return response
