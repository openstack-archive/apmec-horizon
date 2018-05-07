# Copyright 2016 Brocade Communications System, Inc.
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


from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import policy
from apmec_horizon.openstack_dashboard import api


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class DeleteVIMLink(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete VIM",
            u"Delete VIMs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete VIM",
            u"Delete VIMs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_vim(request, obj_id)


class RegisterVIMLink(tables.LinkAction):
    name = "registervim"
    verbose_name = _("Register VIM")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:vim:registervim"


class VIMTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_("Name"),
                         link="horizon:mec:vim:detail",)
    description = tables.Column('description', verbose_name=_("Description"))
    id = tables.Column('id', verbose_name=_("VIM Id"))
    auth_url = tables.Column('auth_url', verbose_name=_("Auth URL"))
    regions = tables.Column('regions', verbose_name=_("Regions"))
    user = tables.Column('user', verbose_name=_("User"))
    project = tables.Column('project', verbose_name=_("Project"))
    status = tables.Column('status', verbose_name=_("Status"))

    class Meta(object):
        name = "vim"
        verbose_name = _("VIM")
        table_actions = (RegisterVIMLink, DeleteVIMLink, MyFilterAction,)
