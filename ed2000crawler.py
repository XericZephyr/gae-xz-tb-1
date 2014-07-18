#-*-coding:UTF-8-*-

'''
Section:  Base Crawler
'''

DEFAULT_HEADER = {}

from urllib2 import Request, build_opener, HTTPRedirectHandler
from urlparse import urlsplit, parse_qs
import logging
from lxml import etree


class BaseCrawler():
    
    def open(self, url, headers=DEFAULT_HEADER, data=None):
        req = Request(url, headers=headers)
        if data:
            req.add_data(data)
        opener = build_opener(HTTPRedirectHandler())
        #ProxyHandler({'http': 'http://127.0.0.1:8087', 'https': 'https://127.0.0.1:8087'}))
        return opener.open(req)
    
    def parse(self, url, headers=DEFAULT_HEADER, data=None):
        try:
            logging.debug("[GET] Fetching %s", url)
            response = self.open(url, headers=headers, data=data)
            html_parser = etree.HTMLParser()
            return etree.parse(response, html_parser)
        except Exception, e:
            raise Exception("Could not fetch %s (%s)" % (url, e))
        
    def get_url_qs(self, url):
        url_parts = urlsplit(url)
        return parse_qs(url_parts.query)
    
import re
from json import dumps
    
def get_last_archive_page():
    try:
        tree = BaseCrawler().parse("http://www.ed2000.com/archives.asp")
        last_page_href = ''.join(tree.xpath("//span[@class='PageInation']/a[1]/@href"))
        last_page_num = re.findall(r"\?PageIndex=(\d+)", last_page_href)[0]
        ret = {'ret': 0, 'data': {'last_page': last_page_num}}
    except Exception, e:
        ret = {'ret': -1, 'errmsg': str(e)}
    finally:
        return dumps(ret)
    
def fetch_list(lid):
    try:
        url = "http://www.ed2000.com/archives.asp?PageIndex=%s" % lid
        tree = BaseCrawler().parse(url)
        links = tree.xpath("//tr[@class='CommonListCell']//a[contains(@href, 'ShowFile.asp?FileID=')]/@href")
        id_list = [''.join(re.findall(r"ShowFile.asp\?FileID=(\d+)", link)) for link in links]
        logging.info(id_list)
        count = len(id_list)
        ret = {'ret': 0, 'data': {'id_list': id_list, 'count': count}}
    except Exception, e:
        ret = {'ret': -1, 'errmsg': str(e)}
    finally:
        return dumps(ret)
    
    
def fetch_page(pid):
    
    def parse_meta_info(tree):
        # page meta info
        title = ''.join(tree.xpath("(//tr[@class='CommonListTitle'])[1]//text()")).strip()
        catagory_list = tree.xpath("//div[@class='topmenu']/following-sibling::a[contains(@href,'FileList.asp?FileCategory=')]//text()")
        catagory_1, catagory_2 = catagory_list
        add_time = ''.join(tree.xpath("(//tr[@class='CommonListCell'])[2]/td[2]//text()")).strip()
        update_time = ''.join(tree.xpath("(//tr[@class='CommonListCell'])[4]/td[2]//text()")).strip()
        keywords = ''.join(tree.xpath("(//tr[@class='CommonListCell'])[5]/td[2]//text()")).strip()
        views = tree.xpath("(//table[@class='CommonListArea'])[1]//comment()")[0].text
        views = ''.join(re.findall(r'<td>([0-9a-fA-F]+)</td>', views))
        size_all = ''.join(tree.xpath("(//tr[@class='CommonListCell'])[3]/td[2]//text()")).strip()
        summary = etree.tostring(tree.xpath("//div[@class='PannelBody']")[0], with_comments=True, encoding='unicode', method='html')
        return {'title': title, 
                'catagory': catagory_1, 
                'subcatagory': catagory_2,
                'add_time': add_time, 
                'update_time': update_time,
                'keywords': keywords,
                'views': views,
                'size_all': size_all,
                'summary': summary}
        
    def parse_ed2k_addrs(tree):
        # parse ed2k addrs
        ed2k_list = []
        link_nodes = tree.xpath("//tr[@class='CommonListTitle']//div[contains(text(), 'eD2k')]/ancestor::table[@class='CommonListArea']//input[not(@class)]/ancestor::tr[@class='CommonListCell']")
        for link_node in link_nodes:
            link = ''.join(link_node.xpath(".//input/@value"))
            size = ''.join(link_node.xpath("./td[last()]/text()"))
            ed2k_list.append({'ed2k': link, 'size': size})
        return ed2k_list
    
    def parse_magnet(tree):
        code = ''.join(tree.xpath("//tr[@class='CommonListTitle']//div[contains(text(), 'Magnet')]/ancestor::table[@class='CommonListArea']//script//text()")).strip()
        if code:
            magnet = ','.join(re.findall("ShowMagnet\(\"(.+?)\"\);", code))
            return magnet
        else:
            return ""
        
    def fix_views(meta_info, ed2k_list=[], magnet=""):
        if ed2k_list:
            ed2k = ed2k_list[0]['ed2k']
            logging.info(ed2k)
            fhash = ''.join(re.findall("\|([0-9A-Fa-f]+?)\|h=", ed2k))
        elif magnet:
            fhash = ''.join(re.findall(r"urn:btih:([0-9a-fA-F]+?)&", magnet))
        else:
            fhash = ""
        
        if fhash:
            meta_info['views'] = meta_info['views'].replace(fhash, '')
        else:
            meta_info['views'] = '0'
    
    try: 
        url = "http://www.ed2000.com/ShowFile.asp?FileID=%s" % pid
        tree = BaseCrawler().parse(url)
        data = {}
        meta_info = parse_meta_info(tree)
        ed2k_list = parse_ed2k_addrs(tree)
        magnet = parse_magnet(tree)
        fix_views(meta_info, ed2k_list, magnet)
        data.update(meta_info)
        if ed2k_list: data['ed2k'] = ed2k_list
        if magnet: data['magnet'] = magnet
        ret = {'ret': 0, 'data': data}
    except Exception, e:
        ret = {'ret': -1, 'errmsg': str(e)}
    finally:
        return dumps(ret)
    

if __name__ == '__main__':
    pass