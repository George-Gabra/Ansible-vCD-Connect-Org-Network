#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import urllib3
import sys

from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware_vcd import VCDService
from ansible.module_utils.vmware_utils import *
from lxml.objectify import ObjectifiedElement
from pyvcloud.vcd.client import *
from pyvcloud.vcd.exceptions import *
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.pvdc import PVDC
from pyvcloud.vcd.system import System
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import BasicLoginCredentials


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview']}

DOCUMENTATION = r'''
---
module: connect_org_network
version_added: "2.13.6"
description:
   - Add Org Network to vAPP
'''

EXAMPLES = '''
- name: Add Org network to vAPP
  connect_org_network:
    user: "username"
    password: "password"
    host: "vcd.hostname"
    api_version: "vCD.API.version"
    org: "organization.name"
    verify_ssl_certs: false
    vapp_name: "vAPP.name"
    vdc: "vDC.name"
    network: "OrgNetwork.name"
    operation: connect_org_network
'''

RETURN = '''# '''


class ConnectOrgNetwork:
    def realize(self):
        argument_spec = dict(
            host=dict(type="str", required=True),
            user=dict(type="str", required=True),
            password=dict(type="str", required=True, no_log=True),
            org=dict(type="str", required=True),
            vdc=dict(type="str", required=True),
            api_version=dict(type="str", required=True),
            vapp_name=dict(type="str", required=True),
            network=dict(type="str", required=True),
            verify_ssl_certs=dict(type="bool", required=False, default=False),
            operation=dict(type="str", required=True)
        )
        self.module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
        self.operation = self.module.params['operation']
        self.vapp_name = self.module.params['vapp_name']
        self.host = self.module.params['host']
        self.user = self.module.params['user']
        self.password = self.module.params['password']
        self.org = self.module.params['org']
        self.vdc = self.module.params['vdc']
        self.api_version = self.module.params['api_version']
        self.network = self.module.params['network']
        self.verify_ssl_certs = self.module.params['verify_ssl_certs']

        self.client = Client(self.host, self.api_version, verify_ssl_certs=False, log_file='pyvcloud.log', log_requests=True, log_headers=True, log_bodies=True)
        self.client.set_credentials(BasicLoginCredentials(self.user, self.org, self.password))
            
        self.org_resource = self.client.get_org()

        org = Org(self.client, resource=self.org_resource)

        self.vcd_service = VCDService(hostname=self.host, username=self.user, password=self.password, org=self.org, verify_ssl=self.verify_ssl_certs)

        self.vdc_resource = org.get_vdc(self.vdc)
        self.vdc = VDC(self.client, resource=self.vdc_resource)

        self.vapp_resource = self.vdc.get_vapp(self.vapp_name)
        self.vapp = VApp(self.client, resource=self.vapp_resource)
        

        if self.operation == 'connect_org_network':
            self._connect_org_network()
        elif self.operation is None:
            self._return_error()

    def _connect_org_network(self):
        retain_ip=None
        is_deployed=None
        fence_mode=FenceMode.BRIDGED.value
        try:
            vdc = VDC(self.client, href=find_link(self.vapp.resource, RelationType.UP, EntityType.VDC.value).href)
            vdc.get_resource()
            for net in vdc.resource.AvailableNetworks.Network:
                if net.get("name") == self.network:
                    orgvdc_network_href = net.get("href")

            network_configuration_section = deepcopy(self.vapp.resource.NetworkConfigSection)

            matched_orgvdc_network_config = self.vapp._search_for_network_config_by_name(self.network, network_configuration_section)

            if matched_orgvdc_network_config is not None:
               self.module.exit_json(skipped=True, msg="Org vDC network " + self.network + " is already connected to vApp.")

            configuration = E.Configuration(E.ParentNetwork(href=orgvdc_network_href), E.FenceMode(fence_mode))
            if retain_ip is not None:
                configuration.append(E.RetainNetInfoAcrossDeployments(retain_ip))
            network_config = E.NetworkConfig(
                configuration, networkName=self.network)
            if is_deployed is not None:
                network_config.append(E.IsDeployed(is_deployed))
            network_configuration_section.append(network_config)

            task = self.client.put_linked_resource(self.vapp.resource.NetworkConfigSection, RelationType.EDIT, EntityType.NETWORK_CONFIG_SECTION.value, network_configuration_section)

            self.vcd_service.task_monitor.wait_for_success(task=task)
            
            self.module.exit_json(changed=True, msg="Org vDC network " + self.network + " has been connected to vAPP.")


        except Exception as err:
            self.module.fail_json(msg="Could not connect Org network to the vAPP.", error=str(err), stack_trace=traceback.format_exc())


    def _return_error(self):
        self.module.fail_json(msg="Operation can't be None.")



if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    connect_org_network = ConnectOrgNetwork()
    connect_org_network.realize()
