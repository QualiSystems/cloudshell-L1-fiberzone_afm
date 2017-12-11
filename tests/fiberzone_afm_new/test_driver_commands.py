from unittest import TestCase

from mock import Mock

from fiberzone_afm_new.driver_commands import DriverCommands


class TestDriverCommands(TestCase):
    def setUp(self):
        self._logger = Mock()
        self._instance = DriverCommands(self._logger)
