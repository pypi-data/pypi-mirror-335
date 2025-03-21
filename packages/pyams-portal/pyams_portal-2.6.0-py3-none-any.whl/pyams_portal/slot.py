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

"""PyAMS_portal.slot module

This module defines slots management components.
"""

from persistent import Persistent
from persistent.list import PersistentList
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from pyams_portal.interfaces import IPortalPage, IPortalTemplate, IPortalTemplateConfiguration, \
    ISlotConfiguration
from pyams_utils.factory import factory_config

__docformat__ = 'restructuredtext'

from pyams_utils.traversing import get_parent


DEVICES = ('xs', 'sm', 'md', 'lg', 'xl')


@factory_config(ISlotConfiguration)
class SlotConfiguration(Persistent, Contained):
    """Portal slot class"""

    slot_name = FieldProperty(ISlotConfiguration['slot_name'])
    _portlet_ids = FieldProperty(ISlotConfiguration['portlet_ids'])
    visible = FieldProperty(ISlotConfiguration['visible'])
    container_css_class = FieldProperty(ISlotConfiguration['container_css_class'])
    xs_width = FieldProperty(ISlotConfiguration['xs_width'])
    sm_width = FieldProperty(ISlotConfiguration['sm_width'])
    md_width = FieldProperty(ISlotConfiguration['md_width'])
    lg_width = FieldProperty(ISlotConfiguration['lg_width'])
    xl_width = FieldProperty(ISlotConfiguration['xl_width'])
    css_class = FieldProperty(ISlotConfiguration['css_class'])
    portlets_css_class = FieldProperty(ISlotConfiguration['portlets_css_class'])
    prefix = FieldProperty(ISlotConfiguration['prefix'])
    suffix = FieldProperty(ISlotConfiguration['suffix'])

    def __init__(self, slot_name, **kwargs):
        self.slot_name = slot_name
        self._portlet_ids = PersistentList()
        self.xs_width = 12
        self.sm_width = 12
        self.md_width = 12
        self.lg_width = 12
        self.xl_width = 12
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def template(self):
        """Template getter"""
        if IPortalTemplate.providedBy(self.__parent__):
            return self.__parent__
        return get_parent(self.__parent__, IPortalPage).template

    @property
    def portlet_ids(self):
        """Portlets IDs getter"""
        if IPortalTemplate.providedBy(self.__parent__):
            return self._portlet_ids
        config = IPortalTemplateConfiguration(self.template)
        return config.get_slot_configuration(self.slot_name).portlet_ids

    @portlet_ids.setter
    def portlet_ids(self, value):
        """Portlets IDs setter"""
        if IPortalTemplate.providedBy(self.__parent__):
            self._portlet_ids = value

    def get_css_class(self, device=None):
        """CSS class getter"""
        if not device:
            device = DEVICES
        elif isinstance(device, str):
            device = (device, )
        result = ['col', self.css_class or '']
        for attr in device:
            width = getattr(self, f'{attr}_width')
            result.append(f'col-{width}' if attr == 'xs' else f'col-{attr}-{width}')
        return ' '.join(result)

    def get_width(self, device=None):
        """Width getter"""
        if not device:
            device = DEVICES
        elif isinstance(device, str):
            device = (device, )
        result = {}
        for attr in device:
            result[attr] = getattr(self, f'{attr}_width')
        return result

    def set_width(self, width, device=None):
        """Width setter"""
        if not device:
            device = DEVICES
        elif isinstance(device, str):
            device = (device, )
        for attr in device:
            setattr(self, f'{attr}_width', width)
