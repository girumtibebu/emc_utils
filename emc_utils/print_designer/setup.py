import os
import frappe

def setup_sample_print_formats():
    """Install or update the modern sectioned print format for Print Format Designer."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "quotation_sections.json")
    css_path = os.path.join(current_dir, "quotation_sections.css")

    if not os.path.exists(json_path) or not os.path.exists(css_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        format_data = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()

    pf_name = "Quotation with Sections"
    if frappe.db.exists("Print Format", pf_name):
        pf = frappe.get_doc("Print Format", pf_name)
    else:
        pf = frappe.new_doc("Print Format")
        pf.name = pf_name

    pf.doc_type = "Quotation"
    pf.module = "EMC Utils" if frappe.db.exists("Module Def", "EMC Utils") else "Selling"
    pf.standard = "No"  # Allows direct visual editing in Print Format Designer
    pf.custom_format = 0
    pf.print_format_builder_beta = 1
    pf.format_data = format_data
    pf.css = custom_css
    pf.save(ignore_permissions=True)
