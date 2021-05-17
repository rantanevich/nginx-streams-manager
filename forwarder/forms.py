from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange, IPAddress, ValidationError

from forwarder.models import Rule


class RuleForm(FlaskForm):
    src_port = IntegerField('Source port', [DataRequired(),
                                            NumberRange(min=1, max=65535)])
    dst_ip = StringField('Destination IP', [DataRequired(),
                                            IPAddress()])
    dst_port = IntegerField('Destination port', [DataRequired(),
                                                 NumberRange(min=1, max=65535)])
    comment = StringField('Comment')
    action = HiddenField('Action')
    enabled = BooleanField('Enable rule')
    submit = SubmitField('Apply')

    def validate_src_port(form, field):
        rule = Rule.query.filter_by(src_port=field.data).first()
        action = form.action.data
        is_port_in_use = rule or Rule.is_port_in_use(field.data)
        if action != 'edit' and is_port_in_use:
            raise ValidationError(f'Port {field.data}/TCP is already in use')
