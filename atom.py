import time

metad = {'title': 'wiki', 'aurl': 'http://4x13.net/wiki/?m=atom',
         'surl': 'http://4x13.net/wiki',
         'purl': 'http://4x13.net/wiki/?m=view;p='}
ip_log = "./ips.txt"
s_time = "-08:00"
a_time = "%Y-%m-%dT%H:%M:%S-08:00"

atom = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">'
<title>wiki</title>
<link rel='self' href='""" + metad['aurl'] + """' />
<link href='""" + metad['surl'] + """'/>
<id>""" + metad['aurl'] + """</id>
{0}
</feed>"""

entry = """\n<entry>
<updated>{0}</updated>
<link rel='alternate' href='{1}' />
<title>{2}</title>
<content type='html'>
{3}
</content>
</entry>"""

def wiki2list():
    entry_keys = ["title", "link", "updated",
                  "id", "content"]
    with open(ip_log) as ips:
        ips = ips.read().splitlines()
    for n, i in enumerate(ips):
        if len(i) < 10:
            continue
        i = i.split("|")
        i.append(i[2].split(" ")[0])
        i[0] = i[1]
        i[1] = metad['purl'] + i[0]
        i[2] = time.strftime(a_time, time.localtime(int(i[3])))
        i[3] = i[1] + "#" + i[2]
        i.append(str(i[0] + " was updated on " + i[2][:10]))
        ips[n] = i
        
    return ips
    
def list2atom(p_index=[]):
    if not p_index:
        p_index = wiki2list()
    atom_e = []
    for p in p_index:
        atom_e.append(entry.format(p[2], p[1], p[0], p[4]))
    print(atom.format("\n".join(atom_e[:-30:-1])))

def test():
    with open(ip_log) as ips:
        ips = ips.read().splitlines()        
    entry_list = []
    for i in ips:
        if len(i) < 10:
            continue
        i = i.split("|")
        i.append(i[2].split(" ")[0])
        i[0] = time.strftime(a_time, time.localtime(int(i[3])))
        i[2] = metad['surl'] + "?m=view;p=" + i[1]
        i[3] = time.strftime("%Y-%m-%d %H:%M", \
                             time.localtime(int(i[3])))
        i[3] = str(i[1] + " updated " + i[3])
        entry_list.append(entry.format(i[0], i[2], i[1], i[3]))
        
    entry_list = "\n".join(entry_list[::-1])
    atom = atom.format(entry_list)
    print("Content-type: application/atom+xml\r\n")
    print('<?xml version="1.0" encoding="utf-8"?>')
    print(entry_list.splitlines()[-7])
    print(atom)

def main():
    print("Content-type: application/atom+xml\r\n")
    list2atom(wiki2list())
    
if __name__ == "__main__":
    main()
