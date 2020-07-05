# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

__copyright__ = "Copyright (C) Stewart Allen [sa@grid.space]"

import octoprint.plugin
import requests
import hashlib
import logging

try:
    # noinspection PyCompatibility
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

# noinspection PyCompatibility
import concurrent.futures

from octoprint.util import RepeatedTimer, monotonic_time
from octoprint.util.version import get_octoprint_version_string
from octoprint.events import Events
from octoprint.filemanager.util import DiskFileWrapper

import json
import time
import urllib
import socket
import requests
import threading

from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError

def background_spool(file_saver, get_name, logger):
    while True:
        logger.debug('connecting')
        try:
            uuid = socket.getfqdn()
            host = socket.gethostname()
            name = get_name() or host
            addr = str(socket.gethostbyname(host))
            stat = {"device":{
                        "name":name,
                        "host":host,
                        "uuid":uuid,
                        "port":5000,
                        "mode":"octo",
                        "addr":[addr]
                    },"state":"ready","rand":round(time.time())}
            stat = urllib.parse.quote_plus(json.dumps(stat, separators=(',', ':')))
            url = "https://grid.space/api/grid_up?uuid={uuid}&stat={stat}".format(uuid=uuid,stat=stat)
            response = requests.get(url)
        except ConnectionError as error:
            logger.info('connection error {}'.format(error))
            time.sleep(10)
            break
        except HTTPError as error:
            logger.info('http error {}'.format(error))
            time.sleep(5)
            break
        except Timeout:
            logger.info('timeout')
            time.sleep(1)
            continue

        if response:
            text = response.text
            if text == 'superceded':
                logger.info('superceded')
                break
            elif text == 'reconnect':
                logger.debug('reconnect')
            else:
                body = text.split('\0')
                file = body[0]
                gcode = body[1]
                logger.info('received "{}" length={}'.format(file,len(gcode)))
                file_saver(file, gcode)

class FileSaveWrapper:
    def __init__(self, gcode):
        self.gcode = gcode

    def save(self, destination):
        f = open(destination, "w")
        f.write(self.gcode)
        f.close()

class GridspacePlugin(octoprint.plugin.SettingsPlugin,
                      octoprint.plugin.StartupPlugin,
                      octoprint.plugin.EnvironmentDetectionPlugin,
                      octoprint.plugin.TemplatePlugin,
                      octoprint.plugin.AssetPlugin):

    def __init__(self):
        self._start_time = monotonic_time()

    def initialize(self):
        self._logger.debug('initialize')

    def file_saver(self, filename, gcode):
        self._file_manager.add_file("local", filename, FileSaveWrapper(gcode))

    def get_name(self):
        return self._settings.global_get(["appearance", "name"])

    def get_settings_defaults(self):
        return dict(enabled=None,appearance=dict(name="aname"))

    def on_settings_save(self, data):
        self._logger.debug('settings_save')

    def on_environment_detected(self, environment, *args, **kwargs):
        self._environment = environment

    def get_assets(self):
        return dict(css=["css/gridspace.css"],
                    js=["js/gridspace.js"])

    def on_after_startup(self):
        thread = threading.Thread(target=background_spool, kwargs=({
            "file_saver": self.file_saver,
            "get_name": self.get_name,
            "logger": self._logger
        }))
        thread.daemon = True
        thread.start()
        self._thread = thread

    def on_event(self, event, payload):
        self._logger.debug('event {} {}'.format(event,payload))

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            gridspace=dict(
                displayName="GridSpace Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="GridSpace",
                repo="OctoPrint-GridSpace",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/GridSpace/OctoPrint-GridSpace/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "GridSpace Plugin"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GridspacePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
