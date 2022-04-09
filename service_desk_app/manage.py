#!/usr/bin/env python3

import os
import sys
import config


def main():  # Django command-line utility for administrative tasks
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as err_msg:
        raise ImportError("Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?") from err_msg
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
