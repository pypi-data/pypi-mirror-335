#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_portal.zmi.widget module

This module defines a custom widget used to select portlet renderer, which
provides access to custom renderer settings, if any.
"""

from zope.interface import implementer

from pyams_form.browser.select import SelectWidget
from pyams_form.interfaces import INPUT_MODE
from pyams_form.template import widget_template_config
from pyams_form.widget import FieldWidget
from pyams_portal.zmi import layout_css, layout_js
from pyams_utils.fanstatic import get_resource_path
from pyams_utils.interfaces.data import IObjectData
from pyams_zmi.interfaces import IAdminLayer

__docformat__ = 'restructuredtext'

from pyams_portal import _


@widget_template_config(mode=INPUT_MODE,
                        template='templates/renderer-input.pt',
                        layer=IAdminLayer)
@implementer(IObjectData)
class RendererSelectWidget(SelectWidget):
    """Portlet renderer widget"""

    format_renderers = True
    no_value_message = _("No selected renderer (use default)")

    @property
    def object_data(self):
        if not self.format_renderers:
            return None
        return {
            'ams-modules': {
                "portal": {
                    "src": get_resource_path(layout_js),
                    "css": get_resource_path(layout_css)
                }
            },
            'ams-select2-after-init-callback': 'MyAMS.portal.renderer.init',
            'ams-select2-template-result': 'MyAMS.portal.renderer.formatRenderer'
        }

    @property
    def show_renderer_properties(self):
        """Getter to check access to renderer properties action"""
        renderer = self.context.get_renderer(self.request)
        return (renderer is not None) and (renderer.settings_interface is not None)


def RendererSelectFieldWidget(field, request):  # pylint: disable=invalid-name
    """Portlet renderer field widget"""
    return FieldWidget(field, RendererSelectWidget(request))
