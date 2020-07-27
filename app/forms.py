import flask_wtf
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, validators
import json


class TransForm(FlaskForm):
    message = TextAreaField('HL7 message', [validators.InputRequired()])
    mapping = TextAreaField('Mapping scheme', [])
    message_out = TextAreaField('Transformed message')
