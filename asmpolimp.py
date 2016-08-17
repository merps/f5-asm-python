#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import re
import os

__author__ = 'Michael Kennedy'
__version__ = '0.02'
__contact__ = 'michael.kennedy@strutdigital.com'

# setup of stuff to connect
f5_host = '192.168.68.128'
f5_port = '443'
f5_login = 'admin'
f5_pass = 'admin'

# stuff that shouldn't change
asm = requests.session()
asm.auth = ('admin', 'admin')
asm.verify = False
asm.headers.update({'Content-Type': 'application/json'})
asm_url_base = ('https://%s:%s/mgmt/tm/asm' % (f5_host, f5_port))

# lets try with doing an read of the files first...
try:
    for filename in os.listdir():
        if filename.endswith(".xml"):

            # lets upload the policy files
            data = open(filename, 'r')
            headers = {'Content-Length': os.path.getsize(filename), 'Content-Type': 'application/xml'}
            upload_asm_policies = asm.post('{0}/file-transfer/uploads/{1}'.format(asm_url_base, filename), data, headers)

            # lets figure out the policy names
            policy_tree = ET.parse(filename)
            policy_root = policy_tree.getroot()
            policy_fullname = policy_root[0][2].text
            name = re.search(r'\/.*\/([^-]*)', policy_fullname).group(1)
            print(name)

            # lets thrown the payload at it
            payload = {
                "filename": "%s" % filename,
                "name": "%s" % name
            }
            import_ams_policies = asm.post(('%s/tasks/import-policy/' % asm_url_base), json=payload).json()
except ():
    print("nothing to see here!")