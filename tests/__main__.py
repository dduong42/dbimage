import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
execute_from_command_line(['django-admin', 'migrate'])
TestRunner = get_runner(settings)
test_runner = TestRunner()
failures = test_runner.run_tests(["tests"])
sys.exit(bool(failures))
