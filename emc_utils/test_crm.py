from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from emc_utils import crm


def _doc():
	return frappe._dict(doctype="CRM Lead", company=None)


class TestCRMCompany(IntegrationTestCase):
	def test_layout_insert_before_owner_once(self):
		layout = [{"columns": [{"fields": ["organization"]}, {"fields": ["territory", "deal_owner"]}]}]
		self.assertTrue(crm._insert_before_anchor(layout, "deal_owner"))
		self.assertEqual(layout[0]["columns"][1]["fields"], ["territory", "company", "deal_owner"])
		self.assertFalse(crm._insert_before_anchor(layout, "deal_owner"))

	def test_layout_without_anchor_untouched(self):
		layout = [{"columns": [{"fields": ["organization"]}]}]
		self.assertFalse(crm._insert_before_anchor(layout, "lead_owner"))

	def test_blank_company_gets_first_scoped_company(self):
		doc = _doc()
		with patch.object(crm, "get_scope", return_value=["Alter Decor", "B"]):
			crm.set_company(doc)
		self.assertEqual(doc.company, "Alter Decor")

	def test_chosen_company_is_kept(self):
		doc = _doc()
		doc.company = "B"
		with patch.object(crm, "get_scope", return_value=["A", "B"]):
			crm.set_company(doc)
		self.assertEqual(doc.company, "B")

	def test_quotation_url_uses_deal_company(self):
		original = "http://x/desk/quotation/new?quotation_to=CRM Deal&crm_deal=D-1&company=Site Co"
		with (
			patch(
				"crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.get_quotation_url",
				return_value=original,
			),
			patch.object(frappe.db, "get_value", return_value="Alter Decor"),
		):
			url = crm.get_quotation_url("D-1")
		self.assertIn("company=Alter%20Decor", url)
		self.assertIn("quotation_to=CRM%20Deal", url)
		self.assertNotIn("Site", url)
