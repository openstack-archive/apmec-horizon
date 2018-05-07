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


class DeleteMESD(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete MES",
            u"Delete MESs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete MES",
            u"Delete MESs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_mesd(request, obj_id)


class OnBoardMES(tables.LinkAction):
    name = "onboardmes"
    verbose_name = _("Onboard MES")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:mescatalog:onboardmes"


class MESCatalogTable(tables.DataTable):
    name = tables.Column('name',
                         link="horizon:mec:mescatalog:detail",
                         verbose_name=_("Name"))
    description = tables.Column('description',
                                verbose_name=_("Description"))
    id = tables.Column('id',
                       verbose_name=_("Catalog Id"))

    class Meta(object):
        name = "mescatalog"
        verbose_name = _("MESCatalog")
        table_actions = (OnBoardMES, DeleteMESD, MyFilterAction,)
