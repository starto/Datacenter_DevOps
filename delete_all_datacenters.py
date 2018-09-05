from profitbricks.client import ProfitBricksService
from pprint import pprint
import json

import logging
import re
import xml.etree.ElementTree
import datetime
import getpass

client = ProfitBricksService(username='pradeep.6174@gmail.com', password='prad1234P%')

# Delete all existing datacenters in your account
datacenters = client.list_datacenters()

for d in datacenters['items']:
    vdc = client.get_datacenter(d['id'])
    name = vdc['properties']['name']
    datacenter_id = vdc['id']
    pprint(datacenter_id)

    del_response = client.delete_datacenter(vdc['id'])
    pprint(del_response)

'''
    #image='4142dc86-953b-11e8-af82-525400f64d8d',
    pprint("Image start")
    image = "Ubuntu-16.04-LTS-server-2018-09-01"
    for image_item in client.list_images()['items']:
        each_image = image_item['properties']['name']
        # if each_image.startswith('Ubuntu'):
        if each_image == image and image_item['properties']['location'] == 'de/fra':
            break

    image_id = image_item['id']
    pprint(image_item)
    print("\n\n\n\n ==== Found Image=====\n\n")
    pprint(image_id)
'''

    # for image_item in self.client.list_images()['items']:
    #     each_image = image_item['properties']['name']
    #     # if each_image.startswith('Ubuntu'):
    #     if each_image == image_to_boot:
    #         break
    #         # image_id = image_item['id']
    #         # pprint(image_id)
    #         # break
    #
    # image_id = image_item['id']
    # print("\nAfter the image_id:", image_id)
    # print(image_id)
