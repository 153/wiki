#!/usr/bin/env python3 

import os, cgi, shutil
import time, re, mistune
import atom
import cgitb
import webtools as wt 
cgitb.enable()

form = cgi.FieldStorage()
markdown = mistune.Markdown()

w_conf = {"pages":"./pages/", \
          "links":"./pages/links.txt", \
          "ips":"./ips.txt", \
          "url":"/wiki"} # change me as needed

def do_atom():
    atom.main()

    
def main():
    if wt.get_form('m') == "atom":
        do_atom()
        return
    print(wt.head('wiki'))
    print(wt.grab_html('head'))    
    print("<body>")
    cgi_modes = ["view", "hist", "link", "rec", "edit", "create"]
    do_mode = wt.get_form('m')
    if not do_mode or do_mode not in cgi_modes:
        w_view("FrontPage")
        return
    w_page = wt.get_form('p')
    if w_page:
        w_page = w_page.replace('.', '').replace('/', '').strip()\
            .replace(u"\uFFFD", "?")
    if w_page not in ["FrontPage", "None", None]:
        print("<a href='.'>&lt; &lt; home</a>")
        if do_mode not in ["view", "create"]:
            print("| <a href='.?m=view;p={0}'>&lt; back</a>".format(w_page))
    elif do_mode in ["link", "hist", "create", "rec"]:
        print("<a href='.'>&lt; &lt; home</a>") #.format(w_conf['url']))
        
    do_it = f"w_{do_mode}('{w_page}')"
    if do_mode in cgi_modes:
        eval(do_it)

def w_view(p=''):
    if not p:
        p = "FrontPage"
    if p != "FrontPage":
            print("| <a href='?m=hist;p={0}'>hist</a>".format(p))
            print(". <a href='?m=edit;p={0}'>edit</a><hr>".format(p))
    page_loc = w_conf['pages'] + p + ".txt"
    if not os.path.isfile(page_loc):
        print("<h2>404 error!!</h2>Sorry,", p, "</i> doesn't exist.")
        print(f"<p>Would you like to <a href='?m=create;p={p}'>create</a> it?")
        return
    with open(page_loc, "r") as w_page:
        w_page = w_page.read().splitlines()
    w_title = "<h3><a href='?m=link;p=" + p + "'>" + p + "</a></h3>"
    w_body = "\n".join(w_page[2:]).replace('&#39;', "'").replace('<', '&lt;')
    w_links = []
    n_links = []
    for m in re.finditer(r"\b([A-Z][a-z]+){2,}\b", w_body):
        if os.path.isfile(w_conf['pages'] + m.group() + ".txt"):
            w_links.append(m.group())
        else:
            n_links.append(m.group())
    for m in re.finditer(r"\[\[(.*?)\]\]", w_body):
        m = m.group()
        if not set(m) & set(w_links):
            if os.path.isfile(w_conf['pages'] + m[2:-2] + ".txt"):
                w_links.append(m)
            else:
                n_links.append(m)
    for link in set(list(w_links)):
        links2 = "<a style='color: #284' href='?m=view;p=" + link + "'>" + link + "</a>"
        if "[[" and "]]" in links2:
            links2 = links2.replace("[[", "").replace("]]", "")
        w_body = w_body.replace(link, links2)
    for link in set(list(n_links)):
        links2 = link + "<a style='color:#d84' href='?m=create;p=" + link + "'>X</a>"
        if "[[" and "]]" in links2:
            links2 = links2.replace("[[", "").replace("]]", "")
        w_body = w_body.replace(link, links2)
    w_body = w_body.replace("</a>'", "</a>").replace('&gt;', '>')
    if w_title != "<h3>404</h3>":
        w_body = markdown(w_body)
    print(w_title, w_body)

def w_edit(p=''):
    locked = ["PostModern", "AveryMorrow", "Shii",
              "MarkDown"]
    if p not in locked:
        do_edit(p)
        return

def w_hist(p='', np=0):
    if not p:
        return
    links = sorted(os.listdir(w_conf['pages']))
    hists = []
    print("<hr>")
    for link in links:
        if p+"." not in link or p == "link":
            continue
        with open(w_conf['pages'] + link) as page:
            page = page.read().splitlines()
            wc = len(" ".join(page[2:]).split(" "))
            page = page[1].split(' ')
            d_string = '%y.%m.%d %H:%M'
            page[0] = time.localtime(int(page[0]))
            page[0] = time.strftime(d_string, page[0])
            hists.append([link, page, wc])
    if np is 1:
        return str(p+'.txt.'+ str(len(hists)))
    if len(hists) == 0:
        print("Page does not exist.")
        return
    print(len(hists), "copies of", p, "on disk:<br>")
    lwc = 0
    nwc = ''
    hists.append(hists.pop(0))
    for i in hists:
        if i[2] > lwc:
            nwc = "+" + str(i[2]-lwc)
        elif i[2] < lwc:
            nwc = "-" + str(lwc-i[2])
        else:
            nwc = "+0"
        lwc = int(i[2])
        print("<br> @", i[1][0], "by", i[1][1])
        print("["+str(lwc)+"w // "+nwc+"w]")

