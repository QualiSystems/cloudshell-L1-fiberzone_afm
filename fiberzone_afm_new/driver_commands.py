#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import os

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.layer_one.core.response.response_info import GetStateIdResponseInfo, ResourceDescriptionResponseInfo, \
    AttributeValueResponseInfo
from fiberzone_afm_new.cli.fiberzone_cli_handler import FiberzoneCliHandler
from fiberzone_afm_new.command_actions.autoload_actions import AutoloadActions
from fiberzone_afm_new.command_actions.mapping_actions import MappingActions
from fiberzone_afm_new.helpers.autoload_helper import AutoloadHelper
from fiberzone_afm_new.helpers.test_cli import TestCliHandler


class PortsPartiallyConnectedException(Exception):
    pass


class DriverCommands(DriverCommandsInterface):
    """
    Driver commands implementation
    """

    def __init__(self, logger):
        """
        :param logger:
        :type logger: logging.Logger
        """
        self._logger = logger
        self._cli_handler = FiberzoneCliHandler(logger)
        # self._cli_handler = TestCliHandler(
        #      os.path.join(os.path.dirname(__file__), 'helpers', 'test_fiberzone_data'), logger)

        self._mapping_timeout = RuntimeConfiguration().read_key('MAPPING.TIMEOUT')
        self._mapping_check_delay = RuntimeConfiguration().read_key('MAPPING.CHECK_DELAY')

    def login(self, address, username, password):
        """
        Perform login operation on the device
        :param address: resource address, "192.168.42.240"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        Example:
            # Define session attributes
            self._cli_handler.define_session_attributes(address, username, password)

            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Executing simple command
                device_info = session.send_command('show version')
                self._logger.info(device_info)
        """
        self._cli_handler.define_session_attributes(address, username, password)
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            self._logger.info('Connected to ' + autoload_actions.board_table().get('model_name'))

    def get_state_id(self):
        """
        Check if CS synchronized with the device.
        :return: Synchronization ID, GetStateIdResponseInfo(-1) if not used
        :rtype: cloudshell.layer_one.core.response.response_info.GetStateIdResponseInfo
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Execute command
                chassis_name = session.send_command('show chassis name')
                return chassis_name
        """
        return GetStateIdResponseInfo('-1')

    def set_state_id(self, state_id):
        """
        Set synchronization state id to the device, called after Autoload or SyncFomDevice commands
        :param state_id: synchronization ID
        :type state_id: str
        :return: None
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.config_mode_service() as session:
                # Execute command
                session.send_command('set chassis name {}'.format(state_id))
        """
        pass

    def map_bidi(self, src_port, dst_port):
        """
        Create a bidirectional connection between source and destination ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_port: dst port address, '192.168.42.240/1/22'
        :type dst_port: str
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                session.send_command('map bidir {0} {1}'.format(convert_port(src_port), convert_port(dst_port)))

        """
        self._logger.info('MapBidi, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_port))
        src_port_id = self._convert_port(src_port)
        dst_port_id = self._convert_port(dst_port)
        self._connect_ports(src_port_id, dst_port_id)

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/22', '192.168.42.240/1/23']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                for dst_port in dst_ports:
                    session.send_command('map {0} also-to {1}'.format(convert_port(src_port), convert_port(dst_port)))
        """
        raise Exception(self.__class__.__name__, 'Unidirectional connections are not allowed')

    def get_resource_description(self, address):
        """
        Auto-load function to retrieve all information from the device
        :param address: resource address, '192.168.42.240'
        :type address: str
        :return: resource description
        :rtype: cloudshell.layer_one.core.response.response_info.ResourceDescriptionResponseInfo
        :raises cloudshell.layer_one.core.layer_one_driver_exception.LayerOneDriverException: Layer one exception.

        Example:

            from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
            from cloudshell.layer_one.core.response.resource_info.entities.blade import Blade
            from cloudshell.layer_one.core.response.resource_info.entities.port import Port

            chassis_resource_id = chassis_info.get_id()
            chassis_address = chassis_info.get_address()
            chassis_model_name = "Fiberzone Afm Chassis"
            chassis_serial_number = chassis_info.get_serial_number()
            chassis = Chassis(resource_id, address, model_name, serial_number)

            blade_resource_id = blade_info.get_id()
            blade_model_name = 'Generic L1 Module'
            blade_serial_number = blade_info.get_serial_number()
            blade.set_parent_resource(chassis)

            port_id = port_info.get_id()
            port_serial_number = port_info.get_serial_number()
            port = Port(port_id, 'Generic L1 Port', port_serial_number)
            port.set_parent_resource(blade)

            return ResourceDescriptionResponseInfo([chassis])
        """
        with self._cli_handler.default_mode_service() as session:
            autoload_actions = AutoloadActions(session, self._logger)
            board_table = autoload_actions.board_table()
            ports_table = autoload_actions.ports_table()
            autoload_helper = AutoloadHelper(address, board_table, ports_table, self._logger)
            response_info = ResourceDescriptionResponseInfo(autoload_helper.build_structure())
            return response_info

    @staticmethod
    def _convert_port(cs_port):
        return cs_port.split('/')[-1]

    def _get_connected_port(self, port_info):
        """
        Get connected
        :param port_info:
        :type port_info: fiberzone_afm.entities.port_entities.PortInfo
        :return:
        """
        east_connected = port_info.east_port.connected
        west_connected = port_info.west_port.connected
        if east_connected and west_connected:
            if east_connected == west_connected:
                return east_connected
            else:
                raise Exception(self.__class__.__name__,
                                'Port {} East and West connected to a different port ids'.format(port_info.port_id))
        elif not east_connected and not west_connected:
            return None
        else:
            raise PortsPartiallyConnectedException(self.__class__.__name__,
                                                   'Port {} partially connected'.format(port_info.port_id))

    def _check_port_locked_or_disabled(self, port_info):
        """
        Check disabled or locked
        :param port_info:
        :type port_info: fiberzone_afm.entities.port_entities.PortInfo
        :return:
        """
        if port_info.east_port.locked or port_info.west_port.locked:
            raise Exception(self.__class__.__name__, 'Port {} is locked'.format(port_info.port_id))
        if port_info.east_port.disabled or port_info.west_port.disabled:
            raise Exception(self.__class__.__name__, 'Port {} is disabled'.format(port_info.port_id))

    def _connect_ports(self, src_port_id, dst_port_id):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            src_port_info, dst_port_info = mapping_actions.ports_info(src_port_id, dst_port_id)
            self._check_port_locked_or_disabled(src_port_info)
            self._check_port_locked_or_disabled(dst_port_info)
            if self._get_connected_port(src_port_info) or self._get_connected_port(dst_port_info):
                raise Exception(self.__class__.__name__,
                                'Port {0}, or port {1} has already been connected'.format(src_port_id, dst_port_id))
            mapping_actions.connect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                src_port_info, dst_port_info = mapping_actions.ports_info(src_port_id, dst_port_id)
                self._check_port_locked_or_disabled(src_port_info)
                self._check_port_locked_or_disabled(dst_port_info)
                try:
                    if self._get_connected_port(src_port_info) == dst_port_id and self._get_connected_port(
                            dst_port_info) == src_port_id:
                        return
                    else:
                        time.sleep(self._mapping_check_delay)
                except PortsPartiallyConnectedException:
                    time.sleep(self._mapping_check_delay)

        raise Exception(self.__class__.__name__,
                        'Cannot connect port {0} to port {1} during {2}sec'.format(src_port_id, dst_port_id,
                                                                                   self._mapping_timeout))

    def _disconnect_ports(self, *ports):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            if len(ports) == 1:
                src_port_id = ports[0]
                src_port_info, = mapping_actions.ports_info(src_port_id)
                dst_port_id = self._get_connected_port(src_port_info)
                if not dst_port_id:
                    return
                dst_port_info, = mapping_actions.ports_info(dst_port_id)
            else:
                src_port_id = ports[0]
                dst_port_id = ports[1]
                src_port_info, dst_port_info = mapping_actions.ports_info(src_port_id, dst_port_id)

            if not self._get_connected_port(src_port_info) and not self._get_connected_port(dst_port_info):
                return

            if self._get_connected_port(src_port_info) != dst_port_id:
                raise Exception(
                    'Port {0} is not connected or connected not to port {1}'.format(src_port_id, dst_port_id))

            if self._get_connected_port(dst_port_info) != src_port_id:
                raise Exception(
                    'Port {0} is not connected or connected not to port {1}'.format(dst_port_id, src_port_id))

            self._check_port_locked_or_disabled(src_port_info)
            self._check_port_locked_or_disabled(dst_port_info)

            mapping_actions.disconnect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                src_port_info, dst_port_info = mapping_actions.ports_info(src_port_id, dst_port_id)
                self._check_port_locked_or_disabled(src_port_info)
                self._check_port_locked_or_disabled(dst_port_info)
                try:
                    if not self._get_connected_port(src_port_info) and not self._get_connected_port(dst_port_info):
                        return
                    else:
                        time.sleep(self._mapping_check_delay)
                except PortsPartiallyConnectedException:
                    time.sleep(self._mapping_check_delay)

            raise Exception(self.__class__.__name__,
                            'Cannot disconnect port {0} from port {1} during {2}sec'.format(src_port_id, dst_port_id,
                                                                                            self._mapping_timeout))

    def map_clear(self, ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param ports: ports, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
            for port in ports:
                session.send_command('map clear {}'.format(convert_port(port)))
        """
        self._logger.info('MapClear, Ports: {}'.format(', '.join(ports)))
        exception_messages = []
        for src_port in ports:
            try:
                src_port_id = self._convert_port(src_port)
                self._disconnect_ports(src_port_id)
            except Exception as e:
                if len(e.args) > 1:
                    exception_messages.append(e.args[1])
                elif len(e.args) == 1:
                    exception_messages.append(e.args[0])

        if exception_messages:
            raise Exception(self.__class__.__name__, ', '.join(exception_messages))

    def map_clear_to(self, src_port, dst_ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                _src_port = convert_port(src_port)
                for port in dst_ports:
                    _dst_port = convert_port(port)
                    session.send_command('map clear-to {0} {1}'.format(_src_port, _dst_port))
        """
        if len(dst_ports) != 1:
            raise Exception(self.__class__.__name__, 'MapClearTo operation is not allowed for multiple Dst ports')
        self._logger.info('MapClearTo, SrcPort: {0}, DstPort: {1}'.format(src_port, dst_ports[0]))
        src_port_id = self._convert_port(src_port)
        dst_port_id = self._convert_port(dst_ports[0])
        self._disconnect_ports(src_port_id, dst_port_id)

    def get_attribute_value(self, cs_address, attribute_name):
        """
        Retrieve attribute value from the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.get_attribute_command(cs_address, attribute_name)
                value = session.send_command(command)
                return AttributeValueResponseInfo(value)
        """
        serial_number = 'Serial Number'
        if len(cs_address.split('/')) == 1 and attribute_name == serial_number:
            with self._cli_handler.default_mode_service() as session:
                autoload_actions = AutoloadActions(session, self._logger)
                board_table = autoload_actions.board_table()
            return AttributeValueResponseInfo(board_table.get('serial_number'))
        else:
            raise Exception(self.__class__.__name__,
                            'Attribute {0} for {1} is not available'.format(attribute_name, cs_address))

    def set_attribute_value(self, cs_address, attribute_name, attribute_value):
        """
        Set attribute value to the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :param attribute_value: value, "10000"
        :type attribute_value: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.set_attribute_command(cs_address, attribute_name, attribute_value)
                session.send_command(command)
                return AttributeValueResponseInfo(attribute_value)
        """
        if attribute_name == 'Serial Number':
            return
        else:
            raise Exception(self.__class__.__name__, 'SetAttribute {} is not supported'.format(attribute_name))

    def map_tap(self, src_port, dst_ports):
        return self.map_uni(src_port, dst_ports)

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        Set connection speed. Is not used with the new standard
        :param src_port:
        :param dst_port:
        :param speed:
        :param duplex:
        :return:
        """
        raise NotImplementedError
