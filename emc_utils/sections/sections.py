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

        orig_before_print = getattr(AccountsController, "before_print", None)
        if orig_before_print and not getattr(AccountsController, "_emc_utils_bp_patched", False):
            def emc_before_print(self, settings=None):
                if isinstance(settings, dict) and not isinstance(settings, frappe._dict):
                    settings = frappe._dict(settings)
                try:
                    return orig_before_print(self, settings)
                except AttributeError:
                    pass
            AccountsController.before_print = emc_before_print
            AccountsController._emc_utils_bp_patched = True

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

def extract_section_styles_from_css(css_str):
    """Extract section visual properties from child table custom CSS, supporting sec- and --sec-."""
    if not css_str:
        return {}
    import re
    props = {}
    mapping = {
        "bg": ["sec-bg", "--sec-bg"],
        "border": ["sec-border", "--sec-border"],
        "border_width": ["sec-border-width", "--sec-border-width"],
        "badge_bg": ["sec-badge-bg", "--sec-badge-bg"],
        "badge_color": ["sec-badge-color", "--sec-badge-color"],
        "badge_radius": ["sec-badge-radius", "--sec-badge-radius"],
        "badge_display": ["sec-badge-display", "--sec-badge-display", "sec-badge", "--sec-badge"],
        "no_display": [
            "sec-no-display", "--sec-no-display", "sec-no", "--sec-no",
            "sec-idx-display", "--sec-idx-display", "sec-idx", "--sec-idx",
            "sec-number-display", "--sec-number-display", "sec-number", "--sec-number",
        ],
        "title_color": ["sec-title-color", "--sec-title-color"],
        "title_size": ["sec-title-size", "--sec-title-size"],
        "title_weight": ["sec-title-weight", "--sec-title-weight"],
    }
    for key, patterns in mapping.items():
        for pat in patterns:
            m = re.search(rf"(?:^|[;\s]){re.escape(pat)}\s*:\s*([^;!\r\n]+)", css_str, re.IGNORECASE)
            if m:
                props[key] = m.group(1).strip()
                break
    return props

def generate_dynamic_section_css(props):
    """Generate scoped CSS rules from extracted custom style properties."""
    if not props:
        return ""
    rules = []
    bg = props.get("bg")
    border = props.get("border")
    badge_bg = props.get("badge_bg")
    badge_color = props.get("badge_color")
    badge_display = props.get("badge_display")
    no_display = props.get("no_display")
    title_color = props.get("title_color")
    title_size = props.get("title_size")
    title_weight = props.get("title_weight")

    if bg or border:
        selectors = (
            'tr.table-row:has([data-is-section="1"]), '
            'tr.table-row:has(.emc-print-section-header), '
            'tr.table-row.emc-print-section-row, '
            'tr.table-row:has([data-is-section="1"]) td, '
            'tr.table-row:has(.emc-print-section-header) td, '
            'tr.table-row.emc-print-section-row td'
        )
        decls = []
        if bg:
            decls.append(f"background-color: {bg} !important;")
        if border:
            decls.append(f"border-top-color: {border} !important; border-bottom-color: {border} !important;")
        rules.append(f"{selectors} {{ {' '.join(decls)} }}")

    if no_display:
        rules.append(
            'tr.table-row:has([data-is-section="1"]) td.column-value[data-fieldname="idx"], '
            'tr.table-row:has(.emc-print-section-header) td.column-value[data-fieldname="idx"], '
            f'tr.table-row.emc-print-section-row td.column-value[data-fieldname="idx"] {{ display: {no_display} !important; }}'
        )
        if no_display == "none":
            rules.append(
                'tr.table-row:has([data-is-section="1"]) td.column-value[data-fieldname="item_name"], '
                'tr.table-row:has(.emc-print-section-header) td.column-value[data-fieldname="item_name"], '
                'tr.table-row.emc-print-section-row td.column-value[data-fieldname="item_name"] { width: 100% !important; max-width: none !important; }'
            )

    b_decls = []
    if badge_bg:
        b_decls.append(f"background-color: {badge_bg} !important;")
    if badge_color:
        b_decls.append(f"color: {badge_color} !important;")
    if badge_display:
        b_decls.append(f"display: {badge_display} !important;")
    if b_decls:
        rules.append(f".emc-print-section-badge {{ {' '.join(b_decls)} }}")

    t_decls = []
    if title_color:
        t_decls.append(f"color: {title_color} !important;")
    if title_size:
        t_decls.append(f"font-size: {title_size} !important;")
    if title_weight:
        t_decls.append(f"font-weight: {title_weight} !important;")
    if t_decls:
        rules.append(f".emc-print-section-title {{ {' '.join(t_decls)} }}")

    return "\n".join(rules)

