from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, IPAddress, ValidationError

from forwarder.models import Rule


class RuleForm(FlaskForm):
    src_port = IntegerField('Source port', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    dst_ip = StringField('Destination IP', validators=[DataRequired(), IPAddress()])
    dst_port = IntegerField('Destination port', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    comment = StringField('Comment')
    submit = SubmitField('Apply')

    def validate_src_port(form, field):
        rule = Rule.query.filter_by(src_port=field.data).first()
        if rule or Rule.is_port_in_use(field.data):
            raise ValidationError(f'Port {field.data}/TCP is already in use')
