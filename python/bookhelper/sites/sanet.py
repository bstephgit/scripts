#!/usr/bin/env python3

from lxml import html, etree
import re
from bookhelper import FormatException, ElementNames


def extract_data(content):
    children = html.fromstring(content).xpath('.//section[@class="descr"]/child::*')
    title = html.fromstring(content).xpath('.//h1[@class="item_title"]/span/text()')[0].strip()
    author = ''
    year= html.fromstring(content).xpath('//div[@class="release-info"]/text()')[0].split('|')[1].strip()
    #str = node.xpath('b/text()')
    if not title or len(title)==0:
        msg = 'Error retrieving title'
        raise FormatException(msg)
    else:
        print('Successfully got title [%s]' % (title,))

    if not year or len(year) == 0:
        msg = 'Error retrieving year in [%s]' % str
        raise FormatException(msg)
    else:
        regexp = re.compile(r'^19[0-9]{2}|20[0,1][0-9]$')
        res = regexp.search(year)
        if not res:
            raise FormatException('Date not found in \'%s\'' % year)
        print('Date successfully retrieved %s' % year)

    descr = ''
    children = children[3:]
    for child in children:
        if child.tag == 'div':
            break
        descr += etree.tostring(child, encoding='UTF-8').replace(b'\n', b'').decode('utf-8')

    #print('description=%s',descr)

    return {ElementNames.TITLE: title.strip(), ElementNames.AUTHOR: author.strip(), ElementNames.YEAR: year, \
                ElementNames.DESCRIPTION: descr}
