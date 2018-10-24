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
from apmec_horizon.openstack_dashboard.dashboards.mec.meacatalog import tables
from apmec_horizon.openstack_dashboard.dashboards.mec import utils

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs


class MEACatalogItem(object):
    def __init__(self, name, description, services, mead_id):
        self.id = mead_id
        self.name = name
        self.description = description
        self.services = services


class MEACatalogTab(tabs.TableTab):
    name = _("MEACatalog Tab")
    slug = "meacatalog_tab"
    table_classes = (tables.MEACatalogTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_meacatalog_data(self):
        try:
            # marker = self.request.GET.get(
            #            tables.MEACatalogTable._meta.pagination_param, None)

            self._has_more = False
            catalogs = []
            meads = api.apmec.mead_list(self.request,
                                        template_source="onboarded")
            for mead in meads:
                s_types = [s_type for s_type in mead['service_types']
                           if s_type != 'mead']
                s_types_string = ""
                if len(s_types) > 0:
                    s_types_string = ', '.join(
                        [str(item) for item in s_types])
                item = MEACatalogItem(mead['name'],
                                      mead['description'],
                                      s_types_string, mead['id'])
                catalogs.append(item)
            return catalogs
        except Exception:
            self._has_more = False
            error_message = _('Unable to get mea catalogs')
            exceptions.handle(self.request, error_message)

            return []


class MEACatalogTabs(tabs.TabGroup):
    slug = "meacatalog_tabs"
    tabs = (MEACatalogTab,)
    sticky = True


class TemplateTab(tabs.Tab):
    name = _("Template")
    slug = "template"
    template_name = ("mec/meacatalog/template.html")

    def get_context_data(self, request):
        return {'mead': self.tab_group.kwargs['mead']}


class MEADEventsTab(tabs.TableTab):
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
                                           self.tab_group.kwargs['mead_id'])
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


class MEADDetailTabs(tabs.TabGroup):
    slug = "MEAD_details"
    tabs = (TemplateTab, MEADEventsTab)
    sticky = True
