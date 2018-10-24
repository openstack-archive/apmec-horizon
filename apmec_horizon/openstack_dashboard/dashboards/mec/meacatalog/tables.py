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


from apmec_horizon.openstack_dashboard import api

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import policy


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class DeleteMEAD(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete MEA",
            u"Delete MEAs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete MEA",
            u"Delete MEAs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_mead(request, obj_id)


class OnBoardMEA(tables.LinkAction):
    name = "onboardmea"
    verbose_name = _("Onboard MEA")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:meacatalog:onboardmea"


class MEACatalogTable(tables.DataTable):
    name = tables.Column('name',
                         link="horizon:mec:meacatalog:detail",
                         verbose_name=_("Name"))
    description = tables.Column('description',
                                verbose_name=_("Description"))
    services = tables.Column('service types',
                             verbose_name=_("Service Types"))
    id = tables.Column('id',
                       verbose_name=_("Catalog Id"))

    class Meta(object):
        name = "meacatalog"
        verbose_name = _("MEACatalog")
        table_actions = (OnBoardMEA, DeleteMEAD, MyFilterAction,)
