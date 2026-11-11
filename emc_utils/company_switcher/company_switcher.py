"""Company switcher: let a user narrow Desk to some of the companies they may see.

Works on any ERPNext site with several companies, flat or in a group hierarchy
(Company > Parent Company, with Is Group ticked on the parents).

Two layers decide which company's records a user sees:

1. Access (set by an admin): the user's Company User Permissions. A permission on
   a group company covers the companies under it, as Frappe applies it. A user
   with no Company permission sees every company.
2. Scope (picked by the user in the switcher at the top left of Desk): a subset of
   the companies they have access to. Ticking a group ticks every company under
   it. Ticking everything shows everything; ticking fewer narrows company-owned
   lists and link searches to those companies.

The scope is stored as a user default, so it follows the user across devices.
The first company in the scope becomes the user's default company, so new
documents start in it.
"""

import json

import frappe
from frappe import _

from emc_utils.constants import PRINT_FORMAT_DOCTYPES, SCOPED_DOCTYPES

SCOPE_KEY = "company_switcher_scope"


def get_companies():
	"""Every company with its place in the group tree."""
	return frappe.get_all(
		"Company",
		fields=["name", "abbr", "company_logo", "parent_company", "is_group", "lft", "rgt"],
		order_by="lft asc",
		ignore_permissions=True,
	)


def get_allowed_companies(user=None):
	"""Trading (non-group) companies the user may see, in tree order."""
	from frappe.permissions import get_user_permissions

	user = user or frappe.session.user
	leaves = [row.name for row in get_companies() if not row.is_group]
	permissions = get_user_permissions(user).get("Company")
	if not permissions:
		return leaves
	permitted = {row.get("doc") for row in permissions}
	return [name for name in leaves if name in permitted]


def get_scope(user=None):
	"""Companies the user chose to see; all allowed companies when they never chose."""
	user = user or frappe.session.user
	allowed = get_allowed_companies(user)
	saved = frappe.defaults.get_user_default(SCOPE_KEY, user)
	try:
		chosen = set(json.loads(saved)) if saved else set()
	except (TypeError, ValueError):
		chosen = set()
	return [name for name in allowed if name in chosen] or allowed


@frappe.whitelist()
def get_switcher():
	"""What the switcher shows: allowed companies plus the groups above them, in tree order."""
	allowed = set(get_allowed_companies())
	companies = get_companies()
	by_name = {row.name: row for row in companies}

	visible = set(allowed)
	for name in allowed:
		parent = by_name[name].parent_company
		while parent and parent in by_name and parent not in visible:
			visible.add(parent)
			parent = by_name[parent].parent_company

	rows = []
	for row in companies:
		if row.name not in visible:
			continue
		depth, parent = 0, row.parent_company
		while parent and parent in visible:
			depth += 1
			parent = by_name[parent].parent_company
		rows.append(
			{
				"name": row.name,
				"abbr": row.abbr,
				"logo": row.company_logo,
				"parent": row.parent_company if row.parent_company in visible else None,
				"is_group": bool(row.is_group),
				"depth": depth,
			}
		)
	return {"companies": rows, "scope": get_scope()}


@frappe.whitelist()
def set_scope(companies):
	"""Save the user's chosen trading companies, picking the first as their default."""
	if isinstance(companies, str):
		try:
			companies = json.loads(companies)
		except (TypeError, ValueError):
			companies = [companies]

	chosen = set(companies or [])
	allowed = get_allowed_companies()
	valid = [name for name in allowed if name in chosen]

	if not valid:
		frappe.throw(_("Pick at least one company."))

	user = frappe.session.user
	frappe.defaults.set_user_default(SCOPE_KEY, json.dumps(valid), user)
	frappe.defaults.set_user_default("company", valid[0], user)
	return {"scope": valid}


def get_permission_query_conditions(user=None, doctype=None):
	"""Limit company-owned doctypes to the user's scope.

	Installed on doctypes that have a ``company`` Link field; leaves anything
	without one alone. When the scope matches every company the user may see,
	no extra WHERE clause is added, leaving Frappe's own permissions to do the
	work.
	"""
	if not doctype:
		return ""

	try:
		meta = frappe.get_meta(doctype)
		if not meta or not meta.has_field("company"):
			return ""
		df = meta.get_field("company")
		if not df or df.fieldtype != "Link" or df.options != "Company":
			return ""
	except Exception:
		return ""

	user = user or frappe.session.user
	allowed = get_allowed_companies(user)
	scope = get_scope(user)

	if set(scope) >= set(allowed):
		return ""

	quoted = ", ".join(frappe.db.escape(name) for name in scope)
	return f"`tab{doctype}`.`company` in ({quoted})"


def boot_session(bootinfo):
	"""Feed the switcher to Desk on page load and expose per-company print formats."""
	if frappe.session.user == "Guest":
		return

	allowed = get_allowed_companies()
	if len(allowed) <= 1:
		return

	bootinfo.company_switcher = get_switcher()

	bootinfo.company_print_formats = {}
	fields = ["name"] + list(PRINT_FORMAT_DOCTYPES.values())
	for row in frappe.get_all("Company", fields=fields):
		formats = {dt: row.get(fn) for dt, fn in PRINT_FORMAT_DOCTYPES.items() if row.get(fn)}
		if formats:
			bootinfo.company_print_formats[row.name] = formats
