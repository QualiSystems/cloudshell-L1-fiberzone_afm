from unittest import TestCase

from mock import patch, Mock

from main import Main


class TestMain(TestCase):
    def setUp(self):
        self._driver_path = Mock()
        self._port = Mock()
        self._log_path = Mock()
        self._instance = self._create_instance()

    @patch('main.os')
    @patch('main.sys')
    def _create_instance(self, sys_mod, os_mod):
        os_mod.path.dirname.return_value = self._driver_path
        return Main(None, self._port, self._log_path)

    @patch('main.os')
    @patch('main.sys')
    def test_init(self, sys_mod, os_mod):
        file_path = Mock()
        os_mod.path.dirname.return_value = self._driver_path
        os_mod.environ = {}
        instance = Main(file_path, self._port, self._log_path)
        os_mod.path.dirname.assert_called_once_with(file_path)
        self.assertIs(instance._driver_path, self._driver_path)
        self.assertIs(instance._log_path, self._log_path)
        self.assertIs(os_mod.environ.get('LOG_PATH'), self._log_path)

    @patch('main.os')
    @patch('main.sys')
    def test_init_default_values(self, sys_mod, os_mod):
        file_path = Mock()
        os_mod.path.dirname.return_value = self._driver_path
        args = [file_path]
        sys_mod.argv = args
        os_mod.path.join.return_value = self._log_path
        os_mod.environ = {}
        instance = Main(None, self._port, None)
        os_mod.path.dirname.assert_called_once_with(file_path)
        os_mod.path.join.assert_called_once_with(self._driver_path, '..', 'Logs')
        self.assertIs(instance._driver_path, self._driver_path)
        self.assertIs(instance._log_path, self._log_path)
        self.assertIs(os_mod.environ.get('LOG_PATH'), self._log_path)

    # @patch('main.os')
    # @patch('main.importlib')
    # @patch('main.datetime')
    # @patch('main.RuntimeConfiguration')
    # @patch('main.XMLLogger')
    # @patch('main.get_qs_logger')
    # @patch('main.DriverCommands')
    # @patch('main.CommandExecutor')
    # @patch('main.DriverListener')
    # def test_run_driver(self, driver_listener_class, command_executor_class, driver_commands_class,
    #                     get_qs_logger_mod, xml_logger_class, runtime_configuration_class, datetime_mod, importlib_mod, os_mod):
    #     config_path = Mock()
    #     xml_log_path = Mock()
    #     os_mod.path.join.side_effect = [config_path, xml_log_path]
    #     runtime_config_instance = Mock()
    #     runtime_configuration_class.return_value = runtime_config_instance
    #     driver_name = Mock()
    #     self._instance.run_driver(driver_name)
