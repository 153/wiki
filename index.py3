#!/bin/python3 

import os, cgi, shutil
import time, re, mistune

form = cgi.FieldStorage()
markdown = mistune.Markdown()

w_conf = {"pages":"./pages/", \
          "links":"./pages/links.txt", \
          "ips":"./ips.txt", \
          "rec":20, \
          "url":"/wiki/"} # change me as needed

def main():
    print("Content-type: text/html\n")
    print("<title>wiki</title>")
    print('<meta name="viewport" content="width=device-width" />')
    print("""<style> a {color: #00c}
body {font-size: 1em;
line-height: 1.44;
max-width: 700px;
font-weight:400;}
img {max-width:100%}
p {margin-bottom: 1.3em;}
h1, h2, h3, h4 {
  margin:0.5em 0 0.5em;
  line-height: 1.2;}

</style>""")
    print("<body>")
    cgi_modes = ["edit", "create", "view", "hist", "link", "rec"]
    do_mode = form.getvalue('m')
    if not do_mode:
        w_view("FrontPage")
    elif not do_mode in cgi_modes:
        w_view("FrontPage")
    else:
        do_mode = cgi.escape(do_mode)
        w_page = form.getvalue('p')
        if w_page:
            w_page = cgi.escape(w_page).replace('.', 'o').replace('/', "l")
        if w_page not in ["FrontPage", "None", None]:
            print("<a href='{0}'>&lt; &lt; home</a>".format(w_conf['url']))
            if do_mode not in ["view", "create"]:
                print("| <a href='{1}?m=view;p={0}'>&lt; back</a>".format(w_page, w_conf['url']))
        elif do_mode in ["link", "hist", "create", "rec"]:
            print("<a href='{0}'>&lt; &lt; home</a>".format(w_conf['url']))
            
        if do_mode == "view":
            w_view(w_page)
        elif do_mode == "create":
            w_create(w_page)
        elif do_mode == "edit":
            w_edit(w_page)
        elif do_mode == "link":
            w_links(w_page)
        elif do_mode == "hist":
            w_hist(w_page)
        elif do_mode == 'rec':
            w_rec(w_page)

def w_view(p=''):
    if p:
        if p != "FrontPage":
            print("| <a href='?m=hist;p={0}'>hist</a> |".format(p))
            print("<a href='?m=edit;p={0}'>edit</a><hr>".format(p))
        page_loc = w_conf['pages'] + p + ".txt"
        if os.path.isfile(page_loc):
            with open(page_loc, "r") as w_page:
                w_page = w_page.read().splitlines()
                w_title = "<h3><a " + \
                           "href='?m=link;p=" + p + "'>" + p + "</a></h3>"
                w_body = "\n".join(w_page[2:]).replace('&#39;', "'").replace('<', '&lt;')
                w_links = []
                n_links = []
                for m in re.finditer(r"\b([A-Z][a-z]+){2,}\b", w_body):
                    if os.path.isfile(w_conf['pages'] + m.group() + ".txt"):
                        w_links.append(m.group())
                    else:
                        n_links.append(m.group())
                for link in set(list(w_links)):
                    links2 = "<a style='color: #284' href='?m=view;p=" + link + "'>" + link + "</a>"
                    w_body = w_body.replace(link, links2)
                for link in set(list(n_links)):
                    links2 = link + "<a style='color:#d84' href='?m=create;p=" + link + "'>X</a>"
                    w_body = w_body.replace(link, links2)
                w_body = w_body.replace("</a>'", "</a>")
                if w_title != "<h3>404</h3>":
                    w_body = markdown(w_body)
                print(w_title, w_body)
                
        else:
            print("<h2>404 error!!</h2>Sorry,")
            print(p + "</i> doesn't exist.")
            print("<p>Would you like to ")
            print("<a href='?m=create;p={0}'>create</a> it?".format(p))
    else:
        w_view("FrontPage")

def w_edit(p=''):
    if p:
        do_edit(p)
        return

def w_hist(p='', np=0):
    if p:
        links = sorted(os.listdir(w_conf['pages']))
        hists = []
        print("<hr>")
        for link in links:
            if p+"." not in link:
                continue
            if re.match(r"([A-Z][a-z]+){2,}", p):
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
            
        print(len(hists), "copies of", p, "on disk:<br>")
        lwc = 0
        nwc = ''
        hists.append(hists.pop(0))
        for i in hists:
            if i[2] > lwc:
                nwc = "+" + str(i[2]-lwc)
            elif i[2] < lwc:
                nwc = "-" + str(lwc-i[2])
            lwc = int(i[2])
            print("<br> @", i[1][0], "by", i[1][1])
            print("["+str(lwc)+"w // "+nwc+"w]")

def w_create(p=''):
    if not p:
        print("<hr>Before creating a page, ask yourself whether",
              "it would be a good fit for this wiki. Type the",
              "name in CamelCase with no digits or special",
              "characters.")
        print("<p><form action='.' method='post'>")
        print("<input type='hidden' name='m' value='create'>")
        print("<input type='text' name='p'>")
        print("<input type='submit' value='Create'>")
        print("</form>")
    else:
        do_edit(p, "create")

