#!/usr/bin/env bash

#Check that the JSON VM Inventory has been populated
AzureVMsJson=$(get_octopusvariable "Octopus.Action[Dynamic-VM-Inventory].Output.AzureVMsJson")
#Check that the JSON VM Inventory has been populated
if [ ! -z "$AzureVMsJson" -a "$AzureVMsJson" != " " ]; then
        echo "AzureVMsJson is not null or space"
else
        echo "AzureVMsJson is null or space"
		exit 1 # terminate and indicate error
fi