def w_create(p=''):
    if not p:
        print(wt.grab_html('create'))
    else:
        do_edit(p, "create")

def w_publish(p='', n='', sb='', art=''):
#    print("<p>", wt.get_form('sb'), "<br>", wt.get_form('p'), \
#          "<br>")
    p = wt.get_form('p').replace('.', '')\
                        .replace('/', '').replace(u"\uFFFD", "?")
    art = wt.get_form('article').replace(u"\uFFFD", "?")
    meta = wt.get_form('sb') + " " + wt.get_form('n')
    if os.path.isfile(w_conf['pages'] + p + ".txt"):
        bckup = w_conf['pages'] + w_hist(p, 1)
        shutil.copyfile(w_conf['pages'] + p + ".txt", bckup)
        
    with open(w_conf['pages'] + p + ".txt", "w") as wp:
        page = "\n".join([p, meta, art])
        wp.write(page)
        print("<p>Page", p, "written!")
    with open(w_conf['ips'], "a") as ipl:
        ip = os.environ["REMOTE_ADDR"]
        ip = "|".join([ip, p, meta+"\n"])
        ipl.write(ip)
    link_list = []
    with open(w_conf['links'], 'r+') as w_links:
        w_ll = w_links.read().splitlines()
        new_links = wt.get_form('wl').replace('[[', '').replace(']]', '')
        new_links = new_links.split(" ")
        for link in w_ll:
            link = link.replace("[[", "").replace("]]","")
            link = link.split(':')
            if link[0] in new_links and p not in link[1]:
                link_list.append(link[0] + ":" + link[1] + " " + p)
            elif link[0] not in new_links and p in link[1]:
                link_list.append(link[0] + ":" + link[1].replace(p, '').replace('  ', ' ').strip())
            elif link[0] is p:
                link_list.append(link[0] + ":" + link[1])
                new_links.remove(link[0])
            else:
                link_list.append(link[0] + ":" + link[1])
            if link[0] in new_links:
                new_links.remove(link[0])
        for l in new_links:
            l = l.replace('[[', '').replace(']]', '')
            link_list.append(l + ":" + p)
        link_list = sorted(link_list)
        print("<br>Redirecting you back in five seconds...")
        print("<meta http-equiv='refresh' content='5; ", \
              "url=?m=view;p={0}'>".format(p))
        w_links.seek(0)
        w_links.write("\n".join(link_list))
        w_links.truncate()
        
def w_rec(p=0):
    if not p:
        p = 0
    fir_num = int(p)
    print("<hr>")
    print("<a href='?m=atom'>")
    print('<img src="/bbs/img/rss.png">')
    print("</a> Last 30 changes:")
    edits = []
    with open(w_conf['ips'], 'r') as ips:
        ips = ips.read().splitlines()
        for ip in ips:
            ip = ip.split("|")
            ip.append(ip[2].split(" ")[1])
            ip[2] = ip[2].split(" ")[0]
                # [2] page, [3] time, [4] name
            edits.append(ip[1:])
    edits.reverse()
    print("<pre style='line-height:1em'><ul style='border:0;padding:0 3%;margin:0'>")
    edits = edits[:30]
    for n, ip in enumerate(edits):
        ip[1] = time.localtime(int(ip[1]))
        ip[1] = time.strftime('%y.%m.%d %H:%M', ip[1])
        print("<li>[{1}]: <a href='?m=view;p={0}'>{0}</a>, {2}".format(*ip))
    print("</ul></pre>")

