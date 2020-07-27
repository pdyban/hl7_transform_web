import pytest
import os
import sys
sys.path.append(os.path.abspath('.'))
print(sys.path)
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
from app import app


@pytest.fixture
def client():
     # start Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    #options.binary = os.path.join(os.path.abspath('.'), 'chromedriver')
    browser = webdriver.Chrome(os.path.join(os.path.abspath('.'), 'chromedriver'), options=options)
    browser.set_window_size(1280, 1024)
    browser.set_page_load_timeout(30)

    app.config['TESTING'] = True
    with app.test_client() as app_client:
        with app.app_context():
            # e.g. app.init_db()
            pass
        yield browser

    browser.close()

def test_navbar(client):
    client.get('http://localhost:8000/')
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
    client.get('http://localhost:8000/')
    assert 'HL7 Transform Web UI' == client.title
    message_field = client.find_element_by_id('message_in')
    assert message_field is not None
    print(dir(message_field))
    assert message_field.text == ''
    message_field.send_keys('Hello world')
    message_field.submit()

def test_about(client):
    client.get('http://localhost:8000/about')
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
    client.get('http://localhost:8000/examples')
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

def test_can_add_new_rule(client):
    client.get('http://localhost:8000')
    # create a new rule and verify that it was created
    len0 = len(client.find_elements_by_xpath('//ul[@id="rule-list"]/li'))
    new_rule_button = client.find_element_by_id('newRuleButton')
    new_rule_button.click()
    link = client.find_element_by_xpath('//a[@class="dropdown-item"][text()="set_value"]')
    assert link is not None
    link.click()
    rules = client.find_elements_by_xpath('//ul[@id="rule-list"]/li')
    assert len(rules) == len0 + 1
    div = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div[@name="rule-name"]')
    assert div.text == 'set_value'
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-target-field"]')
    target_field.send_keys('SCH.12')
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-value"]')
    target_field.send_keys('Some value')

    # switch to advanced view and verify JSON formatted mapping scheme
    client.find_element_by_id('advanced-tab').click()
    textarea = client.find_element_by_xpath('//textarea[@id="mapping_scheme"]')
    text = textarea.get_attribute("value")
    assert len(text) > 3
    assert '"operation": "set_value",' in text
    assert '"target_field": "SCH.12",' in text
    assert '"args": {' in text
    assert '"value": "Some value"' in text
    assert '}' in text

    # switch back to quick view and verify data consistency
    client.find_element_by_id('quick-tab').click()
    div = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div[@name="rule-name"]')
    assert div.text == 'set_value'
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-target-field"]')
    assert target_field.get_attribute('value') == 'SCH.12'
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-value"]')
    assert target_field.get_attribute('value') == 'Some value'

def test_can_switch_to_quick_view(client):
    client.get('http://localhost:8000')

    ops = [{"operation":"copy_value","target_field":"MSH.9.1","source_field":"MSH.9.2"},{"operation":"set_value","target_field":"MSH.9.3","args":{"value":"SIU_S12"}}]

    # given a JSON-formatted scheme, switch to quick view
    client.find_element_by_id('advanced-tab').click()
    # textarea = client.find_element_by_xpath('//textarea[@id="mapping_scheme"]')
    client.save_screenshot('screenshot.png')
    textarea = WebDriverWait(client, 10).until(EC.element_to_be_clickable((By.XPATH, '//textarea[@id="mapping_scheme"]')))
    # textarea.click()
    client.execute_script("arguments[0].click();", textarea)
    textarea.clear()
    textarea.send_keys(json.dumps(ops))

    # switch to quick view and verify list of rules
    client.find_element_by_id('quick-tab').click()
    for index, op in enumerate(ops):
        div = client.find_elements_by_xpath('//ul[@id="rule-list"]/li/div[@name="rule-name"]')
        assert div[index].text == op['operation']
        target_field = client.find_elements_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-target-field"]')
        assert target_field[index].get_attribute('value') == op['target_field']

    # switch back to advanced view and compare JSON
    client.find_element_by_id('advanced-tab').click()
    textarea = client.find_element_by_xpath('//textarea[@id="mapping_scheme"]')
    text = textarea.get_attribute("value")
    assert json.loads(text) == ops

def test_example_orm(client):
    client.get('http://localhost:8000/examples/create_orm_o01_message')
    assert 'HL7 Transform Web UI' == client.title
    message_field = client.find_element_by_id('message_in')
    assert message_field.text == r'MSH|^~\&'
    rule_list = client.find_elements_by_xpath('//ul[@id="rule-list"]/li')
    assert len(rule_list) == 34
    transform_btn = client.find_element_by_name('transform-btn')
    transform_btn.click()
    # client.find_element_by_id('advanced-tab').click()
    message_field = client.find_element_by_id('message_out')
    assert r'MSH|^~\&|||||202006171230||ORM^O01|' in message_field.text
    assert r'PV1||U||||||||MY_HOSPITAL_UNIT_EXTID|||||||||' in message_field.text
    assert r'||MY_VISIT_MOTIVE_EXTID^MY_VISIT_MOTIVE_TEXT^MY_HOSPITAL_UNIT_EXTID|Low|20200507172300|||||||RELEVANT_CLINICAL_INFO|||^ORDERING_PROVIDER_FAMILY_NAME|||||||||||^^^20200507172300^20200507172330^Low|||TRANSPORTATION_MODE|REASON_FOR_STUDY' in message_field.text

def test_workflow(client):
    client.get('http://localhost:8000/')

    # enter message
    message_field = client.find_element_by_id('message_in')
    message_field.click()
    message_field.send_keys(r'MSH|^~\&')

    # create mappings cheme in quick view
    client.find_element_by_id('newRuleButton').click()
    client.find_element_by_xpath('//a[@class="dropdown-item"][text()="set_value"]').click()
    rules = client.find_elements_by_xpath('//ul[@id="rule-list"]/li')
    assert len(rules) == 1
    #div = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div[@name="rule-name"]')
    #assert div.text == 'set_value'
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-target-field"]')
    target_field.send_keys('MSH.5')
    target_field = client.find_element_by_xpath('//ul[@id="rule-list"]/li/div/input[@name="rule-value"]')
    target_field.send_keys('Sender')

    # compute transformed message
    client.find_element_by_name('transform-btn').click()

    # verify message_out
    message_field = client.find_element_by_id('message_out')
    assert message_field.text == r'MSH|^~\&|||Sender'

def test_empty_workflow(client):
    client.get('http://localhost:8000/')

    # enter message
    message_field = client.find_element_by_id('message_in')
    message_field.click()
    message_field.send_keys(r'MSH|^~\&')

    # compute message transformed with an empty scheme
    client.find_element_by_name('transform-btn').click()

    # verify message_out
    message_field = client.find_element_by_id('message_out')
    assert message_field.text == r'MSH|^~\&'
