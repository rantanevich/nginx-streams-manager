from socket import gethostname

from flask import (
    flash,
    url_for,
    request,
    redirect,
    render_template
)

from manager import app, db
from manager.models import Stream, RouteTable, NetworkInterfaces
from manager.forms import StreamForm, RouteTableForm, NetworkInterfacesForm
from manager.structures import Route, Address


@app.get('/')
def index():
    return render_template('index.html',
                           title=f'{gethostname()} | Main',
                           hostname=gethostname(),
                           streams=Stream.query.all(),
                           routes=RouteTable.static_routes(),
                           addresses=NetworkInterfaces.addresses())


@app.get('/streams')
def streams():
    return render_template('streams.html',
                           hostname=gethostname(),
                           title=f'{gethostname()} | Port Forwarding',
                           streams=Stream.query.all())


@app.get('/stream')
@app.post('/stream')
def new_rule():
    form = StreamForm()
    if form.validate_on_submit():
        stream = Stream(src_port=form.src_port.data,
                        dst_ip=form.dst_ip.data,
                        dst_port=form.dst_port.data,
                        comment=form.comment.data,
                        enabled=form.enabled.data)
        db.session.add(stream)
        db.session.commit()
        if Stream.apply_rules():
            flash(f'Rule "{stream}" has been added', 'success')
        else:
            flash(f'Rule: "{stream}" hasn\'t been added', 'danger')
        return redirect(url_for('streams'))
    return render_template('stream.html',
                           hostname=gethostname(),
                           title=f'{gethostname()} | Port Forwarding - New',
                           form=form)

@app.get('/stream/<int:stream_id>/edit')
@app.post('/stream/<int:stream_id>/edit')
def edit_rule(stream_id):
    stream = Stream.query.get_or_404(stream_id)
    form = StreamForm(action='edit', obj=stream)
    if form.validate_on_submit():
        stream.update(**form.data)
        db.session.commit()
        if Stream.apply_rules():
            flash(f'Rule "{stream}" has been updated', 'success')
        else:
            flash(f'Rule: "{stream}" hasn\'t been updated', 'danger')
        return redirect(url_for('streams'))
    return render_template('stream.html',
                           hostname=gethostname(),
                           title=f'{gethostname()} | Port Forwarding - Edit',
                           form=form)


@app.get('/stream/<int:stream_id>/delete')
def delete_rule(stream_id):
    stream = Stream.query.get_or_404(stream_id)
    db.session.delete(stream)
    db.session.commit()
    if Stream.apply_rules():
        flash(f'Rule "{stream}" has been deleted', 'success')
    else:
        flash(f'Rule "{stream}" hasn\'t been deleted', 'danger')
    return redirect(url_for('streams'))


@app.get('/routes')
@app.post('/routes')
def routes():
    form = RouteTableForm()
    if form.validate_on_submit():
        dst, prefix = form.dst.data.split('/')
        route = Route(dst=dst,
                      prefix=int(prefix),
                      gateway=form.gateway.data)
        RouteTable.add_route(route)
        flash(f'Route "{route}" has been added', 'success')
        return redirect(url_for('routes'))
    return render_template('routes.html',
                           title=f'{gethostname()} | Static Routes',
                           hostname=gethostname(),
                           form=form,
                           routes=RouteTable.static_routes(),
                           networks=RouteTable.onlink_routes())


@app.get('/routes/delete')
def route_delete():
    route = Route(dst=request.args.get('dst'),
                  prefix=int(request.args.get('prefix')),
                  gateway=request.args.get('gateway'),
                  ifindex=int(request.args.get('ifindex')),
                  ifname=request.args.get('ifname'))
    flash(f'Route "{route}" has been deleted', 'success')
    RouteTable.delete_route(route)
    return redirect(url_for('routes'))


@app.get('/addresses')
@app.post('/addresses')
def addresses():
    form = NetworkInterfacesForm()
    if form.validate_on_submit():
        ip, prefix = form.address.data.split('/')
        address = Address(ip=ip,
                          prefix=int(prefix),
                          ifname=form.ifname.data)
        NetworkInterfaces.add_address(address)
        flash(f'Address "{address}" has been added', 'success')
        return redirect(url_for('addresses'))
    return render_template('addresses.html',
                           title=f'{gethostname()} | Addresses',
                           hostname=gethostname(),
                           form=form,
                           addresses=NetworkInterfaces.addresses())


@app.get('/addresses/delete')
def address_delete():
    address = Address(ip=request.args.get('ip'),
                      prefix=int(request.args.get('prefix')),
                      ifindex=int(request.args.get('ifindex')),
                      ifname=request.args.get('ifname'))
    NetworkInterfaces.delete_address(address)
    flash(f'Address "{address}" has been deleted', 'success')
    return redirect(url_for('addresses'))
