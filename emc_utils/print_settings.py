import json
import frappe
from frappe.utils import flt
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

HR_SEPARATOR_HTML = '<hr style="margin: 14px 0 14px 0; border: 0; border-top: 1px solid var(--border-color);">'

PRINT_CUSTOM_FIELDS = {
    "Quotation": [
        {
            "fieldname": "print_options_sep_1",
            "fieldtype": "HTML",
            "options": HR_SEPARATOR_HTML,
            "insert_after": "group_same_items",
        },
        {
            "fieldname": "print_show_section_subtotals",
            "label": "Show Section Subtotals",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_options_sep_1",
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
            "fieldname": "print_options_sep_2",
            "fieldtype": "HTML",
            "options": HR_SEPARATOR_HTML,
            "insert_after": "language",
        },
        {
            "fieldname": "print_hide_qty",
            "label": "Hide Quantity Column",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_options_sep_2",
        },
        {
            "fieldname": "print_without_vat",
            "label": "Print Without VAT",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_hide_qty",
        },
        {
            "fieldname": "print_payment_terms",
            "label": "Print Payment Terms",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_without_vat",
        },
        {
            "fieldname": "print_terms",
            "label": "Print Terms and Conditions",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_payment_terms",
        },
    ],
    "Sales Order": [
        {
            "fieldname": "print_options_sep_1",
            "fieldtype": "HTML",
            "options": HR_SEPARATOR_HTML,
            "insert_after": "group_same_items",
        },
        {
            "fieldname": "print_show_section_subtotals",
            "label": "Show Section Subtotals",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_options_sep_1",
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
            "fieldname": "print_options_sep_2",
            "fieldtype": "HTML",
            "options": HR_SEPARATOR_HTML,
            "insert_after": "language",
        },
        {
            "fieldname": "print_hide_qty",
            "label": "Hide Quantity Column",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_options_sep_2",
        },
        {
            "fieldname": "print_without_vat",
            "label": "Print Without VAT",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "print_hide_qty",
        },
        {
            "fieldname": "print_payment_terms",
            "label": "Print Payment Terms",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_without_vat",
        },
        {
            "fieldname": "print_terms",
            "label": "Print Terms and Conditions",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "print_payment_terms",
        },
    ],
}

def update_doctype_field_order(doctype, fields_to_insert_after):
    """If a field_order property setter exists (from Customize Form), synchronize field positions."""
    ps_name = frappe.db.get_value("Property Setter", {"doc_type": doctype, "property": "field_order"}, "name")
    if not ps_name:
        return
    try:
        ps = frappe.get_doc("Property Setter", ps_name)
        order = json.loads(ps.value)

        all_our_fields = set()
        for flist in fields_to_insert_after.values():
            all_our_fields.update(flist)
        order = [f for f in order if f not in all_our_fields]

        for target_field, new_fields in fields_to_insert_after.items():
            if target_field in order:
                idx = order.index(target_field) + 1
                for f in reversed(new_fields):
                    order.insert(idx, f)
            else:
                order.extend(new_fields)

        # Ensure any missing standard fields (e.g. utm_analytics_section on Sales Order) do not jump in before custom fields
        meta = frappe.get_meta(doctype)
        std_fields = [f.fieldname for f in meta.fields if not getattr(f, "is_custom_field", False)]
        missing = [f for f in std_fields if f not in order]
        if "utm_analytics_section" in missing and "print_without_vat" in order:
            idx = order.index("print_without_vat") + 1
            utm_group = [f for f in ["utm_analytics_section", "utm_source", "utm_medium", "column_break_ijxt", "utm_campaign", "utm_content"] if f in missing]
            for f in reversed(utm_group):
                order.insert(idx, f)

        ps.value = json.dumps(order)
        ps.save(ignore_permissions=True)
    except Exception:
        pass

def setup_print_custom_fields():
    # 1. Clean up obsolete custom fields from earlier versions
    obsolete_fields = [
        "Quotation-print_settings_section",
        "Sales Order-print_settings_section",
        "Quotation-print_options_col_break",
        "Sales Order-print_options_col_break",
    ]
    for field_name in obsolete_fields:
        if frappe.db.exists("Custom Field", field_name):
            try:
                frappe.db.delete("Custom Field", {"name": field_name})
            except Exception:
                pass

    # 2. Create / update fields inside standard Print Settings section
    create_custom_fields(PRINT_CUSTOM_FIELDS, update=True)

    # 3. Synchronize with field_order Property Setter if present (created via Customize Form)
    spec = {
        "group_same_items": [
            "print_options_sep_1",
            "print_show_section_subtotals",
            "print_show_number_of_days",
            "print_show_number_of_pages",
        ],
        "language": [
            "print_options_sep_2",
            "print_hide_qty",
            "print_without_vat",
            "print_payment_terms",
            "print_terms",
        ],
    }
    for dt in ["Quotation", "Sales Order"]:
        update_doctype_field_order(dt, spec)
        frappe.clear_cache(doctype=dt)

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

    # 7. Print Payment Terms (default on so existing docs keep showing them)
    if doc.get("print_payment_terms") is not None:
        print_payment_terms = bool(doc.get("print_payment_terms"))
    else:
        print_payment_terms = True

    # 8. Print Terms and Conditions (default on)
    if doc.get("print_terms") is not None:
        print_terms = bool(doc.get("print_terms"))
    else:
        print_terms = True

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
        "print_payment_terms": print_payment_terms,
        "print_terms": print_terms,
        "total_columns": cols,
        "title_colspan": cols - 1,
        "subtotal_label_colspan": cols - 2,
    }
