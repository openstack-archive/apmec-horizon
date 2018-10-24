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

from horizon import exceptions
from horizon import tabs

from apmec_horizon.openstack_dashboard import api
from apmec_horizon.openstack_dashboard.dashboards.mec.mescatalog import tables
from apmec_horizon.openstack_dashboard.dashboards.mec import utils


class MESCatalogItem(object):
    def __init__(self, name, description, mesd_id):
        self.id = mesd_id
        self.name = name
        self.description = description


class MESCatalogTab(tabs.TableTab):
    name = _("MESCatalog Tab")
    slug = "mescatalog_tab"
    table_classes = (tables.MESCatalogTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_mescatalog_data(self):
        try:
            self._has_more = False
            instances = []
            mesds = api.apmec.mesd_list(self.request)
            for mesd in mesds:
                item = MESCatalogItem(mesd['name'],
                                      mesd['description'],
                                      mesd['id'])
                instances.append(item)
            return instances
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


class MESCatalogTabs(tabs.TabGroup):
    slug = "mescatalog_tabs"
    tabs = (MESCatalogTab,)
    sticky = True


class TemplateTab(tabs.Tab):
    name = _("Template")
    slug = "template"
    template_name = ("mec/mescatalog/template.html")

    def get_context_data(self, request):
        return {'mesd': self.tab_group.kwargs['mesd']}


class MESDEventsTab(tabs.TableTab):
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
                                           self.tab_group.kwargs['mesd_id'])
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


class MESDDetailTabs(tabs.TabGroup):
    slug = "MESD_details"
    tabs = (TemplateTab, MESDEventsTab)
    sticky = True
