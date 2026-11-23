import frappe
from frappe.model.document import Document

class EMCSettings(Document):
    pass

def get_emc_settings():
    """Helper to return EMC Settings doc or cached dictionary."""
    try:
        if frappe.db.exists("DocType", "EMC Settings"):
            return frappe.get_cached_doc("EMC Settings")
    except Exception:
        pass
    return None