def do_edit(p='', e_m=''):
    if wt.get_form('sb'):
        w_publish()
    elif wt.get_form('name') and \
         wt.get_form('name') != 'viagra':
        print("hi spambot")
    elif wt.get_form('email'):
        print("bye")
    elif p:
        print("<hr>")
        page_loc = w_conf['pages'] + p + ".txt"
        art = ''
        if not os.path.isfile(page_loc):
            e_m = 'create'
        else:
            e_m = 'edit'
            with open(page_loc) as art:
                art = art.read().splitlines()
                by = art[1].split(" ")
                art = "\n".join(art[2:]).replace("&#39;", "'")\
                                        .replace("&gt;", ">")
            by[0] = wt.fancy_time(int(by[0]), "human")
            print("last edited", by[0], "by", by[1], "<br>")
        if wt.get_form('article'):
            art = wt.get_form('article')\
                    .replace("&#39;", "'")\
                    .replace("&gt;", ">")\
                    .replace(u"\uFFFD", "?")
        if wt.get_form('n'):
            p_name = wt.get_form('n')
            if not p_name[0].isalpha() or p_name == 'Anonymous':
                p_name2 = 'AnonymousUser'
            else:
                p_name2 = "User" + p_name.capitalize()
        else:
            p_name = 'Anonymous'
            p_name2 = 'AnonymousUser'
        e_utime = wt.fancy_time(None, "unix")
        e_ltime = wt.fancy_time(None, "human")
        print("// You are:", p_name2)
        print("// Time:", e_ltime)

        p_art = art.replace(u"\uFFFD", "?").replace("&amp;", "&")

        w_links = []
        w_links2 = []
        for m in re.finditer(r"\b([A-Z][a-z]+){2,}\b", p_art):
            if not set(m.group()) & set(w_links):
                if os.path.isfile(w_conf['pages'] + m.group() + ".txt"):
                    w_links.append(m.group())
                else:
                    w_links2.append(m.group())
        for m in re.finditer(r"\[\[(.*?)\]\]", p_art):
            m = m.group()
            if not set(m) & set(w_links):
                if os.path.isfile(w_conf['pages'] + m[2:-2] + ".txt"):
                    w_links.append(m)
                else:
                    w_links2.append(m)
        w_links = list(set(w_links))
        w_links2 = list(set(w_links2))
        p_art2 = p_art.replace('&gt;', '>')
        for link in w_links:
            link2 = "<a style='color:#284' href='?m=view;p=" + link + "'>" + link + "</a>"
            if "[[" and "]]" in link2:
                link2 = link2.replace("[[", "").replace("]]", "")
            p_art2 = p_art2.replace(link, link2)
        for n_link in w_links2:
            link2 = n_link + "<a style='color:#d84' " \
                      + "href='?m=create;p=" + n_link +"'>X</a>"
            if "[[" and "]]" in link2:
                link2 = link2.replace("[[", "").replace("]]", "")
            p_art2 = p_art2.replace(n_link, link2)
        p_art2 = p_art2.replace("</a>'", "</a>")
        p_art = p_art.replace("'", '&#39;').replace(">", "&gt;")
        p_art2 = p_art2.replace("&#39;", "'")
        if w_links:
            w_links = " ".join(w_links)
        if w_links and w_links2:
            for i in w_links2:
                w_links += " " + i
        if p_art2:
            print("<hr><h3><form method='post' action='.'> Preview:")
            print("<input type='submit' value='Publish'>")
        print("""<input type='hidden' name='sb' value='{0}'>
<input type='hidden' name='p' value='{1}'>
<input type='hidden' name='n' value='{2}'>                
<input type='hidden' name='m' value='{5}'>
<input type='hidden' name='article' value='{3}'>
<input type='hidden' name='wl' value='{4}'>
""".format(e_utime, p, p_name, p_art.replace(u"\uFFFD", "?"), w_links, e_m))
        print("</form></h3>")
        print(markdown(p_art2))
        print("<hr>")
        p_art = p_art
        with open("edit.html", 'r') as p_create:
            p_create = p_create.read()
            print(p_create.format(e_m, p, p_art, p_name))

            return

def w_link(p=''):
    if not p:
        links = sorted(os.listdir(w_conf['pages']))
        for link in links:
            if link[-4:] == ".txt":
                continue
            links.remove(link)
        links.remove('404.txt')
        links.remove('links.txt')
        print("<hr>All pages on <a href='?m=view;p=ThisWiki'>ThisWiki</a>:<ol>")
        for link in links:
            if link[-4:] == '.txt':
                print("<li><a href='?m=view;p=" + link[:-4] +"'>", link[:-4], "</a>")
        print("</ol>")
    with open(w_conf['links'], 'r') as link_list:
        for link in link_list:
            link = link.split(':')
            if link[0] != p:
                pass
            else:
                print("<hr>Pages that link here: <ul>")
                for p in sorted(link[1].split(" ")):
                    print("<li><a href='?m=view;p=" + p + "'>", \
                          p, "</a>")
                break
    return
main()
