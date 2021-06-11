from ipaddress import IPv4Address, IPv4Network

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    BooleanField,
    SelectField,
    HiddenField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    IPAddress,
    ValidationError
)

from manager.models import Stream, RouteTable, NetworkInterfaces


class StreamForm(FlaskForm):
    src_port = IntegerField('Source port', [DataRequired(),
                                            NumberRange(min=1, max=65535)])
    dst_ip = StringField('Destination IP', [DataRequired(),
                                            IPAddress()])
    dst_port = IntegerField('Destination port', [DataRequired(),
                                                 NumberRange(min=1, max=65535)])
    comment = StringField('Comment')
    action = HiddenField('Action')
    enabled = BooleanField('Enable rule', default=True)
    submit = SubmitField('Apply')

    def validate_src_port(form, field):
        rule = Stream.query.filter_by(src_port=field.data).first()
        action = form.action.data
        is_port_in_use = rule or Stream.is_port_in_use(field.data)
        if action != 'edit' and is_port_in_use:
            raise ValidationError(f'Port {field.data}/TCP is already in use')


class RouteTableForm(FlaskForm):
    dst = StringField('Destination', validators=[DataRequired()])
    gateway = StringField('Gateway', validators=[DataRequired(), IPAddress()])
    submit = SubmitField('Apply')

    def validate_dst(form, field):
        try:
            if '/' not in field.data and IPv4Network(field.data):
                raise ValidationError('Subnet prefix isn\'t specified')

            if RouteTable.route_exists(field.data):
                raise ValidationError('Destination already exists')
        except ValueError as err:
            raise ValidationError(err)

    def validate_gateway(form, field):
        gateway = IPv4Address(field.data)

        if not any(gateway in IPv4Network(f'{network.dst}/{network.prefix}')
                   for network in RouteTable.onlink_routes()):
            raise ValidationError('Network is unreachable')


class NetworkInterfacesForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    ifname = SelectField('Interface', validators=[DataRequired()])
    submit = SubmitField('Apply')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.ifname.choices = NetworkInterfaces.interfaces()

    def validate_address(form, field):
        try:
            if '/' not in field.data and IPv4Network(field.data):
                raise ValidationError('Subnet prefix isn\'t specified')

            if NetworkInterfaces.address_exists(field.data):
                raise ValidationError('Address already exists')
        except ValueError as err:
            raise ValidationError(err)
