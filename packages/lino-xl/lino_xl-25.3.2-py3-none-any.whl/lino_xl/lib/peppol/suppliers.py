# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Developer docs: https://dev.lino-framework.org/plugins/peppol.html

# from datetime import datetime
from dateutil.parser import isoparse

from django.utils import timezone
from django.conf import settings
from django.db import models
from lino.api import dd, rt, _
from lino import logger
from lino.mixins import Contactable, Phonable
from lino.modlib.checkdata.choicelists import Checker
# from lino.mixins.periods import DateRange
from lino_xl.lib.accounting.roles import LedgerStaff
from lino_xl.lib.accounting.choicelists import VoucherStates
# from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.countries.mixins import AddressLocation
from lino_xl.lib.vat.choicelists import VatSubjectable

# TODO: move babelfilter to lino core.utils.mldbc


def babelfilter(name, value, **kwargs):
    flt = models.Q()
    for k, v in dd.str2kw(name, value).items():
        flt |= models.Q(**{k: v})
    if kwargs:
        flt &= models.Q(**kwargs)
    return flt


with_suppliers = dd.get_plugin_setting("peppol", "with_suppliers", False)
# outbound_model = dd.get_plugin_setting("peppol", "outbound_model", None)
# inbound_model = dd.get_plugin_setting("peppol", "inbound_model", None)
# supplier_id = dd.get_plugin_setting("peppol", "supplier_id", None)

peppol = dd.plugins.peppol


class OnboardingStates(dd.ChoiceList):
    verbose_name = _("Onboarding state")
    verbose_name_plural = _("Onboarding states")
    required_roles = dd.login_required(LedgerStaff)


add = OnboardingStates.add_item
add('10', _("Draft"), 'draft')
add('20', _("Created"), 'created')
add('30', _("Approved"), 'approved')
add('40', _("Rejected"), 'rejected')
add('50', _("Onboarded"), 'onboarded')
add('60', _("Offboarded"), 'offboarded')

# add('10', _("Active"), 'active')
# add('20', _("Potential"), 'potential')
# add('30', _("Unreachable"), 'unreachable')


# class Supplier(AddressLocation, ContactRelated, Contactable, Phonable):
class Supplier(AddressLocation, Contactable, Phonable):

    class Meta:
        app_label = 'peppol'
        verbose_name = _("Ibanity supplier")
        verbose_name_plural = _("Ibanity suppliers")

    # preferred_foreignkey_width = 10

    supplier_id = models.CharField(_("Supplier ID"), max_length=50, blank=True)
    company = dd.ForeignKey(
        "contacts.Company",
        related_name="peppol_suppliers_by_company",
        verbose_name=_("Organization"),
        blank=True, null=True)
    names = models.CharField(_('Names'), max_length=200, blank=True)
    ibans = models.CharField(_('IBANs'), max_length=200, blank=True)
    vat_id = models.CharField(_("VAT id"), max_length=200, blank=True)
    onboarding_state = OnboardingStates.field(default='draft')
    peppol_receiver = models.BooleanField(_("Peppol receiver"), default=False)
    last_sync = models.DateTimeField(_("Last sync"), editable=False, null=True)

    @classmethod
    def get_simple_parameters(cls):
        yield super().get_simple_parameters()
        yield "onboarding_state"

    def create_supplier_data(self):
        d = {}
        d["enterpriseIdentification"] = {
            # "enterpriseNumber": "1234567890",
            "vatNumber": self.vat_id}
        d["contactEmail"] = self.email
        d["names"] = [{"value": name} for name in self.names.split(";")]

        if self.company_id:
            d["ibans"] = [{"value": "BE68539007547034"},
                          {"value": "BE68539007547034"}]
        d["city"] = str(self.city)
        d["country"] = str(self.country)
        d["email"] = self.email
        d["homepage"] = self.url
        d["phoneNumber"] = self.phone
        d["street"] = self.street
        d["streetNumber"] = self.street_no
        d["supportEmail"] = "support@example.be"
        d["supportPhone"] = "+3212345121"
        d["supportUrl"] = "www.support.com"
        d["zip"] = self.zip_code
        d["peppolReceiver"] = self.peppol_receiver
        return d


class SupplierDetail(dd.DetailLayout):
    main = """
    supplier_id company id
    vat_id names
    peppol_receiver onboarding_state last_sync
    ibans
    country region city
    zip_code street street_no
    checkdata.MessagesByOwner
    """


