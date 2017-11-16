#!/usr/bin/python
# -*- coding: utf-8 -*-

import fiberzone_afm.command_templates.autoload as command_template
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor


class AutoloadActions(object):
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

    def board_info(self):
        """
        Chassis table
        :return: list of chassis data, [{'index': '1', 'model': 'MRV Chassis', 'serial': '1ndsKsf'}, ]
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_BOARD).execute_command()
        return output

    def ports_info(self):
        """
        Chassis table
        :return: list of chassis data, [{'index': '1', 'model': 'MRV Chassis', 'serial': '1ndsKsf'}, ]
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.PORT_SHOW).execute_command()
        return output
