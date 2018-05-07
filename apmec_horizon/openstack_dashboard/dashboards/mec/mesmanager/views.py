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
from oslo_log import log as logging

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized

from apmec_horizon.openstack_dashboard import api as apmec_api
from apmec_horizon.openstack_dashboard.dashboards.mec.mesmanager \
    import forms as project_forms

from apmec_horizon.openstack_dashboard.dashboards.mec.mesmanager \
    import tabs as mec_tabs

LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = mec_tabs.MESManagerTabs
    template_name = 'mec/mesmanager/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class DeployMESView(forms.ModalFormView):
    form_class = project_forms.DeployMES
    template_name = 'mec/mesmanager/deploy_mes.html'
    success_url = reverse_lazy("horizon:mec:mesmanager:index")
    modal_id = "deploy_mes_modal"
    modal_header = _("Deploy MES")
    submit_label = _("Deploy MES")
    submit_url = "horizon:mec:mesmanager:deploymes"

    def get_initial(self):
        # return {"instance_id": self.kwargs["instance_id"]}
        return {}

    def get_context_data(self, **kwargs):
        context = super(DeployMESView, self).get_context_data(**kwargs)
        # instance_id = self.kwargs['instance_id']
        # context['instance_id'] = instance_id
        # context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url)
        return context


class DetailView(tabs.TabView):
    tab_group_class = mec_tabs.MESDetailsTabs
    template_name = 'mec/mesmanager/detail.html'
    redirect_url = 'horizon:mec:mesmanager:index'
    page_title = _("MES Details: {{ mes_id }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        mes = self.get_data()
        context['mes'] = mes
        context['mes_id'] = kwargs['mes_id']
        context['url'] = reverse(self.redirect_url)
        return context

    @memoized.memoized_method
    def get_data(self):
        mes_id = self.kwargs['mes_id']

        try:
            mes = apmec_api.apmec.get_mes(self.request, mes_id)
            return mes
        except ValueError as e:
            msg = _('Cannot decode json : %s') % e
            LOG.error(msg)
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'MES "%s".') % mes_id,
                              redirect=redirect)
            raise exceptions.Http302(redirect)

    def get_tabs(self, request, *args, **kwargs):
        mes = self.get_data()
        return self.tab_group_class(request, mes=mes, **kwargs)
