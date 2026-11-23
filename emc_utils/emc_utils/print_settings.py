import frappe
from frappe.utils import flt
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

PRINT_CUSTOM_FIELDS = {
    "Quotation": [
        {
            "fieldname": "print_settings_section",
            "label": "Print Options",
            "fieldtype": "Section Break",
            "collapsible": 1,
            "insert_after": "terms",
        },
        {
            "fieldname": "print_show_section_subtotals",
            "label": "Show Section Subtotals",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_settings_section",
        },
        {
            "fieldname": "print_show_number_of_days",
            "label": "Show No. of Days Column",
            "description": "Auto-detected from items if left unchecked",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_show_section_subtotals",
        },
        {
            "fieldname": "print_show_number_of_pages",
            "label": "Show Pages Column",
            "description": "Auto-detected from items if left unchecked",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_show_number_of_days",
        },
        {
            "fieldname": "print_options_col_break",
            "fieldtype": "Column Break",
            "insert_after": "print_show_number_of_pages",
        },
        {
            "fieldname": "print_hide_qty",
            "label": "Hide Quantity Column",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_options_col_break",
        },
        {
            "fieldname": "print_without_vat",
            "label": "Print Without VAT",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_hide_qty",
        },
    ],
    "Sales Order": [
        {
            "fieldname": "print_settings_section",
            "label": "Print Options",
            "fieldtype": "Section Break",
            "collapsible": 1,
            "insert_after": "terms",
        },
        {
            "fieldname": "print_show_section_subtotals",
            "label": "Show Section Subtotals",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_settings_section",
        },
        {
            "fieldname": "print_show_number_of_days",
            "label": "Show No. of Days Column",
            "description": "Auto-detected from items if left unchecked",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_show_section_subtotals",
        },
        {
            "fieldname": "print_show_number_of_pages",
            "label": "Show Pages Column",
            "description": "Auto-detected from items if left unchecked",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_show_number_of_days",
        },
        {
            "fieldname": "print_options_col_break",
            "fieldtype": "Column Break",
            "insert_after": "print_show_number_of_pages",
        },
        {
            "fieldname": "print_hide_qty",
            "label": "Hide Quantity Column",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_options_col_break",
        },
        {
            "fieldname": "print_without_vat",
            "label": "Print Without VAT",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_hide_qty",
        },
    ],
}

def setup_print_custom_fields():
    create_custom_fields(PRINT_CUSTOM_FIELDS, update=True)

def get_print_context(doc):
    """Computes dynamic print visibility flags, column counts and colspans for a document."""
    settings = None
    try:
        if frappe.db.exists("DocType", "EMC Settings"):
            settings = frappe.get_cached_doc("EMC Settings")
    except Exception:
        settings = None

    # 1. Show subtotals
    if doc.get("print_show_section_subtotals") is not None:
        show_subtotals = bool(doc.get("print_show_section_subtotals"))
    elif settings:
        show_subtotals = bool(getattr(settings, "show_section_subtotals", 1))
    else:
        show_subtotals = True

    # 2. Check items for days and pages
    items = doc.get("items") or []
    has_days = any(flt(getattr(r, "number_of_days", 0)) > 0 for r in items)
    has_pages = any(flt(getattr(r, "number_of_pages", 0)) > 0 for r in items)

    # 3. Days column
    if doc.get("print_show_number_of_days"):
        show_days = True
    elif settings and getattr(settings, "default_show_days", 0):
        show_days = True
    elif (settings and getattr(settings, "auto_detect_columns", 1)) or settings is None:
        show_days = has_days
    else:
        show_days = False

    # 4. Pages column
    if doc.get("print_show_number_of_pages"):
        show_pages = True
    elif settings and getattr(settings, "default_show_pages", 0):
        show_pages = True
    elif (settings and getattr(settings, "auto_detect_columns", 1)) or settings is None:
        show_pages = has_pages
    else:
        show_pages = False

    # 5. Hide Qty
    if doc.get("print_hide_qty") is not None and doc.get("print_hide_qty"):
        hide_qty = True
    elif settings and getattr(settings, "default_hide_qty", 0):
        hide_qty = True
    else:
        hide_qty = False

    # 6. Without VAT
    if doc.get("print_without_vat") is not None and doc.get("print_without_vat"):
        without_vat = True
    elif settings and getattr(settings, "default_without_vat", 0):
        without_vat = True
    else:
        without_vat = False

    # Calculate total columns
    # Base columns: No (1), Item (1), Description (1), Rate (1), Amount (1) = 5
    cols = 5
    if not hide_qty:
        cols += 1
    if show_days:
        cols += 1
    if show_pages:
        cols += 1

    return {
        "show_subtotals": show_subtotals,
        "show_days": show_days,
        "show_pages": show_pages,
        "hide_qty": hide_qty,
        "without_vat": without_vat,
        "total_columns": cols,
        "title_colspan": cols - 1,
        "subtotal_label_colspan": cols - 2,
    }
