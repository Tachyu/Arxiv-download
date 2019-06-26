#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   arxiv-download.py
@Time    :   2019/06/26 09:35:57
@Author  :   Tachyu 
@Version :   1.0
@Contact :   2018104088@ruc.edu.cn
@License :   (C)Copyright 2019-2020
@Desc    :   None
'''

# here put the import lib
from urllib import request,parse
from bs4 import BeautifulSoup
import time
import sys
from gooey import Gooey
from gooey import GooeyParser

import requests 
import threading 
  
def Handler(start, end, url, filename): 
    # specify the starting and ending of the file 
    headers = {'Range': 'bytes=%d-%d' % (start, end)} 
    # request the specified part and get into variable     
    r = requests.get(url, headers=headers, stream=True) 
    # open the file and write the content of the html page  
    # into file. 
    with open(filename, "r+b") as fp: 
        fp.seek(start) 
        var = fp.tell() 
        fp.write(r.content)

def download_file(url_of_file,name,number_of_threads): 
    r = requests.head(url_of_file) 
    if name: 
        file_name = name 
    else: 
        file_name = url_of_file.split('/')[-1] 
    try: 
        file_size = int(r.headers['content-length']) 
    except: 
        print("Invalid URL")
        return

    part = int(file_size) / number_of_threads 
    fp = open(file_name, "wb") 
    # fp.write('\0' * file_size) 
    fp.close() 
    for i in range(number_of_threads): 
        start = int(part * i) 
        end = int(start + part) 
        # create a Thread with start and end locations 
        t = threading.Thread(target=Handler, 
            kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name}) 
        t.setDaemon(True) 
        t.start() 

    main_thread = threading.current_thread() 
    for t in threading.enumerate(): 
        if t is main_thread: 
            continue
        t.join() 


def tag_class_name(tag, key):
    return tag.has_attr('class') and ' '.join(tag['class']).find(key) != -1

def title_class(tag):
    return tag.name=='p' and tag_class_name(tag, 'title')

def result_list(tag):
    return tag.name=='li' and tag_class_name(tag, 'arxiv-result')

def get_id_title(query):
    search = "https://arxiv.org/search/?query={}&searchtype=title&source=header"
    url = search.format(query)
    response = request.urlopen(url)
    html=response.read()
    soup = BeautifulSoup(html,'html.parser')
    result = soup.find_all(result_list)[0]
    titles = result.find_all(title_class)
    arxiv_id = titles[0].text.strip().split('\n')[0].split(':')[-1]
    paper_title = titles[1].text.strip()
    return arxiv_id, paper_title

def filename_replace(filename):
    return filename.replace(':',' ').replace(',',' ')

@Gooey(default_size=(20,20), 
header_bg_color='#b31b1b',
body_bg_color='#b31b1b',
use_legacy_titles=False,
program_name='Arxiv Downloader',
progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
       progress_expr="current / total * 100")
def getfilename():
    parser = GooeyParser(description= "Arxiv downloader with auto-rename")
    parser.add_argument('papertitle', help='Paper title')
    parser.add_argument('thread', default=16, type=int, help='Download thread')
    return parser.parse_args()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # query = 'Representation Learning on Graphs: Methods and Applications'
        getfilename()
        thread = int(sys.argv[-1])
    
    query = ' '.join(sys.argv[1:-1])    
    print('progress: 10/100')
    print('Searching in arxiv...')
    thread = int(sys.argv[-1])

    url_query = query.replace(' ', '+').replace(':','%3A')
    arxiv_id, paper_title = get_id_title(url_query)
    print(arxiv_id, paper_title)
    print('progress: 30/100')
    print('Downloading {} from arxiv,T={}'.format(arxiv_id,thread))
    pdf_url = 'https://arxiv.org/pdf/{}.pdf'.format(arxiv_id)
    filename = filename_replace(paper_title) + '.pdf'
    ts = time.time()
    download_file(url_of_file=pdf_url, name=filename,number_of_threads=thread) 
    te = time.time()
    print('progress: 100/100')
    print('{:.0f}s [Complete] {}'.format(te-ts, filename))