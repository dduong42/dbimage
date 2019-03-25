from datetime import datetime
from unittest import mock

from dbimage.models import DBImage
from dbimage.views import ServeImageView
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.utils.http import http_date

serve_image = ServeImageView.as_view()
request = RequestFactory().get('/')


class TestServeImageView(TestCase):
    def setUp(self):
        self.path = 'path.png'
        self.content = b'binary-content'
        self.content_type = 'image/png'
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(year=1991, month=11, day=16)
            self.image = DBImage.objects.create(
                path=self.path,
                content_type=self.content_type,
                content=self.content,
            )

    def test_404(self):
        with self.assertRaises(Http404):
            serve_image(request, 'unknown')

    def test_content_is_good(self):
        response = serve_image(request, self.path)
        self.assertEqual(response.content, self.content)

    def test_content_type_is_good(self):
        response = serve_image(request, self.path)
        self.assertEqual(response['Content-Type'], self.content_type)

    def test_cache_is_good(self):
        response = serve_image(request, self.path)
        elements = response['Cache-Control'].split(', ')
        self.assertIn('public', elements)
        self.assertIn('max-age=315360000', elements)
        self.assertIn('immutable', elements)

    def test_modified_since(self):
        date = datetime(year=1991, month=11, day=17)
        http_d = http_date(date.timestamp())
        request = RequestFactory().get(
            '/', HTTP_IF_MODIFIED_SINCE=http_d)
        response = serve_image(request, self.path)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.content, b'')

    def test_modified_since_older_date(self):
        date = datetime(year=1991, month=11, day=15)
        http_d = http_date(date.timestamp())
        request = RequestFactory().get(
            '/', HTTP_IF_MODIFIED_SINCE=http_d)
        response = serve_image(request, self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.content)
