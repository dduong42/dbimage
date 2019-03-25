import hashlib
import os.path

from django.db import models


class AbstractDBImage(models.Model):
    path = models.CharField(max_length=255, unique=True)
    modified_on = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=255)
    content = models.BinaryField()

    extensions = {
        '.bmp': 'image/x-ms-bmp',
        '.gif': 'image/gif',
        '.ico': 'image/x-icon',
        '.jng': 'image/x-jng',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.svg': 'image/svg+xml',
        '.svgz': 'image/svg+xml',
        '.tif': 'image/tiff',
        '.tiff': 'image/tiff',
        '.wbmp': 'image/vnd.wap.wbmp',
        '.webp': 'image/webp',
    }
    default_type = 'application/octet-stream'

    @staticmethod
    def get_hash(content: bytes) -> str:
        return hashlib.md5(content).hexdigest()

    @classmethod
    def create_from_filename_and_content(cls, filename: str, content: bytes) -> 'AbstractDBImage':
        hash = cls.get_hash(content)
        name, ext = os.path.splitext(filename)
        path = f'{name}.{hash[:12]}{ext}'
        etag = f'"{hash}"'
        return cls.objects.create(
            path=path,
            content=content,
            etag=etag,
        )

    def content_type(self) -> str:
        ext = os.path.splitext(self.path)[1].lower()
        return self.extensions.get(ext, self.default_type)

    class Meta:
        abstract = True


class DBImage(AbstractDBImage):
    pass
