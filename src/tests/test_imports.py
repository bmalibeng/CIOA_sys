import pytest
from django.test import TestCase
from students.management.commands.import_continuous import Command
from unittest.mock import MagicMock, patch
from students.models import Program


class ImportCommandTests(TestCase):
    def test_command_initialization(self):
        cmd = Command()
        self.assertEqual(cmd.help, 'Import continuous data from Excel file')

    def test_program_import_dry_run(self):
        cmd = Command()
        stats = cmd.import_programs(MagicMock(), dry_run=True, update_existing=False)
        self.assertIn('created', stats)
