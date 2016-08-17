#!/usr/bin/env python3
import requests
import time

__author__ = 'Michael Kennedy'
__version__ = '0.03'
__contact__ = 'michael.kennedy@strutdigital.com'

# setup of stuff to connect
f5_host = '192.168.68.128'
f5_port = '443'
f5_login = 'admin'
f5_pass = 'admin'

# stuff that shouldn't change
asm = requests.session()
asm.auth = ('admin', 'admin')
# asm.auth = ('%s', '%s' % f5_login, f5_pass)
asm.verify = False
asm.headers.update({'Content-Type': 'application/json'})
asm_url_base = ('https://%s:%s/mgmt/tm/asm' % (f5_host, f5_port))
get_policies_id = {}
export_polices_id = {}


get_asm_policies = asm.get('%s/policies/?$select=id' % asm_url_base).json()
try:
    # decoded = json.loads(get_asm_policies)
    # sticking it in a dictionary as [id:softLink] from policies
    for x in get_asm_policies['items']:
        k = x['id']
        val = str(x['selfLink']).replace('localhost', '%s' % f5_host)
        get_policies_id[k] = val
# if we break stuff-age
except (ValueError, KeyError, TypeError):
    print("JSON format error")

# let's fire off the requests for exports
for pol_id in get_policies_id:
    data = {"filename": "exported_%s.xml" % pol_id,
            "minimal": "false",
            "policyReference": {
                "link": "https://%s:%s/mgmt/tm/asm/policies/%s" % (f5_host, f5_port, pol_id)}
            }
    export_asm_results = asm.post(('%s/tasks/export-policy/' % asm_url_base), json=data).json()
    key = export_asm_results['id']
    value = export_asm_results['filename']
    export_polices_id[key] = value

for files in export_polices_id.values():
    asm_xml_policies = asm.get(('%s/file-transfer/downloads/%s' % (asm_url_base, files)), stream=True)
    with open(files, 'wb') as fd:
        for chunk in asm_xml_policies.iter_content(chunk_size=1024):
            fd.write(chunk)
    time.sleep(30)