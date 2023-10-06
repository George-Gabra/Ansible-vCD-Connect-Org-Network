# Ansible vCD Connect Org Network module

This repository contains Ansible module for connecting organization networks to a VMware vCloud Director (vCD) vAPP using Ansible.

## Table of Contents

- [Introduction](#introduction)
- [Usage](#usage)
- [Contributing](#contributing)

## Introduction

The module provided in this repository helps overcome issues related to adding imported organization network in vCloud Director to a vAPP using https://github.com/vmware/ansible-module-vcloud-director/wiki/vCD-vApp#add-org-network module.

## Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/George-Gabra/Ansible-vCD-Connect-Org-Network.git
   cd Ansible-vCD-Connect-Org-Network
   ```

2.  **Copy the module file to vCD Ansible modules directory**:
  Copy connect_org_network.py file to vCD ansible modules directory https://github.com/vmware/ansible-module-vcloud-director.  

   
4.  **Add the module and configure Variables**:
   Update Ansible playbook file with the task and necessary configuration parameters, including vCloud Director API endpoint, organization name, network settings, etc.
  
   ```bash
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
   ```

## Contributing

Contributions to this repository are welcome. Feel free to open issues for bug reports, feature requests, or any other improvements you'd like to propose. If you'd like to contribute directly, please fork the repository and submit a pull request with your changes.
