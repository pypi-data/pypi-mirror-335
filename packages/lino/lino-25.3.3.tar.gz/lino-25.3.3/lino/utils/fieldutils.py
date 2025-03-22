# -*- coding: UTF-8 -*-
# Copyright 2009-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.boundaction import BoundAction
from lino.core.actions import Action
from django.db.models import Model
from lino.core.tables import AbstractTable
from lino.core.layouts import BaseLayout
from lino.core.actions import register_params
from rstgen.utils import unindent
import rstgen


def get_fields(model, fieldnames=None, columns=None):
    """Return a list of field in the given database model, action or table.     
    """
    if isinstance(model, BoundAction):
        get_field = model.action.parameters.get
        if fieldnames is None:
            fieldnames = model.action.params_layout
    elif isinstance(model, Action):
        get_field = model.parameters.get
        if fieldnames is None:
            fieldnames = model.params_layout.main
    elif issubclass(model, Model):
        get_field = model._meta.get_field
        # get_field = model.get_data_elem
        if fieldnames is None:
            fieldnames = [f.name for f in model._meta.get_fields()]
    elif issubclass(model, AbstractTable):
        if columns:
            get_field = model.get_data_elem
            if fieldnames is None:
                fieldnames = model.column_names
                # get_handle().grid_layout.main.columns
        else:
            get_field = model.parameters.get
            if fieldnames is None:
                if not isinstance(model.params_layout, BaseLayout):
                    register_params(model)
                fieldnames = model.params_layout.main
    if fieldnames is None:
        return
    if isinstance(fieldnames, str):
        fieldnames = fieldnames.split()
    for n in fieldnames:
        yield get_field(n)


def fields_help(model, fieldnames=None, columns=False, all=None):
    """
    Print an overview description of the specified fields of the
    specified model.

    If model is an action or table, print the parameter fields of that
    action or table.

    If model is a table and you want the columns instead of the
    parameter fields, then specify `columns=True`.

    By default this shows only fields that have a help text.  If you
    specify `all=True`, then also fields that have no help text will
    be shown.
    """
    if all is None:
        all = fieldnames is not None

    cells = []
    # cols = ["Internal name", "Verbose name", "Help text"]
    for fld in get_fields(model, fieldnames, columns):
        if fld is not None and hasattr(fld, "verbose_name"):
            ht = fld.help_text or ""
            if ht or all:
                cells.append([fld.name, fld.verbose_name, unindent(ht)])

    # return table(cols, cells).strip()
    items = ["{} ({}) : {}".format(row[1], row[0], row[2]) for row in cells]
    return rstgen.ul(items).strip()
