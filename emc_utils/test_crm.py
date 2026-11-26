from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from emc_utils import crm


class TestCRMCompany(IntegrationTestCase):
	def test_layout_insert_before_deal_owner_once(self):
		layout = [{"columns": [{"fields": ["organization"]}, {"fields": ["territory", "deal_owner"]}]}]
		self.assertTrue(crm._insert_before_anchor(layout))
		self.assertEqual(layout[0]["columns"][1]["fields"], ["territory", "company", "deal_owner"])
		self.assertFalse(crm._insert_before_anchor(layout))

	def test_layout_without_anchor_untouched(self):
		layout = [{"columns": [{"fields": ["organization"]}]}]
		self.assertFalse(crm._insert_before_anchor(layout))

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
