import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from emc_utils.constants import PRINT_FORMAT_DOCTYPES

def get_company_custom_fields():
    """Per-company default print formats, so each company's documents print with its own brand."""
    fields = [
        {"fieldname": "custom_print_branding_section", "fieldtype": "Section Break", "label": "Print Branding",
         "insert_after": "default_letter_head", "collapsible": 1},
        {"fieldname": "custom_print_logo", "fieldtype": "Attach", "label": "Print Logo",
         "insert_after": "custom_print_branding_section"},
        {"fieldname": "custom_brand_color", "fieldtype": "Color", "label": "Brand Color",
         "insert_after": "custom_print_logo"},
        {"fieldname": "custom_print_footer", "fieldtype": "Small Text", "label": "Print Footer",
         "insert_after": "custom_brand_color"},
        {
            "fieldname": "cs_print_formats_section",
            "fieldtype": "Section Break",
            "label": "Print Formats",
            "insert_after": "custom_print_footer",
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

PRINT_FORMAT_COMPANY = {
    "EMC Quotation Template - Master": "Eternal Media and Communication",
    "EMC Sales Order Template - Master": "Eternal Media and Communication",
    "ALT Quotation Template - Master": "Alter Styling and Decor",
    "ALT Sales Order Template - Master": "Alter Styling and Decor",
}


def setup_print_format_company():
    """Print formats show only for the companies they belong to (blank = all)."""
    create_custom_fields({"Print Format": [{
        "fieldname": "company",
        "fieldtype": "Link",
        "options": "Company",
        "label": "Company",
        "insert_after": "doc_type",
        "in_standard_filter": 1,
    }]}, update=True)
    for name, company in PRINT_FORMAT_COMPANY.items():
        if frappe.db.exists("Print Format", name) and frappe.db.exists("Company", company):
            frappe.db.set_value("Print Format", name, "company", company, update_modified=False)


def setup_custom_fields():
    if not frappe.db.exists("DocType", "Company"):
        return
    company_fields = get_company_custom_fields()
    create_custom_fields(company_fields, update=True)
    setup_print_format_company()
