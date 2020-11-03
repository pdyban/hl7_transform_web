from app import app
from app import forms
from flask import render_template, abort
from collections import namedtuple
import os
from hl7_transform.mapping import HL7Mapping
from hl7_transform.transform import HL7Transform
from hl7_transform.message import HL7Message
from hl7_transform.core import APIError
import json


class FormError:
    def __init__(self, text='', trace=''):
        self.text = text
        self.trace = trace
        self.error_status = False


@app.route("/", methods=('GET', 'POST',))
def home():
    form = forms.TransForm()
    alert = FormError()
    if form.validate_on_submit():
        try:
            message = HL7Message.from_string(form.message.data)
            mapping = HL7Mapping.from_string(form.mapping.data)
            transform = HL7Transform(mapping)
            transform(message)
            form.message_out.data = message.to_string()
        except APIError as e:
            alert.text = 'Could not read HL7 message. Please check your format.'
            alert.trace = e.args[0]
            alert.error_status = True
        except json.decoder.JSONDecodeError as e:
            alert.text = 'Could not read your mapping scheme. Please check if the JSON format is valid.'
            alert.trace = str(e)
            alert.error_status = True
        except (IndexError, KeyError, RuntimeError) as e:
            alert.text = 'Error occurred during processing.'
            alert.trace = str(e)
            alert.error_status = True
    return render_template("home.html", form=form, alert=alert)


@app.route('/examples')
def example():
    ExampleItem = namedtuple('ExampleItem', ['name', 'path'])
    items = []
    example_dir = 'app/data/examples'
    for example_item in os.listdir(example_dir):
        try:
            with open(os.path.join(example_dir, example_item, 'description.txt')) as f:
                name = f.read()
                items.append(ExampleItem(name=name,
                             path=f'/examples/{example_item}'))
        except FileNotFoundError as e:
            print(e)
            continue
    return render_template("examples.html", items=items)


@app.route('/examples/<path:example_name>')
def example_page(example_name):
    if not os.path.exists(f'app/data/examples/{example_name}'):
        return abort(404)
    alert = FormError()
    form = forms.TransForm()
    with open(f'app/data/examples/{example_name}/message.hl7') as f:
        form.message.data = f.read().strip()
    with open(f'app/data/examples/{example_name}/mapping.json') as f:
        form.mapping.data = f.read().strip()
    return render_template("home.html", form=form, alert=alert)


@app.route('/about')
def about():
    return render_template("about.html")
