========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/apmec-horizon.svg
          :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on


Apmec Horizon UI
=================

Horizon UI for Apmec MEA Manager

Installation
============

1. Install module

  ::

    sudo python setup.py install


2. Copy files to Horizon tree

  ::

    cp apmec_horizon/enabled/* /opt/stack/horizon/openstack_dashboard/enabled/


3. Restart the apache webserver

  ::

    sudo service apache2 restart


More Information
================

Apmec Wiki:
https://wiki.openstack.org/wiki/Apmec
