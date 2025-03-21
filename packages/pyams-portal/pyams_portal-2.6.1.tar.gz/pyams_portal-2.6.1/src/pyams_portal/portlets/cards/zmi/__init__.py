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

"""PyAMS_portal.portlets.cards.zmi module

"""

from pyramid.view import view_config
from zope.interface import Interface, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.portlets.cards.interfaces import ICard, ICardsContainer, ICardsPortletSettings
from pyams_portal.zmi import PortletPreviewer
from pyams_sequence.interfaces import ISequentialIdInfo
from pyams_skin.interfaces.view import IModalPage
from pyams_skin.interfaces.viewlet import IContentSuffixViewletManager
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_template.template import template_config
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config, query_adapter
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm, FormGroupSwitcher
from pyams_zmi.helper.container import delete_container_element, switch_element_attribute
from pyams_zmi.helper.event import get_json_table_row_add_callback, \
    get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.form import IFormTitle, IPropertiesEditForm
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import I18nColumnMixin, IconColumn, InnerTableAdminView, NameColumn, \
    ReorderColumn, SortableTable, TableElementEditor, TrashColumn, VisibilityColumn
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class CardsTable(SortableTable):
    """Cards table"""

    container_class = ICardsContainer

    display_if_empty = True


@adapter_config(required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IValues)
class CardsTableValues(ContextRequestViewAdapter):
    """Cards table values adapter"""

    @property
    def values(self):
        """Cards table values getter"""
        yield from self.context.values()


@adapter_config(name='reorder',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableReorderColumn(ReorderColumn):
    """Cards table reorder column"""


@view_config(name='reorder.json',
             context=ICardsContainer, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=MANAGE_TEMPLATE_PERMISSION)
def reorder_cards_table(request):
    """Reorder cards table"""
    order = request.params.get('order').split(';')
    request.context.updateOrder(order)
    return {
        'status': 'success',
        'closeForm': False
    }


@adapter_config(name='visible',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableVisibleColumn(VisibilityColumn):
    """Cards table visible column"""

    hint = _("Click icon to show or hide card")


@view_config(name='switch-visible-item.json',
             context=ICardsContainer, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def switch_visible_card(request):
    """Switch visible card"""
    return switch_element_attribute(request)


@adapter_config(name='title',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableTitleColumn(NameColumn):
    """Cards table name column"""

    i18n_header = _("Title")


@adapter_config(name='target',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableTargetColumn(I18nColumnMixin, GetAttrColumn):
    """Cards table target column"""

    i18n_header = _("Target")
    weight = 20

    def get_value(self, obj):
        if obj.reference:
            target = obj.target
            if target is not None:
                label = get_object_label(target, self.request)
                oid = ISequentialIdInfo(obj.target).public_oid
                return '{} ({})'.format(label, oid)
        return obj.target_url or '--'


@adapter_config(name='illustration',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableIllustrationColumn(IconColumn):
    """Cards table illustration column"""

    weight = 90
    icon_class = 'far fa-image text-muted'
    hint = _("Illustration")

    @staticmethod
    def checker(image):
        """Column image checker"""
        return bool(image.illustration and image.illustration.data)


@adapter_config(name='trash',
                required=(ICardsContainer, IAdminLayer, CardsTable),
                provides=IColumn)
class CardsTableTrashColumn(TrashColumn):
    """Cards table trash column"""


@view_config(name='delete-element.json',
             context=ICardsContainer, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=MANAGE_TEMPLATE_PERMISSION)
def delete_card(request):
    """Delete card"""
    return delete_container_element(request)


@viewlet_config(name='cards-content-table',
                context=ICardsContainer, layer=IAdminLayer,
                view=IPropertiesEditForm,
                manager=IContentSuffixViewletManager, weight=10)
class CardsTableView(InnerTableAdminView):
    """Cards table view"""

    table_class = CardsTable
    table_label = _("List of portlet cards")


@adapter_config(required=(Interface, IPyAMSLayer, Interface, ICardsPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/cards-preview.pt', layer=IPyAMSLayer)
class CardsPortletPreviewer(PortletPreviewer):
    """Cards portlet previewer"""


#
# Cards forms
#

@viewlet_config(name='add-card.menu',
                context=ICardsContainer, layer=IAdminLayer, view=CardsTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class CardAddAction(ContextAddAction):
    """Card add action"""

    label = _("Add card")
    href = 'add-card.html'


class ICardForm(Interface):
    """Card form marker interface"""


@ajax_form_config(name='add-card.html',
                  context=ICardsContainer, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@implementer(ICardForm)
class CardAddForm(AdminModalAddForm):
    """Card add form"""

    subtitle = _("New card")
    legend = _("New card properties")
    modal_class = 'modal-xl'

    fields = Fields(ICard).select('title', 'illustration', 'body', 'css_class')
    content_factory = ICard

    def add(self, obj):
        self.context.append(obj)


@adapter_config(required=(ICardsContainer, IAdminLayer, CardAddForm),
                provides=IAJAXFormRenderer)
class CardAddFormRenderer(ContextRequestViewAdapter):
    """Card add form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'status': 'success',
            'callbacks': [
                get_json_table_row_add_callback(self.context, self.request,
                                                CardsTable, changes)
            ]
        }


@adapter_config(required=(ICard, IAdminLayer, Interface),
                provides=ITableElementEditor)
class CardElementEditor(TableElementEditor):
    """Card element editor"""


@ajax_form_config(name='properties.html',
                  context=ICard, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@implementer(ICardForm)
class CardEditForm(AdminModalEditForm):
    """Card properties edit form"""

    @property
    def subtitle(self):
        """Form title getter"""
        translate = self.request.localizer.translate
        return translate(_("Card: {}")).format(get_object_label(self.context, self.request, self))

    legend = _("Card properties")
    modal_class = 'modal-xl'

    fields = Fields(ICard).select('title', 'illustration', 'body', 'css_class')


@adapter_config(required=(ICard, IAdminLayer, IModalPage),
                provides=IFormTitle)
def card_edit_form_title(context, request, view):
    """Card edit form title"""
    settings = get_parent(context, ICardsContainer)
    return query_adapter(IFormTitle, request, settings, view)


@adapter_config(required=(ICard, IAdminLayer, CardEditForm),
                provides=IAJAXFormRenderer)
class CardEditFormRenderer(ContextRequestViewAdapter):
    """Card edit form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(self.context.__parent__, self.request,
                                                    CardsTable, self.context)
            ]
        }


@adapter_config(name='button',
                required=(Interface, IAdminLayer, ICardForm),
                provides=IGroup)
class CardFormButtonEditForm(FormGroupSwitcher):
    """Card form button edit form"""

    legend = _("Action button")

    fields = Fields(ICard).select('reference', 'target_url', 'button_label', 'button_status')
