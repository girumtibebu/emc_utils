"""Per-company leads and deals for Frappe CRM.

Frappe CRM has one site-wide ERPNext company. This adds a Company field on
CRM Lead and CRM Deal:

- A user with access to one company always gets it.
- A user with several companies gets the first company picked in the switcher
  (Frappe fills it from their default company) and can change it on the record.
- Web forms and email intake get the site's default company, as Frappe's global
  default fills it before any hook runs.

Lead conversion copies same-named fields, so the deal keeps the lead's company.
"Create Quotation" uses the deal's company. The company switcher's "*" permission
rule scopes lead and deal lists by this field, and a list script puts the switcher
on the CRM Leads and Deals pages.
"""

import json
from urllib.parse import parse_qsl, quote, urlencode

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from emc_utils.company_switcher.company_switcher import get_scope

QUOTATION_URL_METHOD = "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.get_quotation_url"
# The company field goes just before the owner field in each CRM layout.
LAYOUT_ANCHORS = {"CRM Lead": "lead_owner", "CRM Deal": "deal_owner"}
LIST_SCRIPT_NAME = "Company Switcher - {}"

LIST_SCRIPT = """function setupList({ call }) {
	const method = "emc_utils.company_switcher.company_switcher."
	return call(method + "get_switcher").then(({ companies, scope }) => {
		const leaves = companies.filter((c) => !c.is_group).map((c) => c.name)
		if (leaves.length < 2) return {}
		const pick = (names) => call(method + "set_scope", { companies: JSON.stringify(names) })
			.then(() => window.location.reload())
		const all = scope.length === leaves.length
		const mark = (on) => (on ? "\\u2713 " : "\\u2003")
		return {
			actions: [{
				group: "Company",
				buttonLabel: all ? __("All companies") : scope.length === 1 ? scope[0] : __("{0} companies", [scope.length]),
				items: [
					{ label: mark(all) + __("All companies"), onClick: () => pick(leaves) },
					...leaves.map((name) => ({
						label: mark(!all && scope.includes(name)) + name,
						onClick: () => pick([name]),
					})),
				],
			}],
		}
	})
}
"""


def setup_custom_fields():
	for doctype in LAYOUT_ANCHORS:
		if not frappe.db.exists("DocType", doctype):
			continue
		is_new = not frappe.db.exists("Custom Field", f"{doctype}-company")
		create_custom_fields(
			{
				doctype: [
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
			add_to_layouts(doctype)
		setup_list_script(doctype)


def add_to_layouts(doctype):
	anchor = LAYOUT_ANCHORS[doctype]
	for layout_name in frappe.get_all("CRM Fields Layout", filters={"dt": doctype}, pluck="name"):
		doc = frappe.get_doc("CRM Fields Layout", layout_name)
		layout = json.loads(doc.layout or "[]")
		if _insert_before_anchor(layout, anchor):
			doc.layout = json.dumps(layout)
			doc.save(ignore_permissions=True)


def _insert_before_anchor(node, anchor):
	"""Put "company" before the anchor in the first fields list that has it."""
	if isinstance(node, dict):
		fields = node.get("fields")
		if isinstance(fields, list) and anchor in fields and "company" not in fields:
			fields.insert(fields.index(anchor), "company")
			return True
		node = list(node.values())
	if isinstance(node, list):
		return any(_insert_before_anchor(child, anchor) for child in node)
	return False


def setup_list_script(doctype):
	if not frappe.db.exists("DocType", "CRM Form Script"):
		return
	name = LIST_SCRIPT_NAME.format(doctype)
	if frappe.db.exists("CRM Form Script", name):
		frappe.db.set_value("CRM Form Script", name, "script", LIST_SCRIPT)
		return
	frappe.get_doc(
		{
			"doctype": "CRM Form Script",
			"name": name,
			"dt": doctype,
			"view": "List",
			"enabled": 1,
			"script": LIST_SCRIPT,
		}
	).insert(ignore_permissions=True)


def set_company(doc, method=None):
	"""Tag a new lead or deal with the company the user works in."""
	# Frappe already set the user's default company when they have one; this covers
	# users whose only company is not the site default (Frappe skips a disallowed default).
	if doc.get("company") or frappe.session.user == "Guest":
		return
	scope = get_scope()
	if scope:
		doc.company = scope[0]


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
	base, _sep, query = url.partition("?")
	params = dict(parse_qsl(query))
	params["company"] = company
	# quote (not quote_plus): Desk route options decode %20, not "+".
	return f"{base}?{urlencode(params, quote_via=quote)}"
