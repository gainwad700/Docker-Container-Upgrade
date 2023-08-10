# Auto Deploy Containers for Openstack and Ceph
The script can be used to automatically download all the containers of a certain release of openstack or ceph.


## openstack
For the openstack part: it goes on github.com to check all the available containers and subcontainers for each service 
defined under the "plugins" variable down below. Regarding to that it modifies the strings, so that it can download the 
corresponding versions from quay.io.

## Ceph
For the ceph part: as ceph doesn't provide release specific tags and also not a "latest" tag, it's more difficult to 
find the right versions. Therefore the URLs are hardcoded here in the script and need to be manually adjusted by any change.


## installation

You need a node to download all the containers to push them to the registry.
Perform all the tasks mentioned below on this dedicated node.

### Clone the scripts

```
git clone https://git:3000/Docker-Container-Upgrade.git

```

### Install the prereqs
#### Install python
```
apt install python3 -y

```

#### Install the python modules
```
pip3 install bs4
pip3 install requests
pip3 install ...

```

## Check for new services
To know if there is a certain service available to download. Please just check this git to find out it's name and add it to the script.

- [ ] https://github.com/openstack/kolla/tree/master/docker/


### Add the name in the script at line 58 --> plugins

![line to adjust for new plugins](https://git:3000/Docker-Container-Upgrade/src/branch/master/imgs/plugins.PNG)


## Run the script

The script can be used for Openstack and Ceph seperately.

### Argument values format
```
# python3 ./docker-container-upgrade.py --platform [platformname] --service [servicename]
```

### Examples Openstack
```
# python3 ./docker-container-upgrade.py --platform openstack --service all
# python3 ./docker-container-upgrade.py --platform openstack --service neutron
# python3 ./docker-container-upgrade.py --platform openstack --service glance,grafana
```
### Examples Ceph
```
# python3 ./docker-container-upgrade.py --platform ceph --service all
# python3 ./docker-container-upgrade.py --platform ceph --service prometheus
# python3
```

