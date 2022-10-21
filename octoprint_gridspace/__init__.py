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
from octoprint.events import Events, eventManager
from octoprint.filemanager.util import DiskFileWrapper
from octoprint.filemanager.destinations import FileDestinations

import os
import json
import time
import uuid
import urllib
import socket
import requests
import threading

from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError

def background_spool(file_saver, get_name, ip_addr, port, guid, grid, logger, version, exit):
    last = "*"
    count = 0
    logger.info('v{} thread start'.format(version))
    while not exit.is_set():
        logger.debug('v{} connecting'.format(version))
        try:
            fqdn = socket.getfqdn()
            host = socket.gethostname()
            name = get_name() or host
            addr = ip_addr or str(socket.gethostbyname(fqdn))
            stat = {"device":{
                        "name": name,
                        "host": host,
                        "uuid": guid,
                        "port": port,
                        "mode": "octo",
                        "addr": [addr]
                    },
                    "state":"ready",
                    "rand":round(time.time()),
                    "type":"op-{}".format(version)}
            if count < 2:
                logger.info('connect {} {} = [{}] {}'.format(count,grid,guid,stat))
            else:
                logger.debug('connect {} {} = [{}] {}'.format(count,grid,guid,stat))
            stat = urllib.parse.quote_plus(json.dumps(stat, separators=(',', ':')))
            url = "{grid}/api/grid_up?uuid={guid}&stat={stat}&last={last}".format(grid=grid,guid=guid,stat=stat,last=last)
            response = requests.get(url)
            last = "*";
        except ConnectionError as error:
            logger.info('connection error {}'.format(error))
            time.sleep(10)
            break
        except HTTPError as error:
            logger.info('http error {}'.format(error))
            time.sleep(5)
            break
        except Timeout:
            logger.info('connection timeout')
            time.sleep(1)
            continue
        finally:
            count = count + 1

        if response:
            text = response.text
            if count < 2:
                logger.info('response = {}'.format(text))
            if text == 'superceded':
                logger.info('superceded')
                break
            elif text == 'reconnect':
                logger.debug('reconnect')
            else:
                body = text.split('\0')
                last = body[0]
                file = body[0]
                gcode = body[1]
                logger.info('received "{}" length={}'.format(file,len(gcode)))
                file_saver(file, gcode)
    logger.info('v{} thread exit'.format(version))

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
        self._started = 0

    def initialize(self):
        logger = self._logger
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 80))
            ip_addr = sock.getsockname()[0]
            self._ip_addr = ip_addr
            logger.info('ip_addr = {}'.format(ip_addr))
        except socket.error:
            logger.info('ip_addr error')
        finally:
            sock.close()
        try:
            guid = self._settings.get(["guid"])
            if guid is None:
                guid = str(uuid.uuid4())
                self._settings.set(["guid"], guid)
                self._settings.save()
            logger.info('guid = {}'.format(guid))
        except:
            logger.info('guid fail')

    def file_saver(self, filename, gcode):
        self._file_manager.add_file(FileDestinations.LOCAL, filename, FileSaveWrapper(gcode))
        # FileManager only triggers AddFile events - triggering Events.UPLOAD allows other plugins
        # to treat spooling the same as drag & drop.
        #
        # See https://github.com/OctoPrint/OctoPrint, src/octoprint/server/api/files.py for Events.UPLOAD payload spec
        eventManager().fire(
            Events.UPLOAD,
            {
                "name": os.path.basename(filename),
                "path": filename,
                "target": FileDestinations.LOCAL,
                "select": False,
                "print": False,
                "effective_select": False,
                "effective_print": False,
            },
        )

    def get_name(self):
        return self._settings.global_get(["appearance", "name"])

    def get_settings_defaults(self):
        return dict(
            enabled=None,
            appearance=dict(name="aname"),
            host="https://live.grid.space",
            port=80,
            guid=None,
            show_help=True
        )

    def on_settings_save(self, data):
        self._logger.info('settings_save')
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.on_after_startup()

    def on_environment_detected(self, environment, *args, **kwargs):
        self._environment = environment

    def get_assets(self):
        return dict(css=["css/gridspace.css"], js=["js/gridspace.js"])

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=True)]

    def on_after_startup(self):
        if self._started > 0:
            self._exit_flag.set()
        exit_flag = threading.Event();
        thread = threading.Thread(target=background_spool, kwargs=({
            "file_saver": self.file_saver,
            "get_name": self.get_name,
            "ip_addr": self._ip_addr,
            "port": self._settings.get_int(["port"]),
            "guid": self._settings.get(["guid"]),
            "grid": self._settings.get(["host"]),
            "logger": self._logger,
            "version": self._plugin_version,
            "exit": exit_flag
        }))
        thread.daemon = True
        thread.start()
        self._thread = thread
        self._exit_flag = exit_flag
        self._started = self._started + 1

    def on_event(self, event, payload):
        self._logger.debug('event {} {}'.format(event, payload))

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
