import os.path

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'dbimage',
    'tests',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_DIR, 'db.sqlite3'),
    },
}
