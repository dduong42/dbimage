from datetime import datetime
from unittest import mock

from dbimage.models import DBImage
from dbimage.views import ServeImageView
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.utils.http import http_date

serve_image = ServeImageView.as_view()


class TestDBImage(TestCase):
    def test_jpg(self):
        image = DBImage(path='image.jpg')
        self.assertEqual(image.content_type(), 'image/jpeg')

    def test_jpeg(self):
        image = DBImage(path='image.jpeg')
        self.assertEqual(image.content_type(), 'image/jpeg')

    def test_jpg_upper(self):
        image = DBImage(path='image.JPG')
        self.assertEqual(image.content_type(), 'image/jpeg')

    def test_jpg_plus_noise(self):
        image = DBImage(path='image.noise.jpg')
        self.assertEqual(image.content_type(), 'image/jpeg')

    def test_jpg_unknown(self):
        image = DBImage(path='image.unknown')
        self.assertEqual(image.content_type(), 'application/octet-stream')

    def test_jpg_with_dir(self):
        image = DBImage(path='directory/image.jpg')
        self.assertEqual(image.content_type(), 'image/jpeg')

    def test_from_filename_and_content(self):
        image = DBImage.create_from_path_and_content(
            path='image.jpg',
            content=b'content',
        )
        self.assertEqual(image.etag, '"9a0364b9e99bb480dd25e1f0284c8555"')
        self.assertEqual(image.path, 'image.9a0364b9e99b.jpg')

    def test_from_path_and_content_with_dir(self):
        image = DBImage.create_from_path_and_content(
            path='directory/image.jpg',
            content=b'content',
        )
        self.assertEqual(image.etag, '"9a0364b9e99bb480dd25e1f0284c8555"')
        self.assertEqual(image.path, 'directory/image.9a0364b9e99b.jpg')


class TestServeImageView(TestCase):
    def setUp(self):
        self.path = 'path.png'
        self.content = b'binary-content'
        self.content_type = 'image/png'
        self.etag = '"123"'
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime(year=1991, month=11, day=16)
            self.image = DBImage.objects.create(
                path=self.path,
                content=self.content,
                etag=self.etag,
            )

    def test_404(self):
        request = RequestFactory().get('/')
        with self.assertRaises(Http404):
            serve_image(request, 'unknown')

    def test_content_is_good(self):
        request = RequestFactory().get('/')
        response = serve_image(request, self.path)
        self.assertEqual(response.getvalue(), self.content)

    def test_content_type_is_good(self):
        request = RequestFactory().get('/')
        response = serve_image(request, self.path)
        self.assertEqual(response['Content-Type'], self.content_type)

    def test_cache_is_good(self):
        request = RequestFactory().get('/')
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
        self.assertEqual(response.getvalue(), b'')

    def test_modified_since_older_date(self):
        date = datetime(year=1991, month=11, day=15)
        http_d = http_date(date.timestamp())
        request = RequestFactory().get(
            '/', HTTP_IF_MODIFIED_SINCE=http_d)
        response = serve_image(request, self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.getvalue(), self.content)

    def test_response_returns_etag(self):
        request = RequestFactory().get('/')
        response = serve_image(request, self.path)
        self.assertEqual(response['ETag'], self.etag)

    def test_304_etag(self):
        request = RequestFactory().get(
            '/', HTTP_IF_NONE_MATCH=self.etag)
        response = serve_image(request, self.path)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.getvalue(), b'')

    def test_200_etag(self):
        request = RequestFactory().get(
            '/', HTTP_IF_NONE_MATCH='"456"')
        response = serve_image(request, self.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.getvalue(), self.content)
