import os
import frappe

import os
import json
import frappe

def setup_sample_print_formats():
    """Install or update sample print formats with section support for Print Format Designer."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_name = "EMC Utils" if frappe.db.exists("Module Def", "EMC Utils") else "Selling"

    css_path = os.path.join(current_dir, "quotation_sections.css")
    custom_css = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            custom_css = f.read()

    formats = [
        {
            "name": "Quotation with Sections",
            "file": "quotation_sections.json",
            "css": custom_css,
        },
        {
            "name": "Quotation Modern with Sections",
            "file": "quotation_modern_sections.json",
            "css": custom_css,
            "margin_top": 15.0,
            "margin_bottom": 8.0,
            "margin_left": 8.0,
            "margin_right": 8.0,
            "page_number": "Hide",
        },
    ]

    for fmt in formats:
        json_file_path = os.path.join(current_dir, fmt["file"])
        if not os.path.exists(json_file_path):
            continue

        with open(json_file_path, "r", encoding="utf-8") as f:
            disk_format_data = f.read()

        pf_name = fmt["name"]
        if frappe.db.exists("Print Format", pf_name):
            pf = frappe.get_doc("Print Format", pf_name)
            # If doc exists and user has customized custom_style on items, preserve it
            if pf.format_data:
                try:
                    db_fd = json.loads(pf.format_data)
                    disk_fd = json.loads(disk_format_data)

                    # Extract existing custom_style
                    existing_cs = None
                    for s in db_fd.get("sections", []):
                        for c in s.get("columns", []):
                            for fld in c.get("fields", []):
                                if fld.get("fieldname") == "items" and fld.get("custom_style"):
                                    existing_cs = fld.get("custom_style")
                                    break

                    # Update disk_fd's enhancer to ensure latest JavaScript & CSS are active
                    enhancer_html = None
                    for s in disk_fd.get("sections", []):
                        for c in s.get("columns", []):
                            for fld in c.get("fields", []):
                                if fld.get("fieldname") == "custom_html_enhancer":
                                    enhancer_html = fld.get("html")
                                    break

                    if enhancer_html:
                        for s in db_fd.get("sections", []):
                            for c in s.get("columns", []):
                                for fld in c.get("fields", []):
                                    if fld.get("fieldname") == "custom_html_enhancer":
                                        fld["html"] = enhancer_html

                    # Keep existing custom_style if user entered something
                    if existing_cs:
                        for s in db_fd.get("sections", []):
                            for c in s.get("columns", []):
                                for fld in c.get("fields", []):
                                    if fld.get("fieldname") == "items":
                                        fld["custom_style"] = existing_cs

                    format_data_to_save = json.dumps(db_fd)
                except Exception:
                    format_data_to_save = disk_format_data
            else:
                format_data_to_save = disk_format_data
        else:
            pf = frappe.new_doc("Print Format")
            pf.name = pf_name
            format_data_to_save = disk_format_data

        pf.doc_type = "Quotation"
        pf.module = module_name
        pf.standard = "No"  # Allows direct visual editing in Print Format Designer
        pf.custom_format = 0
        pf.html = None
        pf.raw_commands = None
        pf.print_format_builder_beta = 1
        pf.format_data = format_data_to_save
        pf.css = fmt.get("css", "")

        for attr in ("margin_top", "margin_bottom", "margin_left", "margin_right", "page_number"):
            if attr in fmt:
                setattr(pf, attr, fmt[attr])

        pf.save(ignore_permissions=True)

    frappe.db.commit()
