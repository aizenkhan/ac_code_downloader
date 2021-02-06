""" Contains utilities related to web requests """
import requests
from bs4 import BeautifulSoup as soup
from bs4.builder import HTMLParserTreeBuilder
from contextlib import contextmanager


custom_builder = HTMLParserTreeBuilder()
custom_builder.cdata_list_attributes["*"].remove("class")


def http_get(session, url, headers=None, verify=False):
    res = session.get(url, headers=headers, verify=verify)
    return res


def http_post(session, url, payload, headers=None):
    res = session.post(url, data=payload, headers=headers)
    return res


def parse(html):
    content = soup(html, "html.parser", builder=custom_builder)
    return content


@contextmanager
def managed_session():
    try:
        session = requests.session()
        yield session
    finally:
        session.close()
