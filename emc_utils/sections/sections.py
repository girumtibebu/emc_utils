import frappe
from frappe.utils import flt
from frappe.model.document import Document

def patch_all():
    patch_document_mandatory()
    patch_accounts_controller()

def patch_document_mandatory():
    if getattr(Document, "_emc_utils_mandatory_patched", False):
        return

    orig_get_missing_mandatory_fields = Document._get_missing_mandatory_fields

    def emc_get_missing_mandatory_fields(self):
        if getattr(self, "is_section", 0):
            return []
        return orig_get_missing_mandatory_fields(self)

    Document._get_missing_mandatory_fields = emc_get_missing_mandatory_fields
    Document._emc_utils_mandatory_patched = True

def patch_accounts_controller():
    try:
        from erpnext.controllers.accounts_controller import AccountsController
        if getattr(AccountsController, "_emc_utils_patched", False):
            return

        orig_validate_qty = AccountsController.validate_qty_is_not_zero

        def emc_validate_qty_is_not_zero(self):
            if self.flags.allow_zero_qty:
                return

            for item in self.items:
                if getattr(item, "is_section", 0):
                    continue
                if self.doctype == "Purchase Receipt" and item.rejected_qty:
                    continue

                if not flt(item.qty):
                    from erpnext.controllers.accounts_controller import InvalidQtyError
                    frappe.throw(
                        msg=frappe._("Row #{0}: Quantity for Item {1} cannot be zero.").format(
                            item.idx, frappe.bold(item.item_code)
                        ),
                        title=frappe._("Invalid Quantity"),
                        exc=InvalidQtyError,
                    )

        AccountsController.validate_qty_is_not_zero = emc_validate_qty_is_not_zero
        AccountsController._emc_utils_patched = True
    except ImportError:
        pass

# Initialize patches immediately
patch_all()

def boot_session(bootinfo):
    patch_all()
    try:
        from emc_utils.company_switcher import boot_session as company_boot_session
        company_boot_session(bootinfo)
    except Exception:
        pass

def before_validate_sections(doc, method=None):
    """Ensure safe defaults, zero amounts, and sync titles for section rows."""
    patch_all()

    meta = frappe.get_meta(doc.doctype)
    table_fields = meta.get_table_fields()

    for tf in table_fields:
        child_rows = doc.get(tf.fieldname) or []
        for row in child_rows:
            if getattr(row, "is_section", 0):
                # Ensure harmless UOM & conversion factor so standard validations never complain
                if hasattr(row, "uom") and not row.uom:
                    row.uom = "Unit"
                if hasattr(row, "conversion_factor") and not row.conversion_factor:
                    row.conversion_factor = 1.0

                # Sync section title to description and item_name
                title = (getattr(row, "section_title", None) or getattr(row, "item_name", "") or "").strip()
                if title:
                    row.section_title = title
                    if hasattr(row, "item_name"):
                        row.item_name = title
                    if hasattr(row, "description"):
                        row.description = title

                # Zero out financials and inventory fields to prevent skewing totals
                for num_field in (
                    "qty", "rate", "amount", "net_amount", "base_amount",
                    "base_net_amount", "stock_qty", "price_list_rate", "discount_percentage"
                ):
                    if hasattr(row, num_field):
                        setattr(row, num_field, 0)

def before_print_sections(doc, method=None, print_settings=None):
    """Format section rows for print generation: add badge, bold title, and clean up empty cells."""
    if not hasattr(doc, "get"):
        return

    meta = frappe.get_meta(doc.doctype)
    for tf in meta.get_table_fields():
        child_rows = doc.get(tf.fieldname) or []
        for row in child_rows:
            if getattr(row, "is_section", 0):
                title = (getattr(row, "section_title", None) or getattr(row, "item_name", "") or "Section").strip()
                row.item_name = (
                    f'<div class="emc-print-section-header" data-is-section="1">'
                    f'<span class="emc-print-section-badge">SECTION</span>'
                    f'<span class="emc-print-section-title">{frappe.utils.escape_html(title)}</span>'
                    f'</div>'
                )
                if hasattr(row, "description"):
                    row.description = ""
                if hasattr(row, "item_code"):
                    row.item_code = ""
                if hasattr(row, "uom"):
                    row.uom = ""

def is_section_row(row):
    """Helper method for Jinja print templates."""
    return bool(getattr(row, "is_section", 0))
