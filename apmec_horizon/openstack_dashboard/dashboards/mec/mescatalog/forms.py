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

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from apmec_horizon.openstack_dashboard import api


class OnBoardMES(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'rows': 4}),
                                  label=_("Description"),
                                  required=False)
    source_type = forms.ChoiceField(
        label=_('TOSCA Template Source'),
        required=False,
        choices=[('file', _('TOSCA Template File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'source'}))

    toscal_file = forms.FileField(
        label=_("TOSCA Template File"),
        help_text=_("A local TOSCA template file to upload."),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-file': _('TOSCA Template File')}),
        required=False)

    direct_input = forms.CharField(
        label=_('TOSCA YAML'),
        help_text=_('The YAML formatted contents of a TOSCA template.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-raw': _('TOSCA YAML')}),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(OnBoardMES, self).__init__(request, *args, **kwargs)

    def clean(self):
        data = super(OnBoardMES, self).clean()

        # The key can be missing based on particular upload
        # conditions. Code defensively for it here...
        toscal_file = data.get('toscal_file', None)
        toscal_raw = data.get('direct_input', None)
        source_type = data.get("source_type")
        if source_type == "file" and not toscal_file:
            raise ValidationError(
                _("No TOSCA template file selected."))
        if source_type == "raw" and not toscal_raw:
            raise ValidationError(
                _("No direct input specified."))

        if toscal_file and not toscal_file.name.endswith(('.yaml', '.csar')):
            raise ValidationError(_("Only .yaml or .csar file uploads \
                                    are supported"))

        try:
            if toscal_file:
                toscal_str = self.files['toscal_file'].read()
            else:
                toscal_str = data['direct_input']
            # toscal = yaml.loads(toscal_str)
            data['tosca'] = toscal_str
        except Exception as e:
            msg = _('There was a problem loading the namespace: %s.') % e
            raise forms.ValidationError(msg)

        return data

    def handle(self, request, data):
        try:
            toscal = data['tosca']
            mesd_name = data['name']
            mesd_description = data['description']
            tosca_arg = {'mesd': {'name': mesd_name,
                                 'description': mesd_description,
                                 'attributes': {'mesd': toscal}}}
            mesd_instance = api.apmec.create_mesd(request, tosca_arg)
            messages.success(request,
                             _('MES Catalog entry %s has been created.') %
                             mesd_instance['mesd']['name'])
            return toscal
        except Exception as e:
            msg = _('Unable to create TOSCA. %s')
            msg %= e.message.split('Failed validating', 1)[0]
            exceptions.handle(request, message=msg)
            return False
