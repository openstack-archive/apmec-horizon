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


from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables

from openstack_dashboard import policy
from apmec_horizon.openstack_dashboard import api
from apmecclient.common.exceptions import NotFound


class MESManagerItem(object):
    def __init__(self, name, description, vim, status,
                 mes_id, error_reason):
        self.name = name
        self.description = description
        self.vim = vim
        self.status = status
        self.id = mes_id
        self.error_reason = error_reason


class MESManagerItemList(object):
    MESLIST_P = []

    @classmethod
    def get_obj_given_stack_ids(cls, mes_id):
        for obj in cls.MESLIST_P:
            if obj.id == mes_id:
                return obj

    @classmethod
    def add_item(cls, item):
        cls.MESLIST_P.append(item)

    @classmethod
    def clear_list(cls):
        cls.MESLIST_P = []


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class MESUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.status != 'DELETE_COMPLETE'

    def get_data(self, request, mes_id):
        try:
            # stack = api.heat.stack_get(request, stack_id)
            # if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
            #    raise Http404
            item = MESManagerItemList.get_obj_given_stack_ids(mes_id)
            mes_instance = api.apmec.get_mes(request, mes_id)

            if not mes_instance and not item:
                # TODO(NAME) - bail with error
                return None

            if not mes_instance and item:
                # API failure, just keep the current state
                return item

            mes = mes_instance['mes']
            try:
                mes_desc_str = mes['description']
            except KeyError:
                mes_desc_str = ""

            vim = mes['vim_id']
            if not item:
                # Add an item entry
                item = MESManagerItem(mes['name'], mes_desc_str,
                                     str(vim),
                                     mes['status'], mes['id'],
                                     mes['error_reason'])
            else:
                item.description = mes_desc_str
                item.status = mes['status']
                item.id = mes['id']
            return item
        except (Http404, NotFound):
            raise Http404
        except Exception as e:
            messages.error(request, e)
            raise


class DeleteMES(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Terminate MES",
            u"Terminate MESs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Terminate MES",
            u"Terminate MESs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_mes(request, obj_id)


class DeployMES(tables.LinkAction):
    name = "deploymes"
    verbose_name = _("Deploy MES")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:mesmanager:deploymes"


class MESManagerTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("ERROR", False),
    )
    name = tables.Column("name",
                         link="horizon:mec:mesmanager:detail",
                         verbose_name=_("MES Name"))
    description = tables.Column("description",
                                verbose_name=_("Description"))
    vim = tables.Column("vim", verbose_name=_("VIM"))
    status = tables.Column("status",
                           status=True,
                           status_choices=STATUS_CHOICES)
    error_reason = tables.Column("error_reason",
                                 verbose_name=_("Error Reason"))

    class Meta(object):
        name = "mesmanager"
        verbose_name = _("MESManager")
        status_columns = ["status", ]
        row_class = MESUpdateRow
        table_actions = (DeployMES, DeleteMES, MyFilterAction,)
