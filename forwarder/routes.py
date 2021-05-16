from flask import render_template, redirect, flash, url_for

from forwarder import app, db
from forwarder.models import Rule
from forwarder.forms import RuleForm


@app.route('/')
def index():
    rules = Rule.query.all()
    return render_template('index.html', rules=rules)


@app.route('/rule', methods=['GET', 'POST'])
def new_rule():
    form = RuleForm()
    if form.validate_on_submit():
        rule = Rule(src_port=form.src_port.data,
                    dst_ip=form.dst_ip.data,
                    dst_port=form.dst_port.data,
                    comment=form.comment.data)
        db.session.add(rule)
        db.session.commit()
        Rule.apply_rules()
        flash(f'Added rule: "{rule}"', 'success')
        return redirect(url_for('index'))
    return render_template('rule.html', form=form)


@app.route('/rule/<int:rule_id>/delete')
def delete_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    Rule.apply_rules()
    flash(f'Deleted rule: "{rule}"', 'success')
    return redirect(url_for('index'))
