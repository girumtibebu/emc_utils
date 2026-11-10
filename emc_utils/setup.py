import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from emc_utils.constants import PRINT_FORMAT_DOCTYPES

SUPPORTED_CHILD_DOCTYPES = [
    "Quotation Item",
    "Sales Order Item",
    "Sales Invoice Item",
    "Purchase Order Item",
    "Purchase Invoice Item",
    "Delivery Note Item",
    "Purchase Receipt Item",
]

SECTION_CONDITIONAL_MANDATORY_FIELDS = [
    "item_code",
    "uom",
    "qty",
    "conversion_factor",
]

def after_install():
    setup_custom_fields()
    setup_property_setters()

def after_migrate():
    setup_custom_fields()
    setup_property_setters()

def get_company_custom_fields():
    """Per-company default print formats, so each company's documents print with its own brand."""
    fields = [
        {
            "fieldname": "cs_print_formats_section",
            "fieldtype": "Section Break",
            "label": "Print Formats",
            "insert_after": "default_letter_head",
            "collapsible": 1,
            "description": "Used instead of the site-wide default when printing or emailing this company's documents.",
        }
    ]
    previous = "cs_print_formats_section"
    for doctype, fieldname in PRINT_FORMAT_DOCTYPES.items():
        fields.append(
            {
                "fieldname": fieldname,
                "fieldtype": "Link",
                "label": f"{doctype} Print Format",
                "options": "Print Format",
                "insert_after": previous,
            }
        )
        previous = fieldname
    return {"Company": fields}

def setup_custom_fields():
    custom_fields = {}
    for dt in SUPPORTED_CHILD_DOCTYPES:
        if frappe.db.exists("DocType", dt):
            custom_fields[dt] = [
                {
                    "fieldname": "is_section",
                    "label": "Is Section",
                    "fieldtype": "Check",
                    "default": "0",
                    "hidden": 1,
                    "no_copy": 0,
                    "insert_after": "idx",
                },
                {
                    "fieldname": "section_title",
                    "label": "Section Title",
                    "fieldtype": "Data",
                    "depends_on": "eval:doc.is_section==1",
                    "insert_after": "is_section",
                },
            ]

    # Add company print format fields
    company_fields = get_company_custom_fields()
    for dt, flds in company_fields.items():
        if frappe.db.exists("DocType", dt):
            custom_fields[dt] = flds

    if custom_fields:
        create_custom_fields(custom_fields, update=True)

def setup_property_setters():
    for dt in SUPPORTED_CHILD_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            continue

        meta = frappe.get_meta(dt)
        for fieldname in SECTION_CONDITIONAL_MANDATORY_FIELDS:
            df = meta.get_field(fieldname)
            if df and (df.reqd or df.mandatory_depends_on):
                frappe.make_property_setter({
                    "doctype_or_field": "DocField",
                    "doctype": dt,
                    "fieldname": fieldname,
                    "property": "reqd",
                    "value": "0",
                    "property_type": "Check",
                })
                frappe.make_property_setter({
                    "doctype_or_field": "DocField",
                    "doctype": dt,
                    "fieldname": fieldname,
                    "property": "mandatory_depends_on",
                    "value": "eval:!doc.is_section",
                    "property_type": "Data",
                })
