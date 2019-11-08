.. image:: https://travis-ci.org/vmware/pyvmomi.svg?branch=v6.0.0.2016.4
    :target: https://travis-ci.org/vmware/pyvmomi
    :alt: Build Status

.. image:: https://img.shields.io/pypi/dm/pyvmomi.svg
    :target: https://pypi.python.org/pypi/pyvmomi/
    :alt: Downloads

pyVmomi is the Python SDK for the VMware vSphere API that allows you to manage 
ESX, ESXi, and vCenter.

Nagios Plugins
================
These are Nagios plugins to monitor different devices and resources.   


**Automating Nagios configuration to monitor VMware infrastructure**
================

The script **_configure_nagios.py_** allows you to add all your ESXi hosts, VMs and datastores to Nagios automatically. 
The sciript will connect to vCenter Server and create all the required configuration files in Nagios to monitor your VMware infrastructure. 

You will have to install [pyVmomi](https://github.com/vmware/pyvmomi) in the Nagios server before running these scripts. 

Resources that will be monitored:<br/> 
 VMs - CPU, Memory, Virtual Disks, Snapshots Size<br/>
 ESXi hosts - CPU, Memory <br/>
 Datastores usage
 
 Copy the nagios plugins showed below to - /usr/lib/nagios/plugins/
 ```
 check_vm_cpu.py
 check_vm_memory.py
 check_vm_snapshots.py
 check_vm_disk_win.py
 check_vm_disk_linux.py
 check_datastore_space.py
 check_esxi_cpu.py
 check_esxi_memory.py
 ```
 
 Add the command definitions showed below to the file - /etc/nagios3/commands.cfg
 ```
define command{
        command_name    CHECK_CPU
        command_line    /usr/lib/nagios/plugins/check_vm_cpu.py --vm_uuid '$ARG1$'
        }

define command{
        command_name    CHECK_MEMORY
        command_line    /usr/lib/nagios/plugins/check_vm_memory.py --vm_uuid '$ARG1$'
        }

define command{
        command_name    CHECK_SNAPSHOTS
        command_line    /usr/lib/nagios/plugins/check_vm_snapshots.py --vm_uuid '$ARG1$'
        }

define command{
        command_name    CHECK_DISK_WIN
        command_line    /usr/lib/nagios/plugins/check_vm_disk_win.py --vm_uuid '$ARG1$' -p '$ARG2$'
        }

define command{
        command_name    CHECK_DISK_LINUX
        command_line    /usr/lib/nagios/plugins/check_vm_disk_linux.py --vm_uuid '$ARG1$' -p '$ARG2$'
        }

define command{
        command_name    CHECK_DATASTORE
        command_line    /usr/lib/nagios/plugins/check_datastore_space.py --datastore_uuid '$ARG1$' --cluster_name '$ARG2$'
        }

define command{
        command_name    CHECK_ESXi_CPU
        command_line    /usr/lib/nagios/plugins/check_esxi_cpu.py --host_name '$ARG1$'
        }

define command{
        command_name    CHECK_ESXi_MEMORY
        command_line    /usr/lib/nagios/plugins/check_esxi_memory.py --host_name '$ARG1$'
        }
```

Create hostgruop definitions for each cluster in vCenter(see example below) - /etc/nagios3/conf.d/hostgroups_nagios2.cfg
```
define hostgroup {
        hostgroup_name  Cluster-1
        alias           Cluster-1 servers
        }
define hostgroup {
        hostgroup_name  Cluster-2
        alias           Cluster-2 servers
        }
```
      
