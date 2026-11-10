import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

SUPPORTED_CHILD_DOCTYPES = [
    "Quotation Item",
    "Sales Order Item",
    "Sales Invoice Item",
    "Purchase Order Item",
    "Purchase Invoice Item",
    "Delivery Note Item",
    "Purchase Receipt Item",
]

def after_install():
    setup_custom_fields()
    setup_property_setters()

def after_migrate():
    setup_custom_fields()
    setup_property_setters()

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
    if custom_fields:
        create_custom_fields(custom_fields, update=True)

def setup_property_setters():
    for dt in SUPPORTED_CHILD_DOCTYPES:
        if frappe.db.exists("DocType", dt):
            meta = frappe.get_meta(dt)
            df = meta.get_field("item_code")
            if df and df.reqd:
                frappe.make_property_setter({
                    "doctype_or_field": "DocField",
                    "doctype": dt,
                    "field_name": "item_code",
                    "property": "reqd",
                    "value": "0",
                    "property_type": "Check",
                })
                frappe.make_property_setter({
                    "doctype_or_field": "DocField",
                    "doctype": dt,
                    "field_name": "item_code",
                    "property": "mandatory_depends_on",
                    "value": "eval:!doc.is_section",
                    "property_type": "Data",
                })
