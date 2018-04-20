#!/usr/bin/env python
# coding: utf-8
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler.settings')

from django.core import management


def main():
    management.execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
