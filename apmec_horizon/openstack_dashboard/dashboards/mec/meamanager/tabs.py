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
from apmec_horizon.openstack_dashboard.dashboards.mec.meamanager import tables
from apmec_horizon.openstack_dashboard.dashboards.mec import utils

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs


class MEAManagerTab(tabs.TableTab):
    name = _("MEAManager Tab")
    slug = "meamanager_tab"
    table_classes = (tables.MEAManagerTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_meamanager_data(self):
        try:
            # marker = self.request.GET.get(
            #            tables.MEAManagerTable._meta.pagination_param, None)

            # instances, self._has_more = api.nova.server_list(
            #    self.request,
            #    search_opts={'marker': marker, 'paginate': True})
            self._has_more = True
            tables.MEAManagerItemList.clear_list()
            meas = api.apmec.mea_list(self.request)
            for mea in meas:
                try:
                    mea_services_str = mea['attributes']['service_type']
                except KeyError:
                    mea_services_str = ""
                try:
                    mea_desc_str = mea['description']
                except KeyError:
                    mea_desc_str = ""

                vim = mea['placement_attr']['vim_name']
                obj = tables.MEAManagerItem(
                    mea['name'],
                    mea_desc_str,
                    mea_services_str,
                    vim,
                    mea['status'],
                    mea['status'],
                    mea['id'],
                    mea['error_reason'])
                tables.MEAManagerItemList.add_item(obj)
            return tables.MEAManagerItemList.MEALIST_P
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


class MEAManagerTabs(tabs.TabGroup):
    slug = "meamanager_tabs"
    tabs = (MEAManagerTab,)
    sticky = True


class VDUDetailTab(tabs.Tab):
    name = _("VDU Detail")
    slug = "VDU_Details"
    template_name = "mec/meamanager/vdu_details.html"

    def get_context_data(self, request):
        return {'mea': self.tab_group.kwargs['mea']}


class MEAEventsTab(tabs.TableTab):
    name = _("Events Tab")
    slug = "events_tab"
    table_classes = (utils.EventsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_events_data(self):
        try:
            self._has_more = True
            utils.EventItemList.clear_list()
            events = api.apmec.events_list(self.request,
                                           self.tab_group.kwargs['mea_id'])
            for event in events:
                evt_obj = utils.EventItem(
                    event['id'], event['resource_state'],
                    event['event_type'],
                    event['timestamp'],
                    event['event_details'])
                utils.EventItemList.add_item(evt_obj)
            return utils.EventItemList.EVTLIST_P
        except Exception as e:
            self._has_more = False
            error_message = _('Unable to get events %s') % e
            exceptions.handle(self.request, error_message)
            return []


class MEADetailsTabs(tabs.TabGroup):
    slug = "MEA_details"
    tabs = (VDUDetailTab, MEAEventsTab)
    sticky = True
