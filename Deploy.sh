#!/usr/bin/env bash

echo "HAProxy install and update config"
pwd
ls -lisa

echo "HAProxy update of backends in accordance to vm azure tags"
AzureVMsJson=$(get_octopusvariable "Octopus.Action[Dynamic-VM-Inventory].Output.AzureVMsJson")
echo "Get Azure VMs Json String from Octopus"

echo "Generate backend rules config from tags"
sudo apt install python-pip -y
#pip install --upgrade pip
pip install Jinja2

# Create file for #{environment} and location
location=$(get_octopusvariable "location")
environment=$(get_octopusvariable "environment")
echo $AzureVMsJson | python haproxy.py --environment $environment --location $location > haproxy.cfg
echo "Backend rules config file"
cat haproxy.cfg

echo "Install HAProxy"
sudo apt-get update
sudo apt-get install -y haproxy

#Lint haproxy configuration
/usr/local/sbin/haproxy -c -V -f ./haproxy.cfg

#Copy generated config if validate is ok
echo "Copy generated configs"
sudo cp haproxy.cfg /etc/haproxy/haproxy.cfg

#sudo sudo service haproxy start
sudo sudo service haproxy start
