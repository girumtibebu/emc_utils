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
        "total_display": [
            "sec-total-display", "--sec-total-display",
            "sec-total", "--sec-total",
            "sec-price-display", "--sec-price-display",
            "sec-price", "--sec-price",
        ],
        "total_pos": [
            "sec-total-position", "--sec-total-position",
            "sec-total-pos", "--sec-total-pos",
            "sec-price-position", "--sec-price-position",
            "sec-price-pos", "--sec-price-pos",
        ],
        "total_color": ["sec-total-color", "--sec-total-color", "sec-price-color", "--sec-price-color"],
        "total_bg": ["sec-total-bg", "--sec-total-bg", "sec-price-bg", "--sec-price-bg"],
        "total_size": ["sec-total-size", "--sec-total-size", "sec-price-size", "--sec-price-size"],
        "total_weight": ["sec-total-weight", "--sec-total-weight", "sec-price-weight", "--sec-price-weight"],
        "total_label_display": [
            "sec-total-label-display", "--sec-total-label-display",
            "sec-total-label", "--sec-total-label",
        ],
        "subtotal_bg": ["sec-subtotal-bg", "--sec-subtotal-bg"],
        "subtotal_color": ["sec-subtotal-color", "--sec-subtotal-color"],
        "subtotal_border": ["sec-subtotal-border", "--sec-subtotal-border"],
        "subtotal_size": ["sec-subtotal-size", "--sec-subtotal-size"],
        "subtotal_weight": ["sec-subtotal-weight", "--sec-subtotal-weight"],
    }
    for key, patterns in mapping.items():
        for pat in patterns:
            m = re.search(rf"(?:^|[;\s]){re.escape(pat)}\s*:\s*([^;!\r\n]+)", css_str, re.IGNORECASE)
            if m:
                props[key] = m.group(1).strip()
                break
    return props

