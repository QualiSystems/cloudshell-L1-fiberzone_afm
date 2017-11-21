#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

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

    def board_table(self):
        """
        Chassis table
        :return: list of chassis data, [{'index': '1', 'model': 'MRV Chassis', 'serial': '1ndsKsf'}, ]
        :rtype: list
        """
        board_table = {}
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_BOARD).execute_command()
        serial_search = re.search(r'BOARD\s+.*S/N\((.+?)\)', output, re.DOTALL)
        if serial_search:
            board_table['serial_number'] = serial_search.group(1)

        max_port_east_search = re.search(r'MAX_PORT_EAST\s+(\d+)', output, re.DOTALL)
        max_port_west_search = re.search(r'MAX_PORT_WEST\s+(\d+)', output, re.DOTALL)
        if max_port_east_search and max_port_west_search:
            max_port_east = max_port_east_search.group(1)
            max_port_west = max_port_west_search.group(1)
            board_table['model_name'] = "AFM-360-{0}X{1}".format(max_port_east, max_port_west)

        sw_version_search = re.search(r'ACTIVE\s+SW\s+VER\s+(\d+\.\d+\.\d+\.\d+)', output, re.DOTALL)
        if sw_version_search:
            board_table['sw_version'] = sw_version_search.group(1)

        return board_table

    def ports_table(self):
        """
        Chassis table
        :return: list of chassis data, [{'index': '1', 'model': 'MRV Chassis', 'serial': '1ndsKsf'}, ]
        :rtype: list
        """
        port_table = {}
        port_logic_output = CommandTemplateExecutor(self._cli_service,
                                                    command_template.PORT_SHOW_LOGIC_TABLE).execute_command()

        for record in self._parse_table(port_logic_output.strip(), r'^\d+\s+\d+\s+\w+\s+\w+\s+\w+$'):
            port_table[record[0]] = {'blade': record[2]}

        port_output = CommandTemplateExecutor(self._cli_service,
                                              command_template.PORT_SHOW).execute_command()

        for record in self._parse_table(port_output.strip(), r'^\w+\s+\d+\s+\d+\s+\d+\s+\w+.*$'):
            record_id = re.sub(r'[eE]', '', record[0])
            if record_id in port_table:
                port_table[record_id]['locked'] = True if record[1] == '2' else False
                if len(record) > 7:
                    port_table[record_id]['connected'] = re.sub(r'[wW]', '', record[5])
                else:
                    port_table[record_id]['connected'] = None
        return port_table

    @staticmethod
    def _parse_table(data, pattern):
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        table = []
        for record in data.split('\r\n'):
            matched = re.search(compiled_pattern, record)
            if matched:
                table.append(re.split(r'\s+', matched.group(0)))
        return table
