# -*- coding: utf-8 -*-
'''
.. module:: wizard.__main__
   :synopsis: A Web based wizard to setup the core, entry point
   :noindex:
   :copyright: Copyright 2016 by Tiago Antao
   :license: GNU Affero, see LICENSE for details

.. moduleauthor:: Tiago Antao <tra@popgen.net>

'''
import os
import socket

from flask import Flask, render_template, redirect, request, url_for

import wizard
from wizard import ca

app = Flask(__name__)

_ca_template = '''
[ req ]
default_bits           = 2048
distinguished_name     = req_distinguished_name
attributes             = req_attributes
prompt                 = no

[ req_distinguished_name ]
countryName            = {country}
stateOrProvinceName    = {state}
localityName           = {locality}
organizationName       = {orgname}
organizationalUnitName = {orgunit}
commonName             = {commonname}
emailAddress           = {email}

[ req_attributes ]
'''


def _delist(form, exceptions=[]):
    delist = {}
    for k, v in form.items():
        if type(v) == list and k not in exceptions:
            delist[k] = v[0]
        else:
            delist[k] = v
    return delist


def _has_all_parameters(form, parameters):
    for parameter in parameters:
        if parameter in form:
            if form[parameter] == '':
                return False
        else:
            return False
    return True


@app.route('/', methods=['GET'])
@app.route('/<int:run>', methods=['GET', 'POST'])
def welcome(run=0):
    if run == 0:
        form = wizard.config.get('General', {})
    else:
        form = _delist(request.form)
        if _has_all_parameters(form, ['host', 'country', 'state', 'locality',
                                      'orgname', 'orgunit', 'commonname',
                                      'email']):
            wizard.change_config('General', **form)
            return redirect(url_for('determine_ssh_status', run=0))
    if 'host' not in form:
        form['host'] = socket.getfqdn()
    all_params = {'run': run, **form}
    return render_template('welcome.html', **all_params)


@app.route('/sshkey/<int:run>')
def determine_ssh_status(run=0):
    if not os.path.exists('etc/ssh'):
        os.mkdir('etc/ssh')
    if not os.path.exists('etc/ssh/authorized_keys'):
        return render_template('need_ssh.html', run=run)
    else:
        return redirect(url_for('explain_certificate_authority', run=0))


@app.route('/ca/<int:run>')
def explain_certificate_authority(run=0):
    # TODO: this needs to be changed
    if not os.path.exists('etc/ca'):
        os.mkdir('etc/ca')
    if not os.path.exists('etc/ca/UNDERSTAND') and \
            not os.path.exists('etc/ca/demoCA'):
        return render_template('need_ca.html', run=run)
    else:
        return redirect(url_for('get_named_directories_root'))


@app.route('/create_ca')
def create_certificate_authority(run=0):
    if os.path.exists('etc/ca/demoCA'):
        return render_template('exists_ca.html',
                               next_route='/named_directories')
    ca_template = _ca_template.format(
        country=wizard.config['General']['country'],
        state=wizard.config['General']['state'],
        locality=wizard.config['General']['locality'],
        orgname=wizard.config['General']['orgname'],
        orgunit=wizard.config['General']['orgunit'],
        commonname=wizard.config['General']['commonname'],
        email=wizard.config['General']['email'])
    with open('init.ssl', 'wt') as w:
        w.write(ca_template)
    ca_ok = ca.create_ca()
    if ca_ok:
        return redirect(url_for('get_named_directories_root'))
    return render_template('ca_not_created.html')


@app.route('/named_directories', methods=['GET', 'POST'])
def get_named_directories_root():
    form = _delist(request.form)
    if 'named' in form:
        root = form['named']
    else:
        root = wizard.config['General'].get('nameddirectoriesroot', None)
    if root is None or not os.path.isdir(root):
        return render_template('named_directories.html', root=root)
    wizard.change_config('General', nameddirectoriesroot=root)
    return redirect(url_for('choose_containers'))


@app.route('/choose', methods=['GET', 'POST'])
def choose_containers():
    if len(request.form) > 0:
        active_containers = []
        for entry in request.form:
            active_containers.append(entry)
        wizard.change_config('General', containers=active_containers)
        return redirect(url_for('configure_containers'))
    active_containers = wizard.config['General'].get('containers', ['ldap'])
    return render_template('choose_containers.html',
                           descriptive_names=wizard.descriptive_names,
                           dependencies=wizard.dependencies,
                           container_role=wizard.container_role,
                           active_containers=active_containers,
                           container_order=wizard.container_order)


def _render_configure_template(template, container, **kwargs):
    complete_configuration = [
        container for container in wizard.container_order
        if wizard.is_configuration_complete(container)]
    if container is not None:
        samples = wizard.get_configuration_file_samples(container)
        print(wizard.requirements[container])
        requirements = [(req, wizard.descriptive_requirements[req])
                        for req in wizard.requirements[container]
                        if 'ca' not in req]  # CA is hard-coded, maybe add needs_input to YAML
        complete_samples = [
            file_name for file_name in samples
            if wizard.is_file_configured(container, file_name)]
    else:
        samples = None
        complete_samples = None
    return render_template(template,
                           current_container=container,
                           samples=samples,
                           complete_samples=complete_samples,
                           security=requirements,
                           complete_requirements=[],
                           complete_configuration=complete_configuration,
                           containers=wizard.container_order,
                           **kwargs)


@app.route('/configure')
@app.route('/configure/<string:container>')
def configure_containers(container=None):
    return _render_configure_template('configure_containers.html', container)


@app.route('/configure_file/<string:container>/<path:file_name>')
def configure_container_file(container, file_name):
    final_file = file_name[:-7]
    if os.path.exists(final_file):
        warn = 'File Already exists, editing'
        load_name = final_file
    else:
        warn = 'Using sample file'
        load_name = file_name
    with open(load_name) as f:
        file_contents = f.read()
    return _render_configure_template('configure_container_file.html',
                                      container,
                                      file_name=file_name,
                                      file_contents=file_contents,
                                      warn=warn)


@app.route('/process_file', methods=['POST'])
def process_file():
    container = request.form['container']
    file_name = request.form['file_name']
    file_contents = request.form['file_contents']
    final_file = file_name[:-7]
    operation = request.form['operation']
    if operation == 'save':
        with open(final_file, 'wt') as w:
            w.write(file_contents)
        warn = 'File Saved'
    elif operation == 'reload':
        warn = 'Sample reloaded'
        with open(file_name) as f:
            file_contents = f.read()
    else:
        warn = 'Unknown operation'
    return _render_configure_template('configure_container_file.html',
                                      container,
                                      file_name=file_name,
                                      file_contents=file_contents,
                                      warn=warn)


if __name__ == "__main__":
    app.debug = True
    app.run()
