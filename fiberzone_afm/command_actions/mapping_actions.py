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

    def ports_info(self, *port_ids):
        self._logger.debug('Getting ports info for ports {}'.format(', '.join(port_ids)))
        port_output = CommandTemplateExecutor(self._cli_service,
                                              command_template_autoload.PORT_SHOW).execute_command()
        ports_info = []

        for port_id in port_ids:
            pattern = r'^e{0}\s+\d+\s+\d+\s+\d+\s+w{0}.*$'.format(port_id)
            match_list = CommandActionsHelper.parse_table(port_output.strip(), pattern)
            if len(match_list) == 1:
                record = match_list[0]
                port_info = {'id': port_id,
                             'connected': re.sub(r'\D', '', record[5], re.IGNORECASE) if record[2] == '2' else None,
                             'locked': record[1] == '2',
                             'disabled': record[3] == '2'}
                ports_info.append(port_info)
            else:
                raise Exception(self.__class__.__name__, 'Cannot find port with id {}'.format(port_id))
        return ports_info