def before_print_sections(doc, method=None, print_settings=None):
    """Format section rows for print generation: add badge, bold title, and clean up empty cells."""
    if not hasattr(doc, "get"):
        return

    from types import MethodType
    import json
    import sys

    # Look for active PrintFormat document in the execution stack
    cur = sys._getframe()
    active_pf = None
    while cur:
        f_self = cur.f_locals.get("self")
        if f_self and hasattr(f_self, "print_format"):
            active_pf = getattr(f_self, "print_format")
            break
        if "print_format" in cur.f_locals:
            active_pf = cur.f_locals["print_format"]
            break
        cur = cur.f_back

    # Detect active Print Format's child table custom_style
    custom_style = ""
    if active_pf and getattr(active_pf, "format_data", None):
        try:
            fd = json.loads(active_pf.format_data)
            for sec in fd.get("sections", []):
                for col in sec.get("columns", []):
                    for fld in col.get("fields", []):
                        if fld.get("fieldname") == "items" or fld.get("fieldtype") == "Table":
                            custom_style = fld.get("custom_style") or ""
                            # Also ensure item_name fieldtype is HTML Editor so merged cells do not strip tags
                            for tcol in fld.get("table_columns", []):
                                if tcol.get("fieldname") == "item_name":
                                    tcol["fieldtype"] = "HTML Editor"
                            if custom_style:
                                break
                    if custom_style:
                        break
                if custom_style:
                    break
            active_pf.format_data = json.dumps(fd)
        except Exception:
            pass

    if not custom_style:
        format_name = (
            frappe.form_dict.get("print_format")
            or frappe.form_dict.get("format")
            or getattr(doc, "print_format", None)
            or (active_pf.name if active_pf and hasattr(active_pf, "name") else None)
        )
        if not format_name:
            format_name = frappe.db.get_value(
                "Property Setter",
                {"doc_type": doc.doctype, "property": "default_print_format"},
                "value",
            )

        if format_name and frappe.db.exists("Print Format", format_name):
            try:
                pf = frappe.get_doc("Print Format", format_name)
                if pf.format_data:
                    fd = json.loads(pf.format_data)
                    for sec in fd.get("sections", []):
                        for col in sec.get("columns", []):
                            for fld in col.get("fields", []):
                                if fld.get("fieldname") == "items" or fld.get("fieldtype") == "Table":
                                    custom_style = fld.get("custom_style") or ""
                                    if custom_style:
                                        break
                                if custom_style:
                                    break
                            if custom_style:
                                break
                        if custom_style:
                            break
            except Exception:
                pass

    if not custom_style:
        try:
            pfs = frappe.get_all(
                "Print Format",
                filters={"doc_type": doc.doctype, "print_format_builder_beta": 1, "disabled": 0},
                fields=["name", "format_data"],
                order_by="modified desc",
            )
            for p in pfs:
                if p.format_data:
                    fd = json.loads(p.format_data)
                    for sec in fd.get("sections", []):
                        for col in sec.get("columns", []):
                            for fld in col.get("fields", []):
                                if fld.get("fieldname") == "items" or fld.get("fieldtype") == "Table":
                                    cs = fld.get("custom_style") or ""
                                    if "sec-" in cs or "--sec-" in cs:
                                        custom_style = cs
                                        break
                                if custom_style:
                                    break
                            if custom_style:
                                break
                    if custom_style:
                        break
        except Exception:
            pass

    dynamic_css_rules = ""
    props = {}
    if custom_style:
        props = extract_section_styles_from_css(custom_style)
        dynamic_css_rules = generate_dynamic_section_css(props)

    if dynamic_css_rules and active_pf and hasattr(active_pf, "css"):
        active_pf.css = (active_pf.css or "") + "\n\n/* EMC Dynamic Section CSS */\n" + dynamic_css_rules

    hide_idx = (props.get("no_display") == "none") if props else False
    meta = frappe.get_meta(doc.doctype)
    first_section = True
    for tf in meta.get_table_fields():
        child_rows = doc.get(tf.fieldname) or []
        for row in child_rows:
            if getattr(row, "is_section", 0):
                title = (getattr(row, "section_title", None) or getattr(row, "item_name", "") or "Section").strip()

                # Override get_formatted on the section row to blank out non-title columns
                def make_custom_get_formatted(orig_fn, hide_no=False):
                    def custom_get_formatted(self, fieldname, *args, **kwargs):
                        allowed = ("item_name", "section_title") if hide_no else ("item_name", "section_title", "idx")
                        if fieldname not in allowed:
                            return ""
                        return orig_fn(fieldname, *args, **kwargs)
                    return custom_get_formatted

                row.get_formatted = MethodType(make_custom_get_formatted(row.get_formatted, hide_idx), row)

                if hasattr(row, "description"):
                    row.description = ""
                if hasattr(row, "item_code"):
                    row.item_code = ""
                if hasattr(row, "uom"):
                    row.uom = ""

                # Only include fallback style tag if active_pf could not receive the CSS in head
                style_prefix = ""
                if first_section and dynamic_css_rules and (not active_pf or not hasattr(active_pf, "css")):
                    style_prefix = f'<style id="emc-dynamic-section-css">\n{dynamic_css_rules}\n</style>'
                    first_section = False

                row.item_name = (
                    f'{style_prefix}'
                    f'<div class="emc-print-section-header" data-is-section="1">'
                    f'<span class="emc-print-section-badge">SECTION</span>'
                    f'<span class="emc-print-section-title">{frappe.utils.escape_html(title)}</span>'
                    f'</div>'
                )

def is_section_row(row):
    """Helper method for Jinja print templates."""
    return bool(getattr(row, "is_section", 0))
