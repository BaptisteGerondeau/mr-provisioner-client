#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from library.common import *
from library.ImageControl import ImageControl
from library.PreseedControl import PreseedControl

class StateControl(object):
    def __init__(self, urlhandler, machine_name):
        self.urlhandler = urlhandler
        self.machine_id = get_machine_id(self.urlhandler, machine_name)

    def provision(self, arch, subarch, initrd_desc, kernel_desc,
                  kernel_opts="", preseed_name=None):
        """ enables netboot on the machine and pxe boots it """
        self.set_provisioning_state(arch, subarch, initrd_desc, kernel_desc,
                                    kernel_opts, preseed_name, True)

        url = "/api/v1/machine/{}/state".format(self.machine_id)
        data = json.dumps({'state': 'provision'})

        return self.urlhandler.post(url, data)

    def get_provisioning_state(self):
        """ Get parameters on machine specified by machine_id """
        url = "/api/v1/machine/{}".format(self.machine_id)
        return self.urlhandler.get(url)

    def set_provisioning_state(self, arch, subarch, initrd_desc, kernel_desc,
                          kernel_opts="", preseed_name=None, netboot=False):
        """ Set parameters on machine specified by machine_id """
        if arch == '' or subarch == '' or initrd_desc == '' or kernel_desc == '':
            raise ClientError("Missing arguments for setting machine's state")

        image_controller = ImageControl(self.urlhandler)
        url = "/api/v1/machine/{}".format(self.machine_id)
        parameters = dict()

        if initrd_desc and kernel_desc:
            initrd_id = image_controller.get_image_id(
                        initrd_desc, "Initrd", arch)

            kernel_id = image_controller.get_image_id(kernel_desc,
                                                    "Kernel", arch)
        else:
            raise ClientError("Invalid Initrd and Kernel description")

        if preseed_name is not None:
            preseed_controller = PreseedControl(self.urlhandler)
            preseed_id = preseed_controller.get_preseed_id(preseed_name)
            parameters['preseed_id'] = preseed_id

        if kernel_opts:
            parameters['kernel_opts'] = kernel_opts

        parameters['kernel_id'] = kernel_id
        parameters['initrd_id'] = initrd_id
        parameters['subarch'] = subarch
        parameters['netboot_enabled'] = netboot

        data = json.dumps(parameters)

        return self.urlhandler.put(url, data)

    def get_power_state(self):
        url = "/api/v1/machine/{}/power".format(self.machine_id)
        data = self.urlhandler(url)
        return data['state']

    def set_power_state(self, power_state):
        if power_state is None:
            raise ClientError("Please supply the desired power_state as \
                              argument")
        url = "/api/v1/machine/{}/power".format(self.machine_id)
        state = dict()
        state['state'] = power_state

        data = json.dumps(state)
        return self.urlhandler.post(url, data)
