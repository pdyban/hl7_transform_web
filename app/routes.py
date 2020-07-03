from app import app
from app import forms
from flask import render_template
from flask import request
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
            print(type(message.hl7_message))
            mapping = HL7Mapping.from_string(form.mapping.data)
            transform = HL7Transform(mapping)
            message_out = transform.execute(message)
            print('OUTOUT', type(message_out.hl7_message))
            print('ININ', type(message))
            form.message_out.data = message.to_string()
        except APIError as e:
            alert.text = 'Could not read HL7 message. Please check your format.'
            alert.trace = e.args[0]
            alert.error_status = True
        # except (TypeError, IndexError) as e:
        #     alert.text = 'Could not read HL7 message. Please check your format.'
        #     alert.trace = str(e)
        #     alert.error_status = True
        except json.decoder.JSONDecodeError as e:
            alert.text = 'Could not read your mapping scheme. Please check if the JSON format is valid.'
            alert.trace = str(e)
            alert.error_status = True
    return render_template("home.html", form=form, alert=alert)

@app.route('/example')
def example():
    form = forms.TransForm()
    with open('app/data/example.hl7') as f:
        form.message.data = f.read().strip()
    with open('app/data/example.json') as f:
        form.mapping.data = f.read().strip()
    return render_template("home.html", form=form, alert=False)

@app.route('/about')
def about():
    return render_template("about.html")