def w_publish(p='', n='', sb='', art=''):
    print("<p>", form.getvalue('sb'), "<br>", form.getvalue('p'), \
          "<br>")
    p = cgi.escape(form.getvalue('p')).replace('.', 'o').replace('/', 'l')
    art = cgi.escape(form.getvalue('article'))
    meta = cgi.escape(form.getvalue('sb')) + " " + cgi.escape(form.getvalue('n'))
    if os.path.isfile(w_conf['pages'] + p + ".txt"):
        bckup = w_conf['pages'] + w_hist(p, 1)
        shutil.copyfile(w_conf['pages'] + p + ".txt", bckup)
        
    with open(w_conf['pages'] + p + ".txt", "w") as wp:
        page = "\n".join([p, meta, art])
        wp.write(page)
        print("Page", p, "written!")
    with open(w_conf['ips'], "a") as ipl:
        ip = os.environ["REMOTE_ADDR"]
        ip = "|".join([ip, p, meta+"\n"])
        ipl.write(ip)
    link_list = []
    with open(w_conf['links'], 'r+') as w_links:
        w_ll = w_links.read().splitlines()
        new_links = form.getvalue('wl').split(" ")
        for link in w_ll:
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
            link_list.append(l + ":" + p)
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
    sec_num = p + w_conf['rec']
    print("<hr>")
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
    print("<ul>")
    for n, ip in enumerate(edits):
        ip[1] = time.localtime(int(ip[1]))
        ip[1] = time.strftime('%y.%m.%d %H:%M', ip[1])
        print("<li>[{1}]: <a href='?m=view;p={0}'>{0}</a>, {2}".format(*ip))
    print("</ul>")

def do_edit(p='', e_m=''):
    if form.getvalue('sb'):
        w_publish()
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
                art = "\n".join(art[2:]).replace("&#39;", "'")
            print("last edited at")
            d_string = '%Y-%m-%d [%a] %H:%M'
            by[0] = time.localtime(int(by[0]))
            by[0] = time.strftime(d_string, by[0])
            print(by[0], "by", by[1], "<br>")
        if form.getvalue('article'):
            art = form.getvalue('article').replace("&#39;", "'")
        if 1:
            if form.getvalue('n'):
                p_name = cgi.escape(form.getvalue('n')).strip()
                if not p_name[0].isalpha() or p_name == 'Anonymous':
                    p_name2 = 'AnonymousUser'
                else:
                    p_name2 = "User" + p_name.capitalize()
            else:
                p_name = 'Anonymous'
                p_name2 = 'AnonymousUser'
            print("// You are:", p_name2)
            print("// Time:")
            d_string = '%Y-%m-%d [%a] %H:%M'
            e_utime = int(time.time())
            e_ltime = time.localtime(e_utime)
            e_ltime = time.strftime(d_string, e_ltime)
            print(e_ltime, "<hr>")
            p_art = cgi.escape(art)
            w_links = []
            w_links2 = []
            for m in re.finditer(r"\b([A-Z][a-z]+){2,}\b", p_art):
                if not set(m.group()) & set(w_links):
                    if os.path.isfile(w_conf['pages'] + m.group() + ".txt"):
                        w_links.append(m.group())
                    else:
                        w_links2.append(m.group())
            w_links = list(set(w_links))
            w_links2 = list(set(w_links2))
            p_art2 = p_art
            for link in w_links:
                link2 = "<a style='color:#284' href='?m=view;p=" + link + "'>" + link + "</a>"
                p_art2 = p_art2.replace(link, link2)
            for n_link in w_links2:
                link2 = n_link + "<a style='color:#d84' " \
                          + "href='?m=create;p=" + n_link +"'>X</a>"
                p_art2 = p_art2.replace(n_link, link2)

            p_art2 = p_art2.replace("</a>'", "</a>")
            p_art = p_art.replace("'", '&#39;')
            p_art2 = p_art2.replace("&#39;", "'").replace('&gt;', '>')
            if w_links:
                w_links = " ".join(w_links)
            print("""<h3><form method='post' action='.'>
Preview: 
<input type='submit' value='Publish'>
<input type='hidden' name='sb' value='{0}'>
<input type='hidden' name='p' value='{1}'>
<input type='hidden' name='n' value='{2}'>                
<input type='hidden' name='m' value='{5}'>
<input type='hidden' name='article' value='{3}'>
<input type='hidden' name='wl' value='{4}'>
""".format(e_utime, p, p_name, p_art, w_links, e_m))                
            print("</form></h3>")
            print(markdown(p_art2))
            print("<hr>")
        else:
            p_art = ''
            p_name = ''
        with open("edit.html", 'r') as p_create:
            p_create = p_create.read()
            print(p_create.format(e_m, p, p_art, p_name))
    return

def w_links(p=''):
    if not p:
        links = sorted(os.listdir(w_conf['pages']))
        for link in links:
            if link[-4:] == ".txt":
                continue
            links.remove(link)
        links.remove('404.txt')
        links.remove('links.txt')
        print("<hr>", len(links), "pages currently exist on ThisWiki.")
        print("<ul>")
        for link in links:
            if link[-4:] == '.txt':
                print("<li><a href='?m=view;p=" + link[:-4] +"'>", link[:-4], "</a>")
        print("</ul>")
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
