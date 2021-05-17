from flask import render_template, redirect, flash, url_for

from forwarder import app, db
from forwarder.models import Rule
from forwarder.forms import RuleForm


@app.route('/')
def index():
    rules = Rule.query.all()
    return render_template('index.html', rules=rules, title='Main')


@app.route('/rule', methods=['GET', 'POST'])
def new_rule():
    form = RuleForm()
    if form.validate_on_submit():
        rule = Rule(src_port=form.src_port.data,
                    dst_ip=form.dst_ip.data,
                    dst_port=form.dst_port.data,
                    comment=form.comment.data,
                    enabled=form.enabled.data)
        db.session.add(rule)
        db.session.commit()
        if Rule.apply_rules():
            flash(f'Rule "{rule}" has been added', 'success')
        else:
            flash(f'Rule: "{rule}" hasn\'t been added', 'danger')
        return redirect(url_for('index'))
    return render_template('rule.html', form=form, title='New')


@app.route('/rule/<int:rule_id>/edit', methods=['GET', 'POST'])
def edit_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    form = RuleForm(action='edit')
    if form.validate_on_submit():
        rule.src_port = form.src_port.data
        rule.dst_ip = form.dst_ip.data
        rule.dst_port = form.dst_port.data
        rule.comment = form.comment.data
        rule.enabled = form.enabled.data
        db.session.commit()
        if Rule.apply_rules():
            flash(f'Rule "{rule}" has been updated', 'success')
        else:
            flash(f'Rule: "{rule}" hasn\'t been updated', 'danger')
        return redirect(url_for('index'))
    form.src_port.data = rule.src_port
    form.dst_ip.data = rule.dst_ip
    form.dst_port.data = rule.dst_port
    form.comment.data = rule.comment
    form.enabled.data = rule.enabled
    return render_template('rule.html', form=form, title='Edit')


@app.route('/rule/<int:rule_id>/delete')
def delete_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    if Rule.apply_rules():
        flash(f'Rule "{rule}" has been deleted', 'success')
    else:
        flash(f'Rule "{rule}" hasn\'t been deleted', 'danger')
    return redirect(url_for('index'))
