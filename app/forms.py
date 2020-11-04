from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators


class TransForm(FlaskForm):
    message = TextAreaField('HL7 message', [validators.InputRequired()])
    mapping = TextAreaField('Mapping scheme', [])
    message_out = TextAreaField('Transformed message')
