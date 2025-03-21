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

"""PyAMS_portal.zmi.template module

This module provides templates management components.
"""

from zope.copy import copy
from zope.interface import Interface, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IAddForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortalTemplate, IPortalTemplateContainer, \
    LOCAL_TEMPLATE_NAME, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.zmi.container import PortalTemplatesContainerTable
from pyams_skin.interfaces.view import IModalPage
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_table.interfaces import IColumn
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, AdminModalAddForm
from pyams_zmi.helper.event import get_json_table_row_add_callback
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel, TITLE_SPAN, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IPropertiesMenu, IToolbarViewletManager
from pyams_zmi.table import ActionColumn, TableElementEditor
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class IPortalTemplateAddForm(IAddForm):
    """Portal template add form marker interface"""


@viewlet_config(name='add-portal-template.menu',
                context=IPortalTemplateContainer, layer=IAdminLayer,
                view=PortalTemplatesContainerTable, manager=IToolbarViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=10)
class PortalTemplateAddAction(ContextAddAction):
    """Portal template add action"""

    label = _("Add template")
    href = 'add-portal-template.html'


@ajax_form_config(name='add-portal-template.html',
                  context=IPortalTemplateContainer, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@implementer(IPortalTemplateAddForm)
class PortalTemplateAddForm(AdminModalAddForm):
    """Portal template add form"""

    subtitle = _("New template")
    legend = _("New template properties")

    fields = Fields(IPortalTemplate)
    content_factory = IPortalTemplate

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context[oid] = obj


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, IPortalTemplateAddForm),
                provides=IFormTitle)
def portal_template_add_form_title(context, request, form):
    """Portal template add form title"""
    manager = get_utility(IPortalTemplateContainer)
    return TITLE_SPAN.format(get_object_label(manager, request, form))


@adapter_config(required=IPortalTemplate,
                provides=IObjectLabel)
def portal_template_label(context):
    """Portal templates container table element name factory"""
    return context.name


@adapter_config(name='form-title',
                required=(IPortalTemplate, IAdminLayer, IModalPage),
                provides=IObjectLabel)
def portal_template_form_label(context, request, view):
    """Portal template form label"""
    translate = request.localizer.translate
    if context.name == LOCAL_TEMPLATE_NAME:
        parent = get_parent(context, IPortalContext)
        label = get_object_label(parent, request, view, name='form-title')
        return translate(_("{} --- Local template")).format(label)
    return translate(_("Template: {}")).format(context.name)


@adapter_config(required=(IPortalTemplate, IAdminLayer, Interface),
                provides=ITableElementEditor)
class PortalTemplatesContainerElementEditor(TableElementEditor):
    """Portal template element editor"""

    view_name = 'admin#layout.html'
    modal_target = False


@adapter_config(name='clone',
                required=(IPortalTemplateContainer, IAdminLayer, PortalTemplatesContainerTable),
                provides=IColumn)
class PortalTemplatesContainerCloneColumn(ActionColumn):
    """Portal templates container clone column"""

    hint = _("Clone template")
    icon_class = 'far fa-clone'

    href = 'clone-template.html'
    weight = 100

    permission = MANAGE_TEMPLATE_PERMISSION


@ajax_form_config(name='clone-template.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@implementer(IPortalTemplateAddForm)
class PortalTemplateCloneForm(AdminModalAddForm):
    """Portal template clone form"""

    subtitle = _("Template clone")
    legend = _("New template clone properties")

    fields = Fields(IPortalTemplate).select('name')

    def create(self, data):
        return copy(self.context)

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context.__parent__[oid] = obj


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateCloneForm),
                provides=IFormTitle)
def portal_template_clone_form_title(context, request, form):
    """Portal template add form title"""
    manager = get_utility(IPortalTemplateContainer)
    return TITLE_SPAN_BREAK.format(
        get_object_label(manager, request, form),
        get_object_label(context, request, form, name='form-title'))


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, IPortalTemplateAddForm),
                provides=IAJAXFormRenderer)
class PortalTemplateAddFormRenderer(ContextRequestViewAdapter):
    """Alchemy engine add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'callbacks': [
                get_json_table_row_add_callback(self.context, self.request,
                                                PortalTemplatesContainerTable, changes)
            ]
        }


@viewlet_config(name='properties.menu',
                context=IPortalTemplate, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatePropertiesMenuItem(NavigationMenuItem):
    """Portal template properties menu item"""

    label = _("Properties")
    href = '#properties.html'


@ajax_form_config(name='properties.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatePropertiesEditForm(AdminEditForm):
    """Portal template properties edit form"""

    title = _("Template configuration")
    legend = _("Template properties")

    fields = Fields(IPortalTemplate)
    _edit_permission = MANAGE_TEMPLATE_PERMISSION


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplatePropertiesEditForm),
                provides=IAJAXFormRenderer)
class PortalTemplatePropertiesEditFormRenderer(ContextRequestViewAdapter):
    """Portal template properties edit form renderer"""

    def render(self, changes):
        """Form renderer"""
        if not changes:
            return None
        return {
            'status': 'redirect',
            'message': self.request.localizer.translate(self.view.success_message)
        }
