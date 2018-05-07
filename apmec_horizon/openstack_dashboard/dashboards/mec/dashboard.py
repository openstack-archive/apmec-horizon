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


from django.utils.translation import ugettext_lazy as _

import horizon


class Meamgroup(horizon.PanelGroup):
    slug = "mecgroup"
    name = _("MEA Management")
    panels = ('meacatalog', 'meamanager',)


class Mecogroup(horizon.PanelGroup):
    slug = "meogroup"
    name = _("MEC Orchestration")
    panels = ('vim', 'mescatalog', 'mesmanager')


class Mec(horizon.Dashboard):
    name = _("MEC")
    slug = "mec"
    panels = (Meamgroup, Mecogroup,)  # Add your panels here.
    default_panel = 'meacatalog'  # Specify the slug of the dashboard's
    # default panel.

horizon.register(Mec)
