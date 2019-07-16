# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
import iothub_client
import Adafruit_DHT
import json
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

class Reading:
    def __init__(self,humidity, temperature):
        self.humidity = humidity
        self.temperature = temperature

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT


def send_confirmation_callback(message, result, user_context):
    print("IoT Hub responded to message with status: %s" % (result))


class HubManager(object):

    def __init__(
            self,
            protocol=IoTHubTransportProvider.MQTT):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

    def send_telemetry(self, event, send_context):
        message = IoTHubMessage(bytearray(event,'utf8'))
        self.client.send_event_async(
            'TempAndHumidity', message, send_confirmation_callback, send_context)

def main(protocol):
    try:
        print ( "\nPython %s\n" % sys.version )
        print ( "IoT Hub Client for Python" )

        hub_manager = HubManager(protocol)

        print ( "Starting the IoT Hub Python DHT11 protocol %s..." % hub_manager.client_protocol )
        print ( "The sample is now waiting for messages and will indefinitely.  Press Ctrl-C to exit. ")

        while True:
            try:
                time.sleep(.1)
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 11)
                if humidity is not None and temperature is not None:
                    jsonresult = Reading(humidity,temperature).toJSON()
                    print('Sending telemetry: %s' % jsonresult)
                    hub_manager.send_telemetry(jsonresult,None)
                else:
                    print('Not sending telemetry')
            except Exception as e:
                print('Failed to produce readings: %s' % str(e))

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubModuleClient sample stopped" )

if __name__ == '__main__':
    main(PROTOCOL)