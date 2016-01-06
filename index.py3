#!/bin/python3 

import os, cgi, cgitb, shutil
import time, re, mistune

form = cgi.FieldStorage()
markdown = mistune.Markdown()

w_conf = {"pages":"./pages/", \
          "links":"./pages/links.txt"}

def main():
    print("Content-type: text/html\n")
    print("<style> a {color: #00c}</style>")
    print("<body style='width:700px'>")
    cgi_modes = ["edit", "create", "view", "hist", "link"]
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
            if w_page is "links":
                w_page = ''
        print(do_mode, w_page)
        print("<br><a href='/wiki/'>&lt; &lt; home</a>")
        if do_mode == "view":
            w_view(w_page)
        elif do_mode == "create":
            w_create(w_page)
        elif do_mode == "edit":
            print("<a href='/wiki/?m=view;p={0}'>&lt; back</a><br>".format(w_page))
            w_edit(w_page)
        elif do_mode == "link":
            print("<a href='/wiki/?m=view;p={0}'>&lt; back</a><br>".format(w_page))
            w_links(w_page)
        elif do_mode == "hist":
            w_hist(w_page)

def w_view(p=''):
    if p:
        print("| <a href='?m=hist;p={0}'>hist</a> |".format(p))
        print("<a href='?m=edit;p={0}'>edit</a> |".format(p))
        page_loc = w_conf['pages'] + p + ".txt"
        print(page_loc, "<hr>")
        if os.path.isfile(page_loc):
            with open(page_loc, "r") as w_page:
                w_page = w_page.read().splitlines()
                w_title = "<h3><title>Wiki: " + p \
                          + "</title><a href='?m=link;p=" + p \
                          + "'>" + p + "</a></h3>"
                w_date = w_page[1]
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
            w_view("404")
            print(p + "</i> doesn't exist.")
            print("<p>Would you like to ")
            print("<a href='?m=create;p={0}'>create</a> it?".format(p))
    else:
        w_view("FrontPage")

def w_edit(p=''):
    if p:
        print(p)
        do_edit(p)
        return
        with open(w_conf[0][1] + p + ".txt", 'r') as page:
            page = page.read().splitlines()
            print("<h3>", page[0], "</h3>")
            print("<title>Edit", page[0], "</h3>")
            page[1] = page[1].split(' ')
            l_edit = int(page[1].pop(0))
            l_edit = time.localtime(l_edit)
            d_string = '%Y-%m-%d [%a] %H:%M'
            l_edit = time.strftime(d_string, l_edit)
            l_author = page[1].pop(0)
            print("by", l_author, "at", l_edit, "<br>")
            print("<textarea style='width: 80%;height:50%'>", w_page, "</textarea>")
    return

def w_hist(p='', np=0):
    if p:
        links = sorted(os.listdir(w_conf['pages']))
        hists = []
        print("<br>")
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
            print("["+str(lwc)+" // "+nwc+"]")

def w_create(p=''):
    if not p:
        print("<p>Before creating a page, ask yourself whether",
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
    art = form.getvalue('article')
    meta = cgi.escape(form.getvalue('sb')) + " " + cgi.escape(form.getvalue('n'))
    if os.path.isdir(w_conf['pages'] + p + ".txt"):
        bckup = w_conf['pages'] + w_hist(p, np=1)
        shutil.copyfile(w_conf['pages'] + p + ".txt", bckup)
        
    with open(w_conf['pages'] + p + ".txt", "w") as wp:
        page = "\n".join([p, meta, art])
        wp.write(page)
        print("Page", p, "written!")
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

def do_edit(p='', e_m=''):
    if form.getvalue('sb'):
        w_publish()
    elif p:
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
            print("<br>last edited at")
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
            print(e_ltime)
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
            print("</h3></form>")
            print("<hr>")
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
        links.remove('404.txt')
        links.remove('links.txt')
        print("<hr>", len(links), "pages currently exist on ThisWiki.")
        print("<ul>")
        for link in links:
            if link[-4:] == ".txt":
                print("<li><a href='?m=view;p=" + link[:-4] +"'>", link[:-4], "</a>")
        print("</ul>")
    with open(w_conf['links'], 'r') as link_list:
        for link in link_list:
            link = link.split(':')
            if link[0] != p:
                pass
            else:
                print("<p>Pages that link here: <ul>")
                for p in sorted(link[1].split(" ")):
                    print("<li><a href='?m=view;p=" + p + "'>", \
                          p, "</a>")
                break
    return
main()
