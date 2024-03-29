"""
Polyglot v3 node server
Copyright (C) 2023 Steven Bailey
MIT License
Version 3.0.1 Jun 2023
"""
import udi_interface
import time
import json
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,)

LOGGER = udi_interface.LOGGER


class TempSenNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, new_id, deviceid, apiAccessId, apiSecret, apiEndpoint):
        super(TempSenNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll, self.poll) #, self.poll
        self.new_id = new_id
        self.deviceid = deviceid
        self.DEVICESW_ID = deviceid
        self.apiAccessId = apiAccessId
        self.ACCESS_ID = apiAccessId
        self.apiSecret = apiSecret
        self.ACCESS_KEY = apiSecret
        self.apiEndpoint = apiEndpoint
        self.API_ENDPOINT = apiEndpoint
        self.name = name
        self.DEVICE_NAME = name
        LOGGER.info(name)
        self.BtStat(self)

    # Set Modes
    def modeOn(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICESW_ID = self.DEVICESW_ID
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()
        self.modeOn = int(command.get('value'))
        self.setDriver('GV5', self.modeOn)
        # Colour
        if self.modeOn == 0:
            commands = {'commands': [{'code': 'temp_unit_convert', 'value': 'f'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICESW_ID), commands)
            LOGGER.info('f')
            time.sleep(.1)
            self.query(self)
        # Scene
        elif self.modeOn == 1:
            commands = {'commands': [{'code': 'temp_unit_convert', 'value': 'c'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICESW_ID), commands)
            LOGGER.info('c')
            time.sleep(.1)
            self.query(self)
        else:
            pass

    def BtStat(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICESW_ID = self.DEVICESW_ID
        DEVICE_NAME = self.DEVICE_NAME
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()
        response1 = openapi.get(
            "/v1.0/iot-03/devices/{}".format(DEVICESW_ID) + "/status/")
        LOGGER.info(DEVICE_NAME)
        LOGGER.info(response1)
        for i in response1['result'][0:1]:
            LOGGER.info(i['value'])
            self.setDriver('GV7', i['value'])
        for i in response1['result'][1:2]:
            LOGGER.info(i['value'])
            self.setDriver('CLIHUM', i['value'])    
        for i in response1['result'][3:4]:
            LOGGER.info('Actual Setting F/C')
            LOGGER.info(i['value'])
            if i['value'] == "f":
                LOGGER.info(i['value'])
                self.setDriver('GV6', 0)
            if i['value'] == "c":
                LOGGER.info(i['value'])
                self.setDriver('GV6', 1)
        
        for i in response1['result'][2:3]:
            LOGGER.info(i['value'])
            if i['value'] == "low":
                LOGGER.info(i['value'])
                self.setDriver('GV4', 0)
            if i['value'] == "middle":
                LOGGER.info(i['value'])
                self.setDriver('GV4', 1)
            if i['value'] == "high":
                LOGGER.info(i['value'])
                self.setDriver('GV4', 2)
            else:
                pass
            
                    
        ### Online Status
        response = openapi.get("/v1.0/devices/{}".format(DEVICESW_ID))
        LOGGER.info(response['result']['online'])
        if response['result']['online'] == True:
            LOGGER.info(response['result']['online'])
            self.setDriver('ST', 1)
        if response['result']['online'] == False:
            LOGGER.info(response['result']['online'])
            self.setDriver('ST', 0)
        else:
            pass
    
    def poll(self, polltype):
        if 'longPoll' in polltype:
            #self.query(self)
            LOGGER.debug('longPoll (node)')
        else:
            self.BtStat(self)
            LOGGER.debug('shortPoll (node)')

    def query(self, command=None):
        self.BtStat(self)
        self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2, 'name': 'Online'},
        {'driver': 'GV2', 'value': 0, 'uom': 2, 'name': 'Status'},
        {'driver': 'GV7', 'value': 0, 'uom': 14, 'name': 'Temperature'},
        {'driver': 'CLIHUM', 'value': 0, 'uom': 22, 'name': 'Humidity'},
        {'driver': 'GV4', 'value': 0, 'uom': 25, 'name': 'Battery'},
        {'driver': 'GV5', 'value': 0, 'uom': 25, 'name': 'Command'},
        {'driver': 'GV6', 'value': 0, 'uom': 25, 'name': 'Command Status'},
    ]

    id = 'tempsen'

    commands = {
        'QUERY': query,
        'MODETS': modeOn,
    }
