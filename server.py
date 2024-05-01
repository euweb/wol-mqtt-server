import click
import os
import paho.mqtt.client as mqtt
import subprocess
import yaml

class Config(object):

    def __init__(self, d):
        self.__dict__ = d

def get_config_form_file(filename='config.yaml'):
    if not os.path.isfile(filename):
        raise ValueError('Config file %r does not exist!' % filename)
    with open(filename, 'r') as f:
        return yaml.safe_load(f.read())

class Server:

    def __init__(self, config) -> None:
        self.config = config
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def run(self):
        self.config.MQTT_SETTINGS['MQTT_BROKER']
        self.client.connect(self.config.MQTT_SETTINGS['MQTT_BROKER'], self.config.MQTT_SETTINGS['MQTT_PORT'])
        self.client.loop_forever()


    def on_message(self,client, userdata, message):
        msg = str(message.payload.decode("utf-8"))
        print("message received: ", msg)
        print("message topic: ", message.topic)

        is_alive = subprocess.call(['ping', '-c','1', self.config.WOL['IPADDRESS']], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0

        print("is alive: ", is_alive)
        if not is_alive:
            print("send wol")
            process = subprocess.Popen('/usr/bin/wakeonlan -i ' + self.config.WOL['IPADDRESS'] + ' ' + self.config.WOL['MACADDRESS'], shell=True, stdout=subprocess.PIPE)
            stdout = process.communicate()[0]
            print('STDOUT:{}'.format(stdout))

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected to MQTT Broker: " + self.config.MQTT_SETTINGS['MQTT_BROKER'])
        client.subscribe(self.config.MQTT_SETTINGS['TOPIC'])

@click.command()
@click.argument('config', type=click.Path(exists=True))
def main(config):

    config = Config(get_config_form_file(config))

    server = Server(config)
    server.run()

    
if __name__ == '__main__':
    main()