def generate_dynamic_section_css(props=None):
    """Generate complete, robust CSS rules for section rows based on props with safe defaults."""
    props = props or {}

    bg = props.get("bg") or "#f8fafc"
    border = props.get("border") or "#cbd5e1"
    border_width = props.get("border_width") or "1.5px"
    badge_bg = props.get("badge_bg") or "#0f172a"
    badge_color = props.get("badge_color") or "#ffffff"
    badge_size = props.get("badge_size") or "8.5px"
    badge_radius = props.get("badge_radius") or "4px"
    badge_display = props.get("badge_display") or "inline-block"
    no_display = props.get("no_display") or "table-cell"
    title_color = props.get("title_color") or "#0f172a"
    title_size = props.get("title_size") or "13.5px"
    title_weight = props.get("title_weight") or "700"
    title_transform = props.get("title_transform") or "none"

    total_pos = (props.get("total_pos") or "header").strip().lower()
    total_display_raw = (props.get("total_display") or "").strip().lower()

    if total_display_raw in ("none", "hide", "hidden", "0", "false") or total_pos in ("none", "hide", "hidden"):
        total_display = "none"
        subtotal_display = "none"
    elif total_pos in ("bottom", "footer", "separate", "row", "end"):
        total_display = "none"
        subtotal_display = "table-row"
    elif total_pos == "both":
        total_display = "inline-flex"
        subtotal_display = "table-row"
    else:  # header (default)
        total_display = "inline-flex"
        subtotal_display = "none"

    total_label_raw = (props.get("total_label_display") or "").strip().lower()
    if total_label_raw in ("none", "hide", "hidden", "0", "false"):
        total_label_display = "none"
    else:
        total_label_display = "inline"

    total_color = props.get("total_color") or title_color
    total_size = props.get("total_size") or "12.5px"
    total_weight = props.get("total_weight") or "600"
    total_bg = props.get("total_bg") or "transparent"
    total_radius = props.get("total_radius") or "4px"
    total_padding = "2px 7px" if total_bg != "transparent" else "0"

    subtotal_bg = props.get("subtotal_bg") or bg
    subtotal_color = props.get("subtotal_color") or title_color
    subtotal_border = props.get("subtotal_border") or border
    subtotal_size = props.get("subtotal_size") or "12.5px"
    subtotal_weight = props.get("subtotal_weight") or "700"

    title_cell_width = "100%" if no_display == "none" else "95%"

    rules = [
        f""":root, html, body, .print-format, .child-table, tr.table-row, tr.table-row td {{
    --sec-bg: {bg} !important;
    --sec-border: {border} !important;
    --sec-border-width: {border_width} !important;
    --sec-border-top: {border_width} solid {border} !important;
    --sec-border-bottom: {border_width} solid {border} !important;
    --sec-badge-bg: {badge_bg} !important;
    --sec-badge-color: {badge_color} !important;
    --sec-badge-size: {badge_size} !important;
    --sec-badge-radius: {badge_radius} !important;
    --sec-badge-display: {badge_display} !important;
    --sec-no-display: {no_display} !important;
    --sec-idx-display: {no_display} !important;
    --sec-title-color: {title_color} !important;
    --sec-title-size: {title_size} !important;
    --sec-title-weight: {title_weight} !important;
    --sec-title-transform: {title_transform} !important;
    --sec-title-cell-width: {title_cell_width} !important;
    --sec-total-position: {total_pos} !important;
    --sec-total-display: {total_display} !important;
    --sec-total-label-display: {total_label_display} !important;
    --sec-total-color: {total_color} !important;
    --sec-total-size: {total_size} !important;
    --sec-total-weight: {total_weight} !important;
    --sec-total-bg: {total_bg} !important;
    --sec-total-padding: {total_padding} !important;
    --sec-total-radius: {total_radius} !important;
    --sec-subtotal-display: {subtotal_display} !important;
    --sec-subtotal-bg: {subtotal_bg} !important;
    --sec-subtotal-color: {subtotal_color} !important;
    --sec-subtotal-border: {subtotal_border} !important;
    --sec-subtotal-size: {subtotal_size} !important;
    --sec-subtotal-weight: {subtotal_weight} !important;
}}""",

        f"""tr.table-row:has([data-is-section="1"]),
tr.table-row:has(.emc-print-section-header),
tr.table-row.emc-print-section-row {{
    background-color: {bg} !important;
    font-weight: {title_weight} !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

tr.table-row:has([data-is-section="1"]) td,
tr.table-row:has(.emc-print-section-header) td,
tr.table-row.emc-print-section-row td {{
    background-color: {bg} !important;
    border-top: {border_width} solid {border} !important;
    border-bottom: {border_width} solid {border} !important;
    font-weight: {title_weight} !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}""",

        """tr.table-row:has([data-is-section="1"]) td.column-value:not([data-fieldname="item_name"]):not([data-fieldname="section_title"]):not([data-fieldname="idx"]),
tr.table-row:has(.emc-print-section-header) td.column-value:not([data-fieldname="item_name"]):not([data-fieldname="section_title"]):not([data-fieldname="idx"]),
tr.table-row.emc-print-section-row td.column-value:not([data-fieldname="item_name"]):not([data-fieldname="section_title"]):not([data-fieldname="idx"]) {
    display: none !important;
}""",

        f"""tr.table-row:has([data-is-section="1"]) td.column-value[data-fieldname="idx"],
tr.table-row:has(.emc-print-section-header) td.column-value[data-fieldname="idx"],
tr.table-row.emc-print-section-row td.column-value[data-fieldname="idx"] {{
    display: {no_display} !important;
}}

tr.table-row:has([data-is-section="1"]) td.column-value[data-fieldname="item_name"],
tr.table-row:has(.emc-print-section-header) td.column-value[data-fieldname="item_name"],
tr.table-row.emc-print-section-row td.column-value[data-fieldname="item_name"] {{
    width: {title_cell_width} !important;
    max-width: none !important;
}}""",

        f""".emc-print-section-header {{
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    box-sizing: border-box !important;
    gap: 12px !important;
    padding: 2px 0 !important;
}}

.emc-print-section-main {{
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}}

.emc-print-section-badge {{
    background-color: {badge_bg} !important;
    color: {badge_color} !important;
    font-size: {badge_size} !important;
    font-weight: 700 !important;
    padding: 2px 7px !important;
    border-radius: {badge_radius} !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    display: {badge_display} !important;
    flex-shrink: 0 !important;
    white-space: nowrap !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

.emc-print-section-title {{
    font-size: {title_size} !important;
    font-weight: {title_weight} !important;
    color: {title_color} !important;
    text-transform: {title_transform} !important;
    letter-spacing: 0.01em !important;
    display: inline-block !important;
}}

.emc-print-section-total {{
    display: {total_display} !important;
    align-items: center !important;
    gap: 5px !important;
    font-size: {total_size} !important;
    font-weight: {total_weight} !important;
    color: {total_color} !important;
    background-color: {total_bg} !important;
    padding: {total_padding} !important;
    border-radius: {total_radius} !important;
    white-space: nowrap !important;
    margin-left: auto !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

.emc-print-section-total-label {{
    display: {total_label_display} !important;
    font-size: 0.9em !important;
    opacity: 0.8 !important;
    font-weight: 500 !important;
}}

.emc-print-section-total-amount {{
    font-weight: {total_weight} !important;
    font-variant-numeric: tabular-nums !important;
}}

tr.table-row:has([data-is-section-subtotal="1"]),
tr.table-row.emc-print-section-subtotal-row {{
    display: {subtotal_display} !important;
    background-color: {subtotal_bg} !important;
    font-weight: {subtotal_weight} !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

tr.table-row:has([data-is-section-subtotal="1"]) td,
tr.table-row.emc-print-section-subtotal-row td {{
    background-color: {subtotal_bg} !important;
    border-top: 1px dashed {subtotal_border} !important;
    border-bottom: 1.5px solid {subtotal_border} !important;
    font-weight: {subtotal_weight} !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

tr.table-row:has([data-is-section-subtotal="1"]) td.column-value:not([data-fieldname="item_name"]),
tr.table-row.emc-print-section-subtotal-row td.column-value:not([data-fieldname="item_name"]) {{
    display: none !important;
}}

tr.table-row:has([data-is-section-subtotal="1"]) td.column-value[data-fieldname="item_name"],
tr.table-row.emc-print-section-subtotal-row td.column-value[data-fieldname="item_name"] {{
    width: 100% !important;
    max-width: none !important;
}}

.emc-print-section-subtotal-header {{
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 3px 0 !important;
    gap: 12px !important;
    color: {subtotal_color} !important;
    font-size: {subtotal_size} !important;
}}

.emc-print-section-subtotal-label {{
    font-weight: {subtotal_weight} !important;
    letter-spacing: 0.01em !important;
}}

.emc-print-section-subtotal-amount {{
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums !important;
}}

tr.table-row:has([data-is-section="1"]) .cell-line--muted-sm,
tr.table-row.emc-print-section-row .cell-line--muted-sm {{
    display: none !important;
}}"""
    ]

    return "\n\n".join(rules)

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
                        # Strip obsolete conflicting <style> tag from custom_html_enhancer
                        if fld.get("fieldname") == "custom_html_enhancer":
                            h = fld.get("html") or ""
                            if "<style" in h:
                                fld["html"] = re.sub(r"<style[\s\S]*?</style>\s*", "", h)
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

    props = extract_section_styles_from_css(custom_style) if custom_style else {}
    dynamic_css_rules = generate_dynamic_section_css(props)

    if active_pf and hasattr(active_pf, "css"):
        if "/* EMC Dynamic Section CSS */" in (active_pf.css or ""):
            active_pf.css = active_pf.css.split("/* EMC Dynamic Section CSS */")[0]
        active_pf.css = (active_pf.css or "") + "\n\n/* EMC Dynamic Section CSS */\n" + dynamic_css_rules

    import copy
    hide_idx = (props.get("no_display") == "none") if props else False
    meta = frappe.get_meta(doc.doctype)
    first_section = True
    for tf in meta.get_table_fields():
        child_rows = doc.get(tf.fieldname) or []
        if not child_rows:
            continue

        # Precalculate section totals (sum of item.amount until the next section)
        current_section = None
        section_totals = {}
        for row in child_rows:
            if getattr(row, "is_section", 0):
                current_section = row
                section_totals[id(row)] = 0.0
            elif current_section is not None:
                section_totals[id(current_section)] += flt(getattr(row, "amount", 0))

        # Build list of child rows with injected subtotal summary rows
        new_child_rows = []
        cur_sec = None
        for row in child_rows:
            if getattr(row, "is_section", 0):
                if cur_sec is not None:
                    tot = section_totals.get(id(cur_sec), 0.0)
                    formatted_total = frappe.format_value(tot, {"fieldtype": "Currency"}, doc=doc)
                    sec_title = (getattr(cur_sec, "section_title", None) or getattr(cur_sec, "item_name", "") or "Section").strip()
                    sub_label = f"Subtotal ({sec_title}):"

                    sub_row = copy.copy(cur_sec)
                    sub_row.is_section = 0
                    sub_row.is_section_subtotal = 1
                    sub_row.idx = None

                    def make_subtotal_get_formatted(lbl, val):
                        def custom_get_formatted(self, fieldname, *args, **kwargs):
                            if fieldname == "item_name":
                                return (
                                    f'<div class="emc-print-section-subtotal-header" data-is-section-subtotal="1">'
                                    f'<span class="emc-print-section-subtotal-label">{lbl}</span>'
                                    f'<span class="emc-print-section-subtotal-amount">{val}</span>'
                                    f'</div>'
                                )
                            return ""
                        return custom_get_formatted

                    sub_row.get_formatted = MethodType(make_subtotal_get_formatted(sub_label, formatted_total), sub_row)
                    new_child_rows.append(sub_row)

                cur_sec = row

            new_child_rows.append(row)

        if cur_sec is not None:
            tot = section_totals.get(id(cur_sec), 0.0)
            formatted_total = frappe.format_value(tot, {"fieldtype": "Currency"}, doc=doc)
            sec_title = (getattr(cur_sec, "section_title", None) or getattr(cur_sec, "item_name", "") or "Section").strip()
            sub_label = f"Subtotal ({sec_title}):"

            sub_row = copy.copy(cur_sec)
            sub_row.is_section = 0
            sub_row.is_section_subtotal = 1
            sub_row.idx = None

            def make_subtotal_get_formatted(lbl, val):
                def custom_get_formatted(self, fieldname, *args, **kwargs):
                    if fieldname == "item_name":
                        return (
                            f'<div class="emc-print-section-subtotal-header" data-is-section-subtotal="1">'
                            f'<span class="emc-print-section-subtotal-label">{lbl}</span>'
                            f'<span class="emc-print-section-subtotal-amount">{val}</span>'
                            f'</div>'
                        )
                    return ""
                return custom_get_formatted

            sub_row.get_formatted = MethodType(make_subtotal_get_formatted(sub_label, formatted_total), sub_row)
            new_child_rows.append(sub_row)

        doc.set(tf.fieldname, new_child_rows)

        for row in new_child_rows:
            if getattr(row, "is_section", 0):
                title = (getattr(row, "section_title", None) or getattr(row, "item_name", "") or "Section").strip()
                tot = section_totals.get(id(row), 0.0)
                formatted_total = frappe.format_value(tot, {"fieldtype": "Currency"}, doc=doc)

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

                # Injected dynamic style tag directly inside the first section row ensures
                # that table-level and row-level CSS rules always override any layout wrappers
                style_prefix = ""
                if first_section and dynamic_css_rules:
                    style_prefix = f'<style id="emc-dynamic-section-css">\n{dynamic_css_rules}\n</style>'
                    first_section = False

                row.item_name = (
                    f'{style_prefix}'
                    f'<div class="emc-print-section-header" data-is-section="1">'
                    f'<div class="emc-print-section-main">'
                    f'<span class="emc-print-section-badge">SECTION</span>'
                    f'<span class="emc-print-section-title">{frappe.utils.escape_html(title)}</span>'
                    f'</div>'
                    f'<div class="emc-print-section-total">'
                    f'<span class="emc-print-section-total-label">Section Total:</span>'
                    f'<span class="emc-print-section-total-amount">{frappe.utils.escape_html(formatted_total)}</span>'
                    f'</div>'
                    f'</div>'
                )

def is_section_row(row):
    """Helper method for Jinja print templates."""
    return bool(getattr(row, "is_section", 0))
