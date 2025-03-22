# -*- coding: UTF-8 -*-
# Copyright 2022-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
import base64
from pathlib import Path
from lxml import etree

from django.conf import settings
from django.utils import translation
from django.utils.html import mark_safe, escape

from lino.api import dd
from lino.utils.xml import validate_xml
from lino.utils.media import MediaFile


def xml_element(name, value):
    if value:
        return f"<{name}>{escape(str(value))}</{name}>"
    return ""


class XMLMaker(dd.Model):

    class Meta:
        abstract = True

    xml_validator_file = None
    xml_file_template = None
    # xml_file_name = None

    def get_xml_file_parts(self):
        yield 'xml'
        yield self.get_printable_target_stem() + ".xml"

    def make_xml_file(self, ar):
        renderer = settings.SITE.plugins.jinja.renderer
        tpl = renderer.jinja_env.get_template(self.xml_file_template)
        context = self.get_printable_context(ar)
        context.update(xml_element=xml_element)
        context.update(base64=base64)
        xml = tpl.render(**context)
        # parts = [
        #     dd.plugins.accounting.xml_media_dir,
        #     self.xml_file_name.format(self=self)]
        xmlfile = MediaFile(False, *self.get_xml_file_parts())
        # xmlfile = Path(settings.MEDIA_ROOT, *parts)
        ar.logger.info("Make %s from %s ...", xmlfile.path, self)
        xmlfile.path.parent.mkdir(exist_ok=True, parents=True)
        xmlfile.path.write_text(xml)
        # xmlfile.write_text(etree.tostring(xml))

        if self.xml_validator_file:
            # print("20250218 {xml[:100]}")
            # doc = etree.fromstring(xml.encode("utf-8"))
            # ar.logger.info("Validate %s against %s ...",
            #                xmlfile.path.name, self.xml_validator_file)
            if True:
                validate_xml(xmlfile.path, self.xml_validator_file)
            else:
                try:
                    validate_xml(xmlfile.path, self.xml_validator_file)
                except Exception as e:
                    msg = _("XML validation failed: {}").format(e)
                    # print(msg)
                    raise Warning(msg)

        # url = settings.SITE.build_media_url(*parts)
        # return mark_safe(f"""<a href="{url}">{url}</a>""")
        # return (xmlfile, url)
        return xmlfile
