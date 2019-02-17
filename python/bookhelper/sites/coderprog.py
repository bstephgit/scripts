#!/usr/bin/env python3

from lxml import html, etree
import re
from bookhelper import FormatException, ElementNames


def extract_data(content):
    children = html.fromstring(content).xpath('.//div[@class="thecontent"]/child::*')
    title = ''
    author = ''
    year=''
    node = children[2]
    str = node.xpath('b/text()')
    if not str:
        msg = 'Error retrieving title/author in [%s]' % etree.tostring(node)
        raise FormatException(msg)
    str = str[0]
    regexp = re.compile(r'(.+) by (.+)')
    res = regexp.search(str)
    try:
        if res and len(res.groups()) == 2:
            title, author = res.groups()
            print(res.groups())
            print('Successfully got title/author title=[%s], author=[%s]' % (title, author))
        else:
            raise FormatException('Error retrieving title/author from string %s' % str)
    except FormatException:
        print('Error extracting from %s. String cannot be split to Title/Author. Assign to title.' % str)
        title=str

    str = node.xpath('text()')

    try:
        if not str:
            msg = 'Error retrieving year in [%s]' % str
            raise FormatException(msg)
    except FormatException:
        print('Error extracting year and description. Left year and description unassigned')

    str = str[0] if len(str[0]) > 4 else str[1]
    regexp = re.compile(r'.+\s+\|\s+(19[0-9]{2}|20[0,1][0-9])\s+\|')
    res = regexp.search(str)

    try:
        if not res:
            raise FormatException('Date not found in \'%s\'' % str)
        year = res.groups()[0]
        print('Date successfully retrieved %s' % year)
    except FormatException:
        print('Cannot extract date. Left unassingned.')

    descr = ''
    children = children[3:]
    for child in children:
        if child.tag == 'div':
            break
        descr += etree.tostring(child, encoding='UTF-8').replace(b'\n', b'').decode('utf-8')

    # print('description=%s',descr)

    return {ElementNames.TITLE: title.strip(), ElementNames.AUTHOR: author.strip(), ElementNames.YEAR: year, \
                ElementNames.DESCRIPTION: descr}
