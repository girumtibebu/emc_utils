import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from emc_utils.constants import PRINT_FORMAT_DOCTYPES

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
    if not frappe.db.exists("DocType", "Company"):
        return
    company_fields = get_company_custom_fields()
    create_custom_fields(company_fields, update=True)
