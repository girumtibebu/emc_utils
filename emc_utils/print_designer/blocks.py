"""Taxes, payment terms and terms blocks for the EMC quotation print formats.

Each block prints only when its Quotation check box is on, through the print
builder's "visible_if" condition. add_print_blocks adds the blocks a layout lacks
and keeps the rest of the layout (and the user's edits) as it is.
"""

import copy

# The check boxes are created in emc_utils/print_settings.py.
TAXES_VISIBLE = "not doc.print_without_vat"
PAYMENT_VISIBLE = "doc.print_payment_terms and doc.payment_schedule"
TERMS_VISIBLE = "doc.print_terms and doc.terms"

TAXES_REPEATER = {
	"label": "",
	"fieldname": "repeater",
	"fieldtype": "Repeater",
	"source": "taxes",
	"repeater_columns": [
		{"template": [{"t": "f", "v": "description"}], "align": "left", "width": 60, "color": "#6b7280"},
		{"template": [{"t": "f", "v": "tax_amount"}], "align": "right", "width": 40, "color": "#1f2328"},
	],
	"row_condition": "print_settings.print_taxes_with_zero_amount or row.tax_amount != 0",
	"custom_style": "",
}

IN_WORDS_SECTION = {
	"label": "",
	"columns": [{"label": "", "fields": [{"label": "In Words", "fieldname": "in_words", "fieldtype": "Data", "show_label": "hide"}]}],
	"background": "#f8f8f8",
	"padding": {"top": 5, "right": 12, "bottom": 5, "left": 12},
	"margin": {"top": 10, "right": 0, "bottom": 0, "left": 0},
}

PAYMENT_SECTION = {
	"label": "",
	"has_fields": True,
	"margin": {"top": 15, "right": 12, "bottom": 0, "left": 12},
	"columns": [
		{
			"label": "",
			"fields": [
				{
					"label": "Payment Terms",
					"fieldname": "payment_schedule",
					"fieldtype": "Table",
					"options": "Payment Schedule",
					"table_columns": [
						# the print drops a column that is empty in every row, so either may vanish
						{"label": "Payment Term", "fieldname": "payment_term", "fieldtype": "Link", "options": "Payment Term", "width": 20},
						{"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 25},
						{"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 18},
						{"label": "Portion (%)", "fieldname": "invoice_portion", "fieldtype": "Percent", "width": 12},
						{"label": "Amount", "fieldname": "payment_amount", "fieldtype": "Currency", "options": "currency", "width": 25},
					],
					"table_bordered": False,
					"table_header": "styled",
					"table_cell_padding": 8,
					"table_radius": 8,
					"table_header_bg": "#f3f3f3",
					"table_border_color": "#f3f3f3",
				}
			],
		}
	],
}

TERMS_SECTION = {
	"label": "",
	"margin": {"top": 15, "right": 12, "bottom": 0, "left": 12},
	"columns": [{"label": "", "fields": [{"label": "Terms and Conditions", "fieldname": "terms", "fieldtype": "Text Editor"}]}],
}


def add_print_blocks(layout):
	"""Add the taxes, in-words, payment-terms and terms blocks a layout lacks."""
	sections = layout.setdefault("sections", [])
	_add_taxes(sections)
	anchor = _index_of(sections, "in_words")
	if anchor is None:
		anchor = _insert_after(sections, _index_of(sections, "grand_total"), IN_WORDS_SECTION)
	if _index_of(sections, "payment_schedule") is None:
		_insert_after(sections, anchor, PAYMENT_SECTION)
	if _index_of(sections, "terms") is None:
		sections.append(copy.deepcopy(TERMS_SECTION))

	# shortcut: the toggles own visible_if on these fields, so a condition typed in the builder is replaced on migrate.
	for field in _fields(sections):
		if field.get("fieldtype") == "Repeater" and field.get("source") == "taxes":
			field["visible_if"] = TAXES_VISIBLE
		elif field.get("fieldname") == "payment_schedule":
			field["visible_if"] = PAYMENT_VISIBLE
		elif field.get("fieldname") == "terms":
			field["visible_if"] = TERMS_VISIBLE
	return layout


def _add_taxes(sections):
	if any(f.get("fieldtype") == "Repeater" and f.get("source") == "taxes" for f in _fields(sections)):
		return
	for section in sections:
		for column in section.get("columns", []):
			names = [f.get("fieldname") for f in column.get("fields", [])]
			if "grand_total" in names:
				column["fields"].insert(names.index("grand_total"), copy.deepcopy(TAXES_REPEATER))
				return


def _insert_after(sections, index, section):
	index = len(sections) - 1 if index is None else index
	sections.insert(index + 1, copy.deepcopy(section))
	return index + 1


def _index_of(sections, fieldname):
	for i, section in enumerate(sections):
		if any(f.get("fieldname") == fieldname for c in section.get("columns", []) for f in c.get("fields", [])):
			return i
	return None


def _fields(sections):
	return [f for s in sections for c in s.get("columns", []) for f in c.get("fields", [])]
