"""Per-deal company for Frappe CRM.

Frappe CRM has one site-wide ERPNext company. This adds a Company field on
CRM Deal and makes "Create Quotation" use it. Customers and Items stay shared,
as ERPNext keeps them for every company. The company switcher's "*" permission
rule scopes deal lists by this field without extra code.
"""

import json
from urllib.parse import parse_qsl, quote, urlencode

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

QUOTATION_URL_METHOD = "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.get_quotation_url"
LAYOUT_ANCHOR = "deal_owner"


def setup_custom_fields():
	if not frappe.db.exists("DocType", "CRM Deal"):
		return
	is_new = not frappe.db.exists("Custom Field", "CRM Deal-company")
	create_custom_fields(
		{
			"CRM Deal": [
				{
					"fieldname": "company",
					"fieldtype": "Link",
					"label": "Company",
					"options": "Company",
					"insert_after": "organization",
					"in_standard_filter": 1,
				}
			]
		},
		update=True,
	)
	# Only on first setup, so a field the user moves or removes in CRM stays that way.
	if is_new:
		add_to_layouts()


def add_to_layouts():
	for layout_name in frappe.get_all("CRM Fields Layout", filters={"dt": "CRM Deal"}, pluck="name"):
		doc = frappe.get_doc("CRM Fields Layout", layout_name)
		layout = json.loads(doc.layout or "[]")
		if _insert_before_anchor(layout):
			doc.layout = json.dumps(layout)
			doc.save(ignore_permissions=True)


def _insert_before_anchor(node):
	"""Put "company" before deal_owner in the first fields list that has it."""
	if isinstance(node, dict):
		fields = node.get("fields")
		if isinstance(fields, list) and LAYOUT_ANCHOR in fields and "company" not in fields:
			fields.insert(fields.index(LAYOUT_ANCHOR), "company")
			return True
		node = list(node.values())
	if isinstance(node, list):
		return any(_insert_before_anchor(child) for child in node)
	return False


def set_default_company(doc, method=None):
	"""New deals start in the user's default company (the first one in the switcher)."""
	if doc.get("company"):
		return
	doc.company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value(
		"ERPNext CRM Settings", "erpnext_company"
	)


@frappe.whitelist()
def get_quotation_url(crm_deal: str, organization: str | None = None):
	"""CRM's quotation link, with the deal's company instead of the site-wide one."""
	from crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings import (
		get_quotation_url as crm_get_quotation_url,
	)

	url = crm_get_quotation_url(crm_deal, organization)
	company = frappe.db.get_value("CRM Deal", crm_deal, "company")
	if not company:
		return url
	base, _, query = url.partition("?")
	params = dict(parse_qsl(query))
	params["company"] = company
	# quote (not quote_plus): Desk route options decode %20, not "+".
	return f"{base}?{urlencode(params, quote_via=quote)}"
