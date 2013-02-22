import sys
import re
import fcm

if len(sys.argv) != 2:
    sys.exit("Must provide an FCS file name")

file_name = sys.argv[1]

fcs_data = fcm.loadFCS(file_name)

param_dict_pnn = {}
param_dict_pns = {}

for key in fcs_data.notes.text:
    matches = None
    matches = re.search('^P(\d+)N$', key, flags=re.IGNORECASE)
    if matches:
        param_dict_pnn[int(matches.groups()[0])] = "P%sN: %s" % (matches.groups()[0], fcs_data.notes.text[key])

    matches = None
    matches = re.search('^P(\d+)S$', key, flags=re.IGNORECASE)
    if matches:
        param_dict_pns[int(matches.groups()[0])] = "P%sS: %s" % (matches.groups()[0], fcs_data.notes.text[key])

list = [fcs_data.name]
list.extend([param_dict_pnn[key] for key in sorted(param_dict_pnn.iterkeys())])
list.extend([param_dict_pns[key] for key in sorted(param_dict_pns.iterkeys())])

print ','.join(list)
