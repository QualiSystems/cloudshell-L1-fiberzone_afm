import re

import fiberzone_afm.command_templates.autoload as command_template_autoload
import fiberzone_afm.command_templates.mapping as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from fiberzone_afm.helpers.command_actions_helper import CommandActionsHelper


class MappingActions(object):
    """
    Autoload actions
    """

    def __init__(self, cli_service, logger):
        """
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def connect(self, src_port, dst_port):
        """
        Connect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.CONNECT).execute_command(src_port=src_port,
                                                                                                      dst_port=dst_port)
        return output

    def disconnect(self, src_port, dst_port):
        """
        Disconnect ports
        :param src_port:
        :param dst_port:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.DISCONNECT).execute_command(
            src_port=src_port,
            dst_port=dst_port)
        return output

    def port_locked(self, port_id):
        port_output = CommandTemplateExecutor(self._cli_service,
                                              command_template_autoload.PORT_SHOW).execute_command()

        for record in CommandActionsHelper.parse_table(port_output.strip(),
                                                       r'^e{0}\s+\d+\s+\d+\s+\d+\s+w{0}.*$'.format(port_id)):
            if record[1] == '2':
                return True
            else:
                return False
        raise Exception(self.__class__.__name__, "Cannot find port {}".format(port_id))

    def port_connected(self, port_id):
        port_connected_output = CommandTemplateExecutor(self._cli_service,
                                                        command_template.CONNECTIONS).execute_command()

        for record in CommandActionsHelper.parse_table(port_connected_output.strip(),
                                                       r'^e{}\s+w\d+\s+\w+\d+\s+.*$'.format(port_id)):
            port_id = re.sub(r'\D', '', record[1], re.IGNORECASE)
            return port_id
