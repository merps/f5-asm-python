#!/usr/bin/env python3
import requests
import time

__author__ = 'Michael Kennedy'
__version__ = '0.05'
__contact__ = 'michael.kennedy@strutdigital.com'

# --------------------------------------#
# setup of stuff to connect
# --------------------#
f5_host = '192.168.68.128'
f5_port = '443'
f5_login = 'admin'
f5_pass = 'admin'

# --------------------------------------#
# stuff that shouldn't change
# --------------------#
asm = requests.session()
asm.auth = ('admin', 'admin')
# asm.auth = ('%s', '%s' % f5_login, f5_pass)
asm.verify = False
asm.headers.update({'Content-Type': 'application/json'})
asm_url_base = ('https://%s:%s/mgmt/tm/asm' % (f5_host, f5_port))
get_policies_id = {}
export_policies_id = {}


# --------------------------------------#
# Get the ASM policies for exports
# --------------------#
def getasmpolicies():
    # lets try getting the output
    try:
        get_asm_policies = asm.get('%s/policies/?$select=id' % asm_url_base).json()
        # sticking it in a dictionary as [id:softLink] from policies
        for x in get_asm_policies['items']:
            k = x['id']
            val = str(x['selfLink']).replace('localhost', '%s' % f5_host)
            get_policies_id[k] = val
    # if we break stuff-age
    except (ValueError, KeyError, TypeError):
        print("JSON format error")
    return get_policies_id


# --------------------------------------#
# Start ASM exports for download
# --------------------#
def exportasmpolicies(policies_id):
    # let's fire off the requests for exports
    for pol_id in policies_id:
        export = {"filename": "exported_%s.xml" % pol_id,
                  "minimal": "false",
                  "policyReference": {
                     "link": "https://%s:%s/mgmt/tm/asm/policies/%s" % (f5_host, f5_port, pol_id)}}
        export_asm_responses = asm.post(('%s/tasks/export-policy/' % asm_url_base), json=export).json()
        key = export_asm_responses['id']
        value = export_asm_responses['filename']
        export_policies_id[key] = value
        return export_policies_id


# --------------------------------------#
# Test if ASM exports are completed
# --------------------#
def asmexportcheck(exports_id):
    # let's do some functional testing of the load
    try:
        for export_id in exports_id:
            asm_export_status = asm.get("%s/tasks/export-policy/%s" % (asm_url_base, export_id)).json()
            while (asm_export_status['status']) != 'COMPLETED':
                asm_export_status = asm.get("%s/tasks/export-policy/%s" % (asm_url_base, export_id)).json()
                time.sleep(5)
    except (ValueError, KeyError, TabError):
        print("what the smeg are you doing?")


# --------------------------------------#
# Write out the ASM Policies
# --------------------#
def writeasmpolicies(export_policies):
    # lets write to file
    for files in export_policies.values():
        asm_xml_policies = asm.get(('%s/file-transfer/downloads/%s' % (asm_url_base, files)), stream=True)
        with open(files, 'wb') as fd:
            for chunk in asm_xml_policies.iter_content(chunk_size=1024):
                fd.write(chunk)


# --------------------------------------#
# MAIN ENTRY POINT
# --------------------#
def main():
    if getasmpolicies():
        exportasmpolicies(get_policies_id)
        asmexportcheck(export_policies_id)
        writeasmpolicies(export_policies_id)
    else:
        print('No policies to export')

if __name__ == "__main__":
    error = main()
    if error:
        print("error")
    else:
        print("success")
