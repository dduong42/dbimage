from django.http import Http404
from django.test import TestCase, RequestFactory
from dbimage.views import ServeImageView
from dbimage.models import DBImage

serve_image = ServeImageView.as_view()
request = RequestFactory().get('/')


class TestServeImageView(TestCase):
    def setUp(self):
        self.path = 'path.png'
        self.content = b'binary-content'
        self.content_type = 'image/png'
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
