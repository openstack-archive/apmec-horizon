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


from django.http import Http404
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables

from openstack_dashboard import policy
from apmec_horizon.openstack_dashboard import api
from apmecclient.common.exceptions import NotFound


class MEAManagerItem(object):
    def __init__(self, name, description, meas, vim, status,
                 stack_status, stack_id, error_reason):
        self.name = name
        self.description = description
        self.meas = meas
        self.vim = vim
        self.status = status
        self.stack_status = stack_status
        self.id = stack_id
        self.error_reason = error_reason


class MEAManagerItemList(object):
    MEALIST_P = []

    @classmethod
    def get_obj_given_stack_id(cls, mea_id):
        for obj in cls.MEALIST_P:
            if obj.id == mea_id:
                return obj

    @classmethod
    def add_item(cls, item):
        cls.MEALIST_P.append(item)

    @classmethod
    def clear_list(cls):
        cls.MEALIST_P = []


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class StacksUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.status != 'DELETE_COMPLETE'

    def get_data(self, request, stack_id):
        try:
            stack = api.heat.stack_get(request, stack_id)
            if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
                raise Http404
            item = MEAManagerItemList.get_obj_given_stack_id(stack_id)
            item.status = stack.status
            item.stack_status = stack.stack_status
            return item
        except Http404:
            raise
        except Exception as e:
            messages.error(request, e)
            raise


class MEAUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.status != 'DELETE_COMPLETE'

    def get_data(self, request, mea_id):
        try:
            # stack = api.heat.stack_get(request, stack_id)
            # if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
            #    raise Http404
            item = MEAManagerItemList.get_obj_given_stack_id(mea_id)
            mea_instance = api.apmec.get_mea(request, mea_id)

            if not mea_instance and not item:
                # TODO(NAME) - bail with error
                return None

            if not mea_instance and item:
                # API failure, just keep the current state
                return item

            mea = mea_instance['mea']
            try:
                mea_services_str = mea['attributes']['service_type']
            except KeyError:
                mea_services_str = ""
            try:
                mea_desc_str = mea['description']
            except KeyError:
                mea_desc_str = ""

            vim = mea['placement_attr']['vim_name']
            if not item:
                # Add an item entry
                item = MEAManagerItem(mea['name'], mea_desc_str,
                                      mea_services_str, str(vim),
                                      mea['status'], mea['status'], mea['id'],
                                      mea['error_reason'])
            else:
                item.description = mea_desc_str
                item.meas = mea_services_str
                item.status = mea['status']
                item.stack_status = mea['status']
            return item
        except (Http404, NotFound):
            raise Http404
        except Exception as e:
            messages.error(request, e)
            raise


class DeleteMEA(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Terminate MEA",
            u"Terminate MEAs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Terminate MEA",
            u"Terminate MEAs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_mea(request, obj_id)


class DeployMEA(tables.LinkAction):
    name = "deploymea"
    verbose_name = _("Deploy MEA")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:meamanager:deploymea"


class MEAManagerTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("ERROR", False),
    )
    STACK_STATUS_DISPLAY_CHOICES = (
        ("init_in_progress", pgettext_lazy("current status of stack",
                                           u"Init In Progress")),
        ("init_complete", pgettext_lazy("current status of stack",
                                        u"Init Complete")),
        ("init_failed", pgettext_lazy("current status of stack",
                                      u"Init Failed")),
        ("create_in_progress", pgettext_lazy("current status of stack",
                                             u"Create In Progress")),
        ("create_complete", pgettext_lazy("current status of stack",
                                          u"Create Complete")),
        ("create_failed", pgettext_lazy("current status of stack",
                                        u"Create Failed")),
        ("delete_in_progress", pgettext_lazy("current status of stack",
                                             u"Delete In Progress")),
        ("delete_complete", pgettext_lazy("current status of stack",
                                          u"Delete Complete")),
        ("delete_failed", pgettext_lazy("current status of stack",
                                        u"Delete Failed")),
        ("update_in_progress", pgettext_lazy("current status of stack",
                                             u"Update In Progress")),
        ("update_complete", pgettext_lazy("current status of stack",
                                          u"Update Complete")),
        ("update_failed", pgettext_lazy("current status of stack",
                                        u"Update Failed")),
        ("rollback_in_progress", pgettext_lazy("current status of stack",
                                               u"Rollback In Progress")),
        ("rollback_complete", pgettext_lazy("current status of stack",
                                            u"Rollback Complete")),
        ("rollback_failed", pgettext_lazy("current status of stack",
                                          u"Rollback Failed")),
        ("suspend_in_progress", pgettext_lazy("current status of stack",
                                              u"Suspend In Progress")),
        ("suspend_complete", pgettext_lazy("current status of stack",
                                           u"Suspend Complete")),
        ("suspend_failed", pgettext_lazy("current status of stack",
                                         u"Suspend Failed")),
        ("resume_in_progress", pgettext_lazy("current status of stack",
                                             u"Resume In Progress")),
        ("resume_complete", pgettext_lazy("current status of stack",
                                          u"Resume Complete")),
        ("resume_failed", pgettext_lazy("current status of stack",
                                        u"Resume Failed")),
        ("adopt_in_progress", pgettext_lazy("current status of stack",
                                            u"Adopt In Progress")),
        ("adopt_complete", pgettext_lazy("current status of stack",
                                         u"Adopt Complete")),
        ("adopt_failed", pgettext_lazy("current status of stack",
                                       u"Adopt Failed")),
        ("snapshot_in_progress", pgettext_lazy("current status of stack",
                                               u"Snapshot In Progress")),
        ("snapshot_complete", pgettext_lazy("current status of stack",
                                            u"Snapshot Complete")),
        ("snapshot_failed", pgettext_lazy("current status of stack",
                                          u"Snapshot Failed")),
        ("check_in_progress", pgettext_lazy("current status of stack",
                                            u"Check In Progress")),
        ("check_complete", pgettext_lazy("current status of stack",
                                         u"Check Complete")),
        ("check_failed", pgettext_lazy("current status of stack",
                                       u"Check Failed")),
    )
    name = tables.Column("name",
                         link="horizon:mec:meamanager:detail",
                         verbose_name=_("MEA Name"))
    description = tables.Column("description",
                                verbose_name=_("Description"))
    meas = tables.Column("meas",
                         verbose_name=_("Deployed Services"))
    vim = tables.Column("vim", verbose_name=_("VIM"))
    status = tables.Column("status",
                           hidden=True,
                           status=True,
                           status_choices=STATUS_CHOICES)
    stack_status = tables.Column("stack_status",
                                 verbose_name=_("Status"),
                                 display_choices=STACK_STATUS_DISPLAY_CHOICES)
    error_reason = tables.Column("error_reason",
                                 verbose_name=_("Error Reason"))

    class Meta(object):
        name = "meamanager"
        verbose_name = _("MEAManager")
        status_columns = ["status", ]
        row_class = MEAUpdateRow
        table_actions = (DeployMEA, DeleteMEA, MyFilterAction,)
