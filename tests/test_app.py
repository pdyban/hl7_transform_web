import pytest
import os
import sys
sys.path.append(os.path.abspath('.'))
print(sys.path)

from selenium import webdriver
import threading
from app import app


@pytest.fixture
def client():
     # start Chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    #options.binary = os.path.join(os.path.abspath('.'), 'chromedriver')
    browser = webdriver.Chrome(os.path.join(os.path.abspath('.'), 'chromedriver'), options=options)
    browser.set_page_load_timeout(30)

    app.config['TESTING'] = True
    with app.test_client() as app_client:
        with app.app_context():
            # e.g. app.init_db()
            pass
         # start the Flask server in a thread
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        yield browser

    browser.close()

def test_navbar(client):
    client.get('localhost:5000/')
    navbar = client.find_element_by_id('navbarCollapse')
    assert navbar is not None
    options = navbar.find_elements_by_tag_name('li')
    hrefs = []
    for option in options:
        link = option.find_element_by_tag_name('a')
        href = str(link.get_attribute('href'))
        hrefs.append(href)
    for href in hrefs:
        client.get(href)
        assert 'HL7 Transform Web UI' == client.title

def test_index(client):
    client.get('localhost:5000/')
    assert 'HL7 Transform Web UI' == client.title
    message_field = client.find_element_by_id('message_in')
    assert message_field is not None
    print(dir(message_field))
    assert message_field.text == ''
    message_field.send_keys('Hello world')
    message_field.submit()

def test_about(client):
    client.get('localhost:5000/about')
    assert 'HL7 Transform Web UI' == client.title
    header_field = client.find_element_by_tag_name('h1')
    print(header_field)
    assert header_field is not None
    assert 'HL7 Transform' == header_field.text

    lead_field = client.find_element_by_class_name('lead')
    assert lead_field is not None
    assert 'A web tool that allows to transform HL7 messages using a mapping scheme' == lead_field.text

    text_field = client.find_element_by_id('description')
    assert text_field is not None
    assert 'developed at Doctolib' in text_field.text

def test_examples(client):
    client.get('localhost:5000/examples')
    assert 'HL7 Transform Web UI' == client.title
    example_list = client.find_element_by_id('example_list')
    assert example_list is not None

    hrefs = []
    for example_item in example_list.find_elements_by_tag_name('li'):
        link = example_item.find_element_by_tag_name('a')
        href = str(link.get_attribute('href'))
        hrefs.append(href)
    for href in hrefs:
        client.get(href)
        assert 'HL7 Transform Web UI' == client.title
