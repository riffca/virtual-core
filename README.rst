------------------------------------------------
A Data Science core based on Docker containers
------------------------------------------------

Here you can find a set of containers to help creating a data science core architecture, for example:

- LDAP server
- PostgreSQL server
- NFS server (Not active)
- Samba server (for integration with sequencer technology like Illumina)
- Galaxy server
- Zabbix server
- Software server (i.e. a lot of pre-installed software)
- Interative Compute server (a place for users to login)
- Exploratory Analysis server (JupyterHub with JupyterLab)
- SLURM grid configuration

There is a focus on bioinformatics, but the infrastructure can be used for
other applications.

Base images
-----------

We use Alpine Linux for simple servers (very small footprint)
and Ubuntu for larger images. It might happen that some containers
are derived from Debian ones.


Todo: script to create docker volume directory structure

Dependencies
------------

- Python 3.5+
- PyYAML
- Docker
- Ansible (including playbook)
- docker-py


**If you use the setup wizard**

- Flask
- openssl and pyOpenSSL (if you need to generate keys)

(explain with conda)


Installation
------------




This will install all your servers on the local machine. If you have a very large
big-iron machine, this might be what you want. If you have a cluster, this is still
a reasonable starting point, though you will have some work to do, especially
on the security front.

1. Use the wizard to configure the most complicated stuff:
``PYTHONPATH=. python -m wizard``

2. Create a directory that will store all your docker volumes. This might need to be
very big.

3. ``python3 src/prepare_templates.py [Directory_Above]`` . Prepares the ansible
templates (this probably can be put inside ansible).

4. Optional and **not recommended**: ``python3 src/use_examples.py`` . This will copy the example configuration files
to be used as the default ones. Make sure to change things in your final configuaration. **You only run this if you did not run step 1, the wizard. Suggestion: run the wizard.**

4. ``python3 src/create_directory_structure.py [Directory_Above]``


5. ``cp etc/host.sample etc/hosts``

6. ``cd ansible; ansible-playbook --ask-pass -i ../etc/hosts main.yml``

Acknowledgements
----------------

The sequencer Samba file configuration was originally inspired on David Personette's `Samba container`_.
It is currently completely different.

The current Galaxy configuration is based on Björn Grüning's `Galaxy container`_.


Author and License
------------------

Copyright by Tiago Antao. Licensed under GNU Affero General Public License
version 3.


.. _Samba container: https://github.com/dperson/samba

.. _Galaxy container: https://github.com/bgruening/docker-galaxy-stable
