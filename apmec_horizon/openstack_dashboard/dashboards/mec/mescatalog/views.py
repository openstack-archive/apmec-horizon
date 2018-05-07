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


from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs

from horizon.utils import memoized

from openstack_dashboard import api

from apmec_horizon.openstack_dashboard import api as apmec_api
from apmec_horizon.openstack_dashboard.dashboards.mec.mescatalog \
    import tabs as mec_tabs

from apmec_horizon.openstack_dashboard.dashboards.mec.mescatalog \
    import forms as project_forms


class IndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = mec_tabs.MESCatalogTabs
    template_name = 'mec/mescatalog/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class OnBoardMESView(forms.ModalFormView):
    form_class = project_forms.OnBoardMES
    template_name = 'mec/mescatalog/onboardmes.html'
    success_url = reverse_lazy("horizon:mec:mescatalog:index")
    modal_id = "onboardmes_modal"
    modal_header = _("OnBoard MES")
    submit_label = _("OnBoard MES")
    submit_url = "horizon:mec:mescatalog:onboardmes"

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.nova.server_get(self.request,
                                       self.kwargs["instance_id"])
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve instance."))

    def get_initial(self):
        # return {"instance_id": self.kwargs["instance_id"]}
        return {}

    def get_context_data(self, **kwargs):
        context = super(OnBoardMESView, self).get_context_data(**kwargs)
        # instance_id = self.kwargs['instance_id']
        # context['instance_id'] = instance_id
        # context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url)
        return context


class DetailView(tabs.TabView):
    tab_group_class = mec_tabs.MESDDetailTabs
    template_name = 'mec/mescatalog/detail.html'
    redirect_url = 'horizon:mec:mescatalog:index'
    page_title = _("MESD Details: {{ mesd_id }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        mesd = self.get_data()
        context['mesd'] = mesd
        context['mesd_id'] = kwargs['mesd_id']
        context['url'] = reverse(self.redirect_url)
        return context

    @memoized.memoized_method
    def get_data(self):
        mesd_id = self.kwargs['mesd_id']

        try:
            template = None
            mesd = apmec_api.apmec.get_mesd(self.request, mesd_id)
            attributes_json = mesd['mesd']['attributes']
            template = attributes_json.get('mesd', None)
            mesd['template'] = template
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'MESD "%s".') % mesd_id,
                              redirect=redirect)
            raise exceptions.Http302(redirect)
        return mesd

    def get_tabs(self, request, *args, **kwargs):
        mesd = self.get_data()
        return self.tab_group_class(request, mesd=mesd, **kwargs)
