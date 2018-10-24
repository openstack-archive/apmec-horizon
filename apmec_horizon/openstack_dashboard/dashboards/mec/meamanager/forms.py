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

import yaml

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from oslo_log import log as logging

from horizon import exceptions
from horizon import forms
from horizon import messages

from apmec_horizon.openstack_dashboard import api

LOG = logging.getLogger(__name__)


class DeployMEA(forms.SelfHandlingForm):
    mea_name = forms.CharField(max_length=255, label=_("MEA Name"))
    description = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'rows': 4}),
                                  label=_("Description"),
                                  required=False)
    mead_id = forms.ChoiceField(label=_("MEA Catalog Name"),
                                required=False)
    template_source = forms.ChoiceField(
        label=_('MEAD template Source'),
        required=False,
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'template'}))
    template_file = forms.FileField(
        label=_('MEAD template File'),
        help_text=_('MEAD template to create MEA'),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'template',
                   'data-template-file': _('TOSCA Template File')}),
        required=False)
    template_input = forms.CharField(
        label=_('MEAD template'),
        help_text=_('The YAML formatted contents of MEAD template.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'template',
                   'data-template-raw': _('MEAD template')}),
        required=False)
    vim_id = forms.ChoiceField(label=_("VIM Name"), required=False)
    region_name = forms.CharField(label=_("Region Name"), required=False)
    source_type = forms.ChoiceField(
        label=_('Parameter Value Source'),
        required=False,
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'source'}))

    param_file = forms.FileField(
        label=_('Parameter Value File'),
        help_text=_('A local Parameter Value file to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-file': _('Parameter Value File')}),
        required=False)

    direct_input = forms.CharField(
        label=_('Parameter Value YAML'),
        help_text=_('The YAML formatted contents of Parameter Values.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-raw': _('Parameter Values')}),
        required=False)

    config_type = forms.ChoiceField(
        label=_('Configuration Value Source'),
        required=False,
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'config'}))

    config_file = forms.FileField(
        label=_('Configuration Value File'),
        help_text=_('MEA Configuration file with YAML '
                    'formatted contents to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'config',
                   'data-config-file': _('Configuration Value File')}),
        required=False)

    config_input = forms.CharField(
        label=_('Configuration Value YAML'),
        help_text=_('YAML formatted MEA configuration text.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'config',
                   'data-config-raw': _('Configuration Values')}),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(DeployMEA, self).__init__(request, *args, **kwargs)

        try:
            mead_list = api.apmec.mead_list(request,
                                            template_source='onboarded')
            available_choices_mead = [(mea['id'], mea['name']) for mea in
                                      mead_list]
        except Exception as e:
            available_choices_mead = []
            msg = _('Failed to retrieve available MEA Catalog names: %s') % e
            LOG.error(msg)

        try:
            vim_list = api.apmec.vim_list(request)
            available_choices_vims = [(vim['id'], vim['name']) for vim in
                                      vim_list]

        except Exception as e:
            available_choices_vims = []
            msg = _('Failed to retrieve available VIM names: %s') % e
            LOG.error(msg)

        self.fields['mead_id'].choices = [('', _('Select a MEA Catalog Name'))
                                          ]+available_choices_mead
        self.fields['vim_id'].choices = [('',
                                          _('Select a VIM Name'))
                                         ]+available_choices_vims

    def clean(self):
        data = super(DeployMEA, self).clean()

        template_file = data.get('template_file', None)
        template_raw = data.get('template_input', None)

        if template_raw and template_file:
            raise ValidationError(
                _("Cannot specify both file and direct input."))

        if template_file and not template_file.name.endswith('.yaml'):
            raise ValidationError(
                _("Please upload .yaml file only."))

        if template_file:
            data['mead_template'] = yaml.load(template_file,
                                              Loader=yaml.SafeLoader)
        elif template_raw:
            data['mead_template'] = yaml.load(data['template_input'],
                                              Loader=yaml.SafeLoader)
        else:
            data['mead_template'] = None

        param_file = data.get('param_file', None)
        param_raw = data.get('direct_input', None)

        if param_raw and param_file:
            raise ValidationError(
                _("Cannot specify both file and direct input."))

        if param_file and not param_file.name.endswith('.yaml'):
            raise ValidationError(
                _("Please upload .yaml file only."))

        if param_file:
            data['param_values'] = self.files['param_file'].read()
        elif param_raw:
            data['param_values'] = data['direct_input']
        else:
            data['param_values'] = None

        config_file = data.get('config_file', None)
        config_raw = data.get('config_input', None)

        if config_file and config_raw:
            raise ValidationError(
                _("Cannot specify both file and direct input."))

        if config_file and not config_file.name.endswith('.yaml'):
            raise ValidationError(_("Only .yaml file uploads supported"))

        if config_file:
            data['config_values'] = self.files['config_file'].read()
        elif config_raw:
            data['config_values'] = data['config_input']
        else:
            data['config_values'] = None

        return data

    def handle(self, request, data):
        try:
            mea_name = data['mea_name']
            description = data['description']
            mead_id = data.get('mead_id')
            mead_template = data.get('mead_template')
            vim_id = data['vim_id']
            region_name = data['region_name']
            param_val = data['param_values']
            config_val = data['config_values']

            if (mead_id == '') and (mead_template is None):
                raise ValidationError(_("Both MEAD id and template cannot be "
                                        "empty. Please specify one of them"))

            if (mead_id != '') and (mead_template is not None):
                raise ValidationError(_("Both MEAD id and template cannot be "
                                        "specified. Please specify any one"))

            mea_arg = {'mea': {'mead_id': mead_id, 'name':  mea_name,
                               'description': description,
                               'vim_id': vim_id,
                               'mead_template': mead_template}}
            if region_name:
                mea_arg.setdefault('placement_attr', {})[
                    region_name] = region_name
            mea_attr = mea_arg['mea'].setdefault('attributes', {})
            if param_val:
                mea_attr['param_values'] = param_val
            if config_val:
                mea_attr['config'] = config_val

            api.apmec.create_mea(request, mea_arg)
            messages.success(request,
                             _('MEA %s create operation initiated.') %
                             mea_name)
            return True
        except Exception as e:
            exceptions.handle(request,
                              _('Failed to create MEA: %s') %
                              e.message)
