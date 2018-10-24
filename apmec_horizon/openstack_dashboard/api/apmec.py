# Copyright 2015 Brocade Communications System, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import

from apmecclient.v1_0 import client as apmec_client
from django.conf import settings
from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api import base
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


@memoized
def apmecclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    c = apmec_client.Client(
        token=request.user.token.id,
        auth_url=base.url_for(request, 'identity'),
        endpoint_url=base.url_for(request, 'mec-orchestration'),
        insecure=insecure, ca_cert=cacert)
    return c


def mea_list(request, **params):
    LOG.debug("mea_list(): params=%s", params)
    meas = apmecclient(request).list_meas(**params).get('meas')
    return meas


def mead_list(request, **params):
    LOG.debug("mead_list(): params=%s", params)
    meads = apmecclient(request).list_meads(**params).get('meads')
    return meads


def create_mead(request, tosca_body=None, **params):
    LOG.debug("create_mead(): params=%s", params)
    mead_instance = apmecclient(request).create_mead(body=tosca_body)
    return mead_instance


def create_mea(request, mea_arg, **params):
    LOG.debug("create_mea(): mea_arg=%s", str(mea_arg))
    mea_instance = apmecclient(request).create_mea(body=mea_arg)
    return mea_instance


def get_mead(request, mead_id):
    LOG.debug("mead_get(): mead_id=%s", str(mead_id))
    mead = apmecclient(request).show_mead(mead_id)
    return mead


def get_mea(request, mea_id):
    LOG.debug("mea_get(): mea_id=%s", str(mea_id))
    mea_instance = apmecclient(request).show_mea(mea_id)
    return mea_instance


def delete_mea(request, mea_id):
    LOG.debug("delete_mea():mea_id=%s", str(mea_id))
    apmecclient(request).delete_mea(mea_id)


def delete_mead(request, mead_id):
    LOG.debug("delete_mead():mead_id=%s", str(mead_id))
    apmecclient(request).delete_mead(mead_id)


def create_vim(request, vim_arg):
    LOG.debug("create_vim(): vim_arg=%s", str(vim_arg))
    vim_instance = apmecclient(request).create_vim(body=vim_arg)
    return vim_instance


def get_vim(request, vim_id):
    LOG.debug("vim_get(): vim_id=%s", str(vim_id))
    vim_instance = apmecclient(request).show_vim(vim_id)
    return vim_instance


def delete_vim(request, vim_id):
    LOG.debug("delete_vim():vim_id=%s", str(vim_id))
    apmecclient(request).delete_vim(vim_id)


def vim_list(request, **params):
    LOG.debug("vim_list(): params=%s", params)
    vims = apmecclient(request).list_vims(**params).get('vims')
    return vims


def events_list(request, resource_id):
    params = {'resource_id': resource_id}
    events = apmecclient(request).list_events(**params).get('events')
    LOG.debug("events_list() params=%s events=%s l=%s", params, events,
              len(events))
    return events


def create_mesd(request, tosca_body=None, **params):
    LOG.debug("create_mesd(): params=%s", params)
    mesd_instance = apmecclient(request).create_mesd(body=tosca_body)
    return mesd_instance


def mesd_list(request, **params):
    LOG.debug("mesd_list(): params=%s", params)
    mesds = apmecclient(request).list_mesds(**params).get('mesds')
    return mesds


def get_mesd(request, mesd_id):
    LOG.debug("mesd_get(): mesd_id=%s", str(mesd_id))
    mesd = apmecclient(request).show_mesd(mesd_id)
    return mesd


def delete_mesd(request, mesd_id):
    LOG.debug("delete_mesd():mesd_id=%s", str(mesd_id))
    apmecclient(request).delete_mesd(mesd_id)


def get_mes(request, mes_id):
    LOG.debug("mes_get(): mes_id=%s", str(mes_id))
    mes_instance = apmecclient(request).show_mes(mes_id)
    return mes_instance


def delete_mes(request, mes_id):
    LOG.debug("delete_mes():mes_id=%s", str(mes_id))
    apmecclient(request).delete_ns(mes_id)


def mes_list(request, **params):
    LOG.debug("mes_list(): params=%s", params)
    mess = apmecclient(request).list_mess(**params).get('mess')
    return mess


def create_mes(request, mes_arg, **params):
    LOG.debug("create_mes(): mes_arg=%s", str(mes_arg))
    mes_instance = apmecclient(request).create_mes(body=mes_arg)
    return mes_instance
