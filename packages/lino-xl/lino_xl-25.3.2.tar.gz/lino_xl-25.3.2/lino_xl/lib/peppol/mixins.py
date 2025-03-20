# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Developer docs: https://dev.lino-framework.org/plugins/peppol.html

from django.db import models
from lino.api import dd, _


class PeppolJournal(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed('peppol'):
        is_outbound = dd.BooleanField(_("Send via Peppol"), default=False)
    else:
        is_outbound = dd.DummyField()


class PeppolPartner(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed('peppol'):
        is_outbound = dd.BooleanField(_("Send via Peppol"), default=False)
        peppol_id = models.CharField(_("Peppol ID"), max_length=50, blank=True)
    else:
        is_outbound = dd.DummyField()
        peppol_id = dd.DummyField()
