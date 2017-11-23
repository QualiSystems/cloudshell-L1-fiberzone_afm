#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.layer_one.core.response.response_info import GetStateIdResponseInfo, ResourceDescriptionResponseInfo, \
    AttributeValueResponseInfo
from fiberzone_afm.cli.fiberzone_cli_handler import FiberzoneCliHandler
from fiberzone_afm.command_actions.autoload_actions import AutoloadActions
from fiberzone_afm.command_actions.mapping_actions import MappingActions
from fiberzone_afm.helpers.autoload_helper import AutoloadHelper


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
        #     os.path.join(os.path.dirname(__file__), 'helpers', 'test_fiberzone_data'), logger)

        self._mapping_timeout = RuntimeConfiguration().read_key('MAPPING.TIMEOUT')

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

    def _connect_ports(self, src_port_id, dst_port_id):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            if mapping_actions.port_connected(src_port_id) or mapping_actions.port_connected(dst_port_id):
                raise Exception(self.__class__.__name__,
                                'Port {0}, or port {1} has already been connected'.format(src_port_id, dst_port_id))
            if mapping_actions.port_locked(src_port_id) or mapping_actions.port_locked(dst_port_id):
                raise Exception(self.__class__.__name__,
                                'Port {0} or port {1} is locked'.format(src_port_id, dst_port_id))
            mapping_actions.connect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                if not mapping_actions.port_locked(src_port_id) and not mapping_actions.port_locked(dst_port_id):
                    if mapping_actions.port_connected(src_port_id) == dst_port_id and mapping_actions.port_connected(
                            dst_port_id) == src_port_id:
                        return
                    else:
                        time.sleep(5)
                else:
                    raise Exception(self.__class__.__name__,
                                    'Port {0} or port {1} has been locked'.format(src_port_id, dst_port_id))
            raise Exception(self.__class__.__name__,
                            'Cannot connect {0} to {1} during {2}sec'.format(src_port_id, dst_port_id,
                                                                             self._mapping_timeout))

    def _disconnect_ports(self, *ports):
        with self._cli_handler.default_mode_service() as session:
            mapping_actions = MappingActions(session, self._logger)
            if len(ports) == 1:
                src_port_id = ports[0]
                dst_port_id = mapping_actions.port_connected(src_port_id)
                if not dst_port_id:
                    return
            else:
                src_port_id = ports[0]
                dst_port_id = ports[1]

            connected_dst_id = mapping_actions.port_connected(src_port_id)
            connected_src_id = mapping_actions.port_connected(dst_port_id)

            if not connected_src_id and not connected_dst_id:
                return
            elif connected_src_id and connected_src_id != src_port_id:
                raise Exception(self.__class__.__name__,
                                'Dst Port {0} connected to incorrect Src Port {1}'.format(dst_port_id,
                                                                                          connected_src_id))
            elif connected_dst_id and connected_dst_id != dst_port_id:
                raise Exception(self.__class__.__name__,
                                'Src Port {0} connected to incorrect Dst Port {1}'.format(src_port_id,
                                                                                          connected_dst_id))
            
            if mapping_actions.port_locked(src_port_id) or mapping_actions.port_locked(dst_port_id):
                raise Exception(self.__class__.__name__,
                                'Port {0} or port {1} is locked'.format(src_port_id, dst_port_id))
            mapping_actions.disconnect(src_port_id, dst_port_id)
            start_time = time.time()
            while time.time() - start_time < self._mapping_timeout:
                if not mapping_actions.port_locked(src_port_id) and not mapping_actions.port_locked(dst_port_id):
                    if not mapping_actions.port_connected(src_port_id) and not mapping_actions.port_connected(
                            dst_port_id):
                        return
                    else:
                        time.sleep(5)
                else:
                    raise Exception(self.__class__.__name__,
                                    'Port {0} or port {1} has been locked'.format(src_port_id, dst_port_id))
            raise Exception(self.__class__.__name__,
                            'Cannot disconnect {0} from {1} during {2}sec'.format(src_port_id, dst_port_id,
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
        for src_port in ports:
            src_port_id = self._convert_port(src_port)
            self._disconnect_ports(src_port_id)

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
        pass

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
