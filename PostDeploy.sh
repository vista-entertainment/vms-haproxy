#!/usr/bin/env bash

echo "HAProxy config publish step"
pwd

AzureVMsJson=$(get_octopusvariable "Octopus.Action[Dynamic-VM-Inventory].Output.AzureVMsJson")
echo "Get Azure VMs Json String from Octopus"
echo "$AzureVMsJson"
echo "$AzureVMsJson" > azure-vm.json
ls -lisa
new_octopusartifact azure-vm.json

echo "Publish artifact to Octopus"
new_octopusartifact /etc/haproxy/haproxy.cfg

