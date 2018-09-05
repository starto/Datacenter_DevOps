import re
import os

# Default Resource/ENV Settings
LOCATION = os.getenv('PROFITBRICKS_LOCATION', 'de/fra')
IMAGE_NAME = 'Ubuntu-16'  # Note: Partial image name and case sensitive

def resource():
    return {
        'datacenter': {
            'name': 'Trial Virtual DC',
            'description': 'New Virtual Data Center',
            'location': 'de/fra'
        },

        'lan1': {
            'name': 'LAN1 Public',
            'public': True
            #Members: Nic-0 on Internet Access &  NIC-0 on FrontEnd Server
        },

        'lan2': {
            'name': 'LAN2 Private',
            'public': False
            #'private': True,
            #Members: NIC-0 on Backend Server and NIC-1 on FrontEnd Server
        },

        'nic1_1': {
            'name': 'Public NIC',
            'dhcp': True,
            'lan': 1,
            'firewall_active': True,
            'nat': False
        },

        'nic1_2': {
            'name': 'Private NIC',
            'ips': ['10.2.2.1'],
            'lan': 2,
            'firewall_active': True,
            'nat': False
        },

        # Create Private NIC on Server-2/Backend Server
        'nic2': {
            'name': 'Private NIC',
            'ips': ['10.2.2.2'],
            'lan': 2,
            'firewall_active': False,
            'nat': False
        },

        # Create Frontend Server-1
        'server1': {
            'name': 'FrontEnd Server',
            'ram': 2*1024,
            'cores': 2,
            'cpu_family': 'INTEL_XEON'
        },

        'server2': {
            'name': 'BackEnd Server',
            'ram': 4 * 1024,
            'cores': 2,
            'cpu_family': 'INTEL_XEON'
            },

        'Updated_Server1': {
            'name': 'Updated Server1',
            'ram': 6 * 1024,
            'cores': 4,
         },

        'volume1': {
            'name': 'Volume-1 Frontend Storage',
            'size': 4,
            'bus': 'VIRTIO',
            #'type': 'HDD',
            'image' : 'image_id',
            'ssh_keys': ['ssh-rsa AAAAB3NzaC1'],
            #'licence_type': 'LINUX',
            #'image_password': "pradeep123",
            'availability_zone': 'ZONE_1'
         },

         'volume2': {
                'name': 'Volume-2 Backend Storage',
                'size': 4,
                'bus': 'VIRTIO',
                # 'type': 'HDD',
                'image': 'image_id',
                'ssh_keys': ['ssh-rsa AAAAB3NzaC1'],
                # 'licence_type': 'LINUX',
                # 'image_password': "pradeep123",
                'availability_zone': 'ZONE_1'
         },
        'locations': ['us/las', 'us/ewr', 'de/fra', 'de/fkb'],
        'licence_type': ['LINUX', 'WINDOWS', 'WINDOWS2016', 'OTHER', 'UNKNOWN'],
        'vm_states': ['RUNNING', 'SHUTOFF'],
        'uuid_match': '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        'mac_match': re.compile('^([0-9a-f]{2}[:]){5}([0-9a-f]{2})$')
         }