class Suppliers(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = "peppol.Supplier"
    column_names = "supplier_id names vat_id onboarding_state last_sync *"
    insert_layout = """
    company
    supplier_id
    """
    detail_layout = "peppol.SupplierDetail"


class SuppliersListChecker(Checker):
    verbose_name = _("Check for missing or invalid suppliers")
    model = None

    def get_checkdata_problems(self, obj, fix=False):
        if not peppol.credentials:
            logger.info("No Ibanity credentials")
            return

        existing = [o.supplier_id for o in
                    Supplier.objects.exclude(supplier_id='')]

        ses = peppol.get_ibanity_session()
        for sup_info in ses.list_suppliers()['data']:
            if sup_info['type'] != "supplier":
                logger.info("Invalid supplier type '%s'", sup_info['type'])
                continue
            sup_id = sup_info['id']
            if sup_id in existing:
                existing.remove(sup_id)
                continue
            else:
                yield True, _("No entry for {sup_id}.").format(sup_id=sup_id)
                if fix:
                    sup = Supplier(supplier_id=sup_id)
                    sup.full_clean()
                    sup.save()
                    rt.models.checkdata.check_instance(sup, fix=True)
        for sup_id in existing:
            yield False, _("Supplier {} doesn't exist on Ibanity.").format(sup_id)


# if peppol.credentials:
SuppliersListChecker.activate(no_auto=True)


class SupplierChecker(Checker):
    verbose_name = _("Check for differences between our copy and Ibanity")
    model = Supplier
    msg_needs_update = _("Some fields need update: {changed}")

    def get_checkdata_problems(self, obj, fix=False):

        if not peppol.credentials:
            logger.info("No Ibanity credentials")
            return

        Country = rt.models.countries.Country
        Place = rt.models.countries.Place

        def save():
            obj.last_sync = timezone.now()
            obj.full_clean()
            obj.save()

        ses = peppol.get_ibanity_session()

        if obj.supplier_id:
            sup_info = ses.get_supplier(obj.supplier_id)
            sup_id = sup_info['data']['id']
            if sup_id != obj.supplier_id:
                yield False, _("Supplier {} doesn't exist on Ibanity.").format(sup_id)
                save()
                return
        elif not obj.company_id:
            yield True, _("Dangling supplier row should get deleted")
            if fix:
                obj.delete()
            return
        if obj.company and not (obj.names and obj.vat_id):
            yield True, _("Must fill supplier from company")
            if fix:
                obj.vat_id = obj.company.vat_id
                obj.names = obj.company.name
                save()
            else:
                return
        if not obj.supplier_id:
            yield True, _("Must create supplier on Ibanity")
            if fix:
                data = obj.create_supplier_data()
                sup_info = ses.create_supplier(**data)
                sup_id = sup_info['data']['id']
                obj.supplier_id = sup_id
                save()
            else:
                return
        # Synchronize sup_info with our data
        a = sup_info['data']['attributes']
        f2v = dict(
            vat_id=a['enterpriseIdentification']['vatNumber'],
            street=a['street'],
            street_no=a['streetNumber'],
            phone=a['phoneNumber'],
            email=a['email'],
            # url = a['homepage'], # sandbox homepage is invalid for Django
            zip_code=a['zip'],
        )
        f2v['peppol_receiver'] = a['peppolReceiver']
        f2v['names'] = "; ".join([i['value'] for i in a['names']])
        f2v['ibans'] = "; ".join([i['value'] for i in a['ibans']])
        f2v["onboarding_state"] = OnboardingStates.get_by_name(
            a['onboardingStatus'].lower())

        try:
            country = Country.objects.get(babelfilter('name', a['country']))
        except Country.DoesNotExist:
            yield (False, _("Unknown country {country}").format(**a))
        else:
            f2v['country'] = country

        try:
            city = Place.objects.get(
                babelfilter('name', a['city'], country=country))
        except Place.DoesNotExist:
            yield (True, _("Unknown city {city} ((in {country})").format(**a))
            if fix:
                city = Place(name=a['city'], country=country)
                city.full_clean()
                city.save()
                f2v['city'] = city
        else:
            f2v['city'] = city

        changed = []
        for k, v in f2v.items():
            if getattr(obj, k) != v:
                changed.append(k)
        changed.sort()

        if len(changed):
            msg = self.msg_needs_update.format(changed=", ".join(changed))
            yield (True, msg)
            if fix:
                for k in changed:
                    setattr(obj, k, f2v[k])

        if obj.company:
            ctx = dict(
                vn=rt.models.contacts.Company._meta.verbose_name, obj=obj)
            if obj.company.name not in obj.names:
                msg = _("{vn} name {obj.company.name} missing in supplier names")
                yield (False, msg.format(**ctx))
            if obj.company.vat_id != obj.vat_id:
                msg = _("{vn} VAT id {obj.company.vat_id} ≠ {obj.vat_id}")
                yield (False, msg.format(**ctx))

        # We call save() even when there are no changes because we want
        # last_sync to reflect each online check.
        save()

# On a site without Ibanity credentials we don't need to activate this
# checker. SupplierChecker.activate() sets no_auto to True because we do not
# want this checker to run automatically (i.e. during checkdata). It should
# run only when called manually because it requires Ibanity credentials,
# which are not available e.g. on GitLab.


# if peppol.credentials:
SupplierChecker.activate(no_auto=True)
