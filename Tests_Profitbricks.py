import unittest
from pprint import pprint
import paramiko
import os
import json
from datetime import timedelta
from helpers import resource
from uptime import uptime
import multiprocessing
import threading
from profitbricks.client import Datacenter, Server, Volume, NIC, LAN
from profitbricks.client import ProfitBricksService
from profitbricks.errors import PBError, PBNotFoundError, PBNotAuthorizedError, PBValidationError
import time
from paramiko import SSHException, BadHostKeyException, AuthenticationException, BadAuthenticationType
import timeit, datetime
import shutil
import filecmp
from glob import glob
import socket
import smtplib

# 1. Create the empty data center,
# 2. Create the Servers,
# 3. Create the volumes unattached,
# 4. Create the LANs (Public LAN/Private LAN)
# 5. Create the NICs for the Servers,
# 6. Attach the volumes, CD-ROMs to the Servers.
# 7. Start the Servers

class TestVirtualDataCenter(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.resource = resource()
        self.timeout = 1800

        self.client = ProfitBricksService(
            username='pradeep.6174@gmail.com',
            password='pxyz1P%')

        # 1. Creating an empty data center Object
        self.datacenter = self.client.create_datacenter(datacenter=Datacenter(**self.resource['datacenter']))
        self.client.wait_for_completion(self.datacenter, self.timeout)
        datacenter_id = self.datacenter['id']
        print(datacenter_id)

        # Fetch Ubuntu-16's image ID for booting the HDD Storage Unit
        image_to_boot = "Ubuntu-16.04-LTS-server-2018-09-01"
        image_id = ''
        for image_item in self.client.list_images()['items']:
            each_image = image_item['properties']['name']
            location = image_item['properties']['location']
            # if each_image.startswith('Ubuntu'):
            if (each_image == image_to_boot and
                    location == self.resource['datacenter']['location']):
                # image_id = image_item['id']
                break

        image_id = image_item['id']
        print(image_item)
        print("\nAfter the image_id:", image_id)
        print("\nImage Name:", image_item['properties']['name'])
        # print(image_id)

        # # Fetch Ubuntu-16.x ISO image for CD-ROM
        cd_rom_image = "ubuntu-16.04.4-server-amd64.iso"
        self.cdrom_image_id = ''
        for image_item in self.client.list_images()['items']:
            if (image_item['metadata']['state'] == "AVAILABLE"
                    and image_item['properties']['location'] == self.resource['datacenter']['location']
                    and image_item['properties']['public'] is True
                    and image_item['properties']['imageType'] == "CDROM"
                    and image_item['properties']['licenceType'] == "LINUX"):
                # if image_item['properties']['name'].startswith('ubuntu'):
                if image_item['properties']['name'] == cd_rom_image:
                    break

        pprint(image_item['properties']['name'])
        self.cdrom_image_id = image_item['id']
        # self.test_image1['id'] = image_item['id']
        # pprint(self.cdrom_image_id)

        # 2. Create a Test Server & attach a System volume
        # Create Frontend Server-1
        response = self.client.create_server(
            datacenter_id=self.datacenter['id'],
            server=Server(**self.resource['server1']))

        # Define Volumes here
        # response = self.client.create_server(datacenter_id=datacenter_id, server=self.server1)
        self.client.wait_for_completion(response, self.timeout)
        self.server1_id = response['id']

        response = self.client.create_server(
            datacenter_id=self.datacenter['id'],
            server=Server(**self.resource['server2']))

        # Define Volumes here
        # response = self.client.create_server(datacenter_id=datacenter_id, server=self.server1)
        self.client.wait_for_completion(response, self.timeout)
        self.server2_id = response['id']

        # 3. Creating a System Volume-1 within the VDC (& then attach the volume to the Server later)
        volume1 = Volume(
            name='Frontend Storage/Volume-1',
            size=4,
            bus='VIRTIO',
            # type='HDD',
            image=image_id,
            # licence_type='LINUX',
            ssh_keys=['ssh-rsa AAAAB3NzaC1'],
            # image_password = "pradeep123",
            availability_zone='ZONE_1')

        response = self.client.create_volume(
            datacenter_id=datacenter_id,
            volume=volume1)
        self.client.wait_for_completion(response, self.timeout)
        volume1_id = response['id']

        # Attach System volume to App Server-1
        response = self.client.attach_volume(
            datacenter_id=datacenter_id,
            server_id=self.server1_id,
            # server_id=server1_id,
            volume_id=volume1_id)
        self.client.wait_for_completion(response, self.timeout)

        volume2 = Volume(
            name='Backend Volume-2 Storage',
            size=4,
            bus='VIRTIO',
            # type='HDD',
            image=image_id,
            # licence_type='LINUX',
            ssh_keys=['ssh-rsa AAAAB3NzaC1'],
            # image_password = "pradeep123",
            availability_zone='ZONE_1')

        response = self.client.create_volume(
            datacenter_id=datacenter_id,
            volume=volume2)
        self.client.wait_for_completion(response, self.timeout)
        volume2_id = response['id']

        # Attach system volume to Server-1
        response = self.client.attach_volume(
            datacenter_id=datacenter_id,
            server_id=self.server2_id,
            # server_id=server1_id,
            volume_id=volume2_id)
        self.client.wait_for_completion(response, self.timeout)

        ## 4. Create LAN (Public/Private)
        # Both Servers are connected per Private LAN
        self.lan1 = self.client.create_lan(datacenter_id=self.datacenter['id'],
                                           lan=LAN(**self.resource['lan1']))
        self.client.wait_for_completion(self.lan1, self.timeout)

        # LAN-2
        self.lan2 = self.client.create_lan(datacenter_id=self.datacenter['id'],
                                           lan=LAN(**self.resource['lan2']))
        self.client.wait_for_completion(self.lan2, self.timeout)



        # 4. Create test NIC for the Servers
        # Provisioning the FrontEnd Server; create test NIC1 # NIC's name on Server1 to Server2
        nic1_1 = NIC(**self.resource['nic1_1'])
        # nic1_1.lan = self.lan['id']
        self.nic1_1 = self.client.create_nic(
            datacenter_id=self.datacenter['id'],
            server_id=self.server1_id, nic=nic1_1)
        self.client.wait_for_completion(self.nic1_1, self.timeout)

        nic1_2 = NIC(**self.resource['nic1_2'])
        self.nic1_2 = self.client.create_nic(
            datacenter_id=self.datacenter['id'],
            server_id=self.server1_id,
            nic=nic1_2)
        self.client.wait_for_completion(self.nic1_2, self.timeout)

        # Create Private NIC on Server-2/Backend Server
        nic2 = NIC(**self.resource['nic2'])
        # nic1_2.lan = self.lan['id']
        pprint("\n\n---------NIC2---------\n\n")

        self.nic2 = self.client.create_nic(
            datacenter_id=self.datacenter['id'],
            server_id=self.server2_id,
            nic=nic2)
        self.client.wait_for_completion(self.nic2, self.timeout)

        # # Create CD-ROM
        self.cdrom1 = self.client.attach_cdrom(
            datacenter_id=self.datacenter['id'],
            server_id=self.server1_id,
            cdrom_id=self.cdrom_image_id)
        self.client.wait_for_completion(self.cdrom1, self.timeout)

        self.cdrom2 = self.client.attach_cdrom(
            datacenter_id=self.datacenter['id'],
            server_id=self.server2_id,
            cdrom_id=self.cdrom_image_id)
        self.client.wait_for_completion(self.cdrom2, self.timeout)

    # @classmethod
    # def tearDownClass(self):
    #     self.client.delete_datacenter(datacenter_id=self.datacenter['id'])

    ## Testcase-1: Test all the Data Center elements
    def test_all_datacenter_elements(self):
         # Testing Data Center Creation
         datacenter = self.client.get_datacenter(datacenter_id=self.datacenter['id'])
         # assertRegex(self, datacenter['id'], self.resource['uuid_match'])
         self.assertEqual(datacenter['type'].lower(), 'datacenter')
         self.assertEqual(datacenter['id'], self.datacenter['id'])
         self.assertEqual(datacenter['properties']['name'], self.resource['datacenter']['name'])
         self.assertEqual(datacenter['properties']['location'], self.resource['datacenter']['location'])

         # Testing Volumes
         volumes = self.client.list_volumes(datacenter_id=self.datacenter['id'])
         self.assertGreater(len(volumes), 0)
         self.assertEqual(volumes['items'][0]['type'], 'volume')

         # Test list Lans
         lans = self.client.list_lans(datacenter_id=self.datacenter['id'])
         self.assertGreater(len(lans), 0)

         self.assertEqual(lans['items'][0]['type'], 'lan')
         self.assertIn(lans['items'][0]['id'], ('1', '2', '3'))

         ## Test Get lan
         lan = self.client.get_lan(datacenter_id=self.datacenter['id'], lan_id=self.lan1['id'])
         self.assertEqual(lan['type'], 'lan')
         self.assertEqual(lan['id'], self.lan1['id'])
         self.assertEqual(lan['properties']['name'], self.resource['lan1']['name'])
         self.assertTrue(lan['properties']['public'], self.resource['lan1']['public'])

         ## Test list NICs created on Server1
         nics = self.client.list_nics(datacenter_id=self.datacenter['id'],
                                      server_id=self.server1_id)
         self.assertGreater(len(nics), 0)
         self.assertIn(nics['items'][0]['id'], (self.nic1_1['id'], self.nic1_2['id']))
         self.assertEqual(nics['items'][0]['type'], 'nic')

         ## Test list NICs created on Server2
         nics = self.client.list_nics(datacenter_id=self.datacenter['id'],
                                      server_id=self.server2_id)
         pprint(self.nic2['id'])


    ## Testcase-3: Change the Data Center by increasing the Cores/RAM being used.
    def test_update_datacenter_servers(self):
         response = self.client.update_server(
             datacenter_id=self.datacenter['id'],
             server_id=self.server1_id,
             name=self.resource['Updated_Server1']['name'],
             cores=4,
             ram=6 * 1024)

         self.client.wait_for_completion(response, self.timeout)

         server = self.client.get_server(
             datacenter_id=self.datacenter['id'],
             server_id=self.server1_id
         )

         #print("\n=====Updated Server1 details========\n")
         #pprint(server['properties']['name'])
         #pprint(server['properties']['cores'])
         #pprint(server['properties']['ram'])

         self.assertEqual(server['id'], self.server1_id)
         self.assertEqual(server['properties']['name'], self.resource['Updated_Server1']['name'])
         self.assertEqual(server['properties']['cores'], self.resource['Updated_Server1']['cores'])
         self.assertEqual(server['properties']['ram'], self.resource['Updated_Server1']['ram'])

    # Testcase-2: Check whether the ‘Frontend’ Server is up and running.
    # Raised a case with profitbricks cusotmer 5 days ago but issue still not present
    # not able to login to Ubuntu Server, no API to login to remote console. default remote root credentials are not working.
    # I am proposing multiple alternative solutions here
    def test_is_frontend_server_up(self):

        self.server_start = self.client.start_server(
            datacenter_id=self.datacenter['id'],
            server_id=self.server1_id)
        time.sleep(100)

        response1 = self.client.list_users()
        pprint("\n====List all Users=======\n")
        pprint(response1)

        ## Listing the IP Blocks
        response = self.client.list_ipblocks()
        pprint("\n====Listing IP Blocks=======\n")
        pprint(response)

        # Test attached CD-ROM
        cdrom1 = self.client.get_attached_cdrom(
            datacenter_id=self.datacenter['id'],
            server_id=self.server1_id,
           cdrom_id=self.cdrom_image_id)
        self.assertEqual(cdrom1['id'],self.cdrom_image_id)

        cdrom2 = self.client.get_attached_cdrom(
            datacenter_id=self.datacenter['id'],
            server_id=self.server2_id,
           cdrom_id=self.cdrom_image_id)
        self.assertEqual(cdrom2['id'],self.cdrom_image_id)

        pprint("\n=======Get the attached CD-ROM:=======\n")
        ## you can test for all other datacenter elements like: Servers, NICs, LANs, Volumes, CD-ROMS etc like tested in testcase-1

        '''
        Raised a case with ProfitBricks Customer care team: case #130868
        I am not able to remotely login to Ubuntu server after attaching the Profitbricks Ubuntu 16.x IOS image.
        Default root credentials didn't work, the default Image password I had setup failed as well.
        
        Tried reaching out to customer care team but off to no avail. Query hasn't been completed addressed.
        
        >> Unless we have access to server, we cannot conclusively say: Test case #2 (Server up) and #4 (Copy Scenario)
           are working fine: I am proposing multiple solutions here to overcome this.

        ##NOTE:: All the below approaches are written for serial 1 server - but, this can easily be translated to: 
        multi-processing and threading for scalabile 1000+ servers cases (using multiprocessing and threading modules)
        
        Solution - 1: start_server API and check all server id, properties etc (whichwere checked in testcase#1) can be leveraged.
        Solution - 2: Checking if remote SSH to Ubunutu server is working fine (Solution below)
        Solution - 3:   i) Checking 'uptime' of the server using uptime module; this is OS/Platform agnostic module
                       ii) Define your own version of 'uptime'
                       Solution for 3-1/2 are below:
        Solution - 4: Get the IP Address of the Server and check if the 'inet addr' is reachable:
                # root @ tryit - fancy: ~  # /sbin/ifconfig | grep 'inet addr:'
                                           inet addr: 127.0.0.1 Mask: 255.0.0.0
        Solution - 5: Login to Server and check for below install linux images
                # cd /etc
                # dpkg --get-selections | grep linux-image | grep -v deinstall
        Solution - 6: root@tryit-fancy:~# hostname -i                                                                                                                                
                        127.0.1.1 
        '''


        '''
        hostname = 'ttsv-shell102.server1.net'
        port = 22
        username = 'pradeep'
        password = 'xyxyxyx13'
        dir_path = '/homes/anpradeep/'

        ssh_client = paramiko.SSHClient()
        # ssh_client.load_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname, port, username, password)

            if uptime() > 0:
                print("Server has been UP since " + str(uptime()) + " Seconds")

                   # Alternative Solution
                   # If SSH Connection is successful ==> Check if the System is up and measure the System's Uptime
                   # Measure the System Uptime using: 1) cat '/proc/uptime'; 2) 'uptime' on Server
                   with open('/proc/uptime', 'r') as f:
                       uptime_seconds = float(f.readline().split()[0])
                       uptime_string = str(timedelta(seconds=uptime_seconds))
                       #stdin, stdout, stderr = ssh_client.exec_command('uptime')
                       #'b' 09:26:08 up 41 days, 15:01, 273 users,  load average: 173.54, 175.16, 171.59\n'
                       #stdout.strip().split()[0].split(':')[0].strip()
                   print(uptime_string)


            # Close the SSH Client Connection to Remote Server
            ssh_client.close()

        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException) as e:
            print("> {}".format(e))
        '''

    ## Test case-4: Create a file on the ‘Frontend’ Server and transfer it to the ‘Backend’ Server.
    def test_file_transfer_between_servers(self):
        response1 = self.client.list_users()
        pprint("\n====List all Users=======\n")
        pprint(response1)
        pass

    '''
    As mentioned above in Testcase #2, Proposing solutions

    # For GBs of file tranfer we could span several threads for quicker copy for Cross-geo remote file copies usecase.
    1. i) Get the ip address of server using: 'hostname -i' or 'ifconfig | grep 'inet addr:'
        Create a file on Server-1, write data and copy using:
        we can use 'subprocess' module to send commands to linux console.

        root@tryit-ruling:~# echo "Profitbricks" >> pradeep.txt                                                                                                        
        root@tryit-ruling:~# cat pradeep.txt                                                                                                                           
        ProfProfitbricks  

        ii) SFTP ssh client using paramiko library as mentioned in testcase#2 code
            - Then send exec_command like: 
            sftp = paramiko.SFTPClient.from_transport()
            sftp.listdir(dir_path)
            # stdin, stdout, stderr = ssh_client.exec_command('ifconfig')
            # pprint(stdout.read())

        or using generator like: os.walk --> Transfer all files
            # for f in os.walk(dir_path)[2]:

        iii) a) Copy can be done via: paramiko SFTP client constructor using put/get methods
                # download
                ftp_client=ssh_client.open_sftp()
                ftp_client.get(‘remotefileth’,’localfilepath’)
                ftp_client.close()
                # uploading to server
                ftp_client=ssh.open_sftp()
                ftp_client.put(‘localfilepath’,remotefilepath’)
                ftp_client.close()
             b) using scp and shutil
                    with open(src, 'rb') as fin:
                            with open(dst_dir, 'wb') as fout:
                                shutil.copyfile(fin, fout, 128*1024)

            >> This logic can be futher improved if we can span several threading agents for quicker copy for Cross-geo remote file copies.
    '''

## Check the NIC IPs & Print the data center properties and nested resources with depth
# response = self.client.get_datacenter(datacenter_id=self.datacenter_id, depth=5)
#print(json.dumps(response, indent=4))

if __name__ == '__main__':
    unittest.main()