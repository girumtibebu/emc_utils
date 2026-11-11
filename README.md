# EMC Utilities (`emc_utils`)

[![Frappe Framework](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15%20%7C%20v16-brightgreen.svg)](https://erpnext.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](license.txt)

A modular, upgrade-safe utility app for **Frappe Framework & ERPNext (v15 / v16)** designed to replace fragmented client and server scripts with clean, domain-isolated modules:

1. **Universal Child Table Sections:** Add clean, draggable visual section dividers and headings directly inside transactional child tables (Quotations, Sales Orders, Invoices, Purchase Orders) with Espresso UI badges, full-width inputs, and financial zeroing.
2. **Company Switcher & Multi-Company Scoping:** Filter Desk lists and link searches across multiple companies using a sidebar toggle menu, with support for flat and nested company hierarchies.
3. **Per-Company Default Print Formats:** Configure brand-specific print templates on each Company record without mutating site-wide defaults.
4. **Frappe v16 Print Format Designer Integration:** 4 standard sample formats (`Quotation with Sections`, `Quotation with Section Subtotals`, `Quotation Modern with Sections`, `Quotation Modern with Subtotals`) pre-configured for Frappe v16's visual Print Format Designer (`print_format_builder_beta: 1`), featuring full-row section highlights, automatic pre-VAT subtotal calculation, suppression of zero amounts/rates/quantities, and an editable Custom CSS panel.

---

## Modular Architecture

`emc_utils` organizes every feature into self-contained sub-domains. Each domain owns its backend Python logic, database setup, client-side JavaScript, and CSS styles:

```text
emc_utils/
│
├── company_switcher/               # 🏢 Company Switcher & Multi-Company Scoping Domain
│   ├── __init__.py                 # Public domain exports
│   ├── company_switcher.py        # Tree traversal, user scope resolution, and query filter conditions
│   ├── setup.py                   # Custom field definitions for Company DocType
│   ├── company_switcher.js        # Desk sidebar toggle menu UI
│   └── company_switcher.css       # Sidebar header styling
│
├── sections/                       # 📑 Universal Child Table Sections Domain
│   ├── __init__.py                 # Public domain exports
│   ├── sections.py                # Server-side validation bypass, zeroing logic, before_print hook
│   ├── setup.py                   # Custom fields (is_section, section_title) & Property Setters
│   ├── sections.js                # Core DOM controller, grid row formatter, and keyboard handlers
│   ├── quotation.js               # Quotation form script hook & save-before-print interception
│   ├── sales_order.js             # Sales Order form script hook & save-before-print interception
│   └── sections.css               # High-contrast Espresso badges, section rows, and inputs
│
├── print_designer/                 # 🖨️ Frappe v16 Print Format Designer Integration
│   ├── __init__.py                 # Public domain exports
│   ├── setup.py                   # Automated installer/updater for standard sample print formats
│   ├── quotation_sections.json    # Visual designer format_data layout
│   └── quotation_sections.css     # Section print styling exposed in designer's Custom CSS panel
│
├── public/                         # 🌐 Bundled Frappe Asset Pipeline (/assets/emc_utils/...)
│   ├── js/                        # sections.js, company_switcher.js, quotation.js, sales_order.js
│   └── css/                       # sections.css, company_switcher.css, emc_utils.css
│
├── constants.py                    # Shared DocType lists and field name mappings
├── hooks.py                        # Frappe app configuration, asset bundle links, doc_events
└── setup.py                        # Root setup orchestrator (executes sub-domain setup routines)
```

---

## Feature 1: Universal Child Table Sections

Organize complex bill-of-materials and multi-phase quotations into clean visual sections (e.g. *Phase 1: Civil Works*, *Phase 2: Hardware Delivery*, *Optional Services*).

### Key Highlights
- **Native Espresso UI:** Styled with Frappe v16 design tokens, solid gray pill badges (`.es-badge`), and full-width inline input fields.
- **Zero Financial / Stock Impact:** Quantities, rates, amounts, net totals, and stock quantities on section rows are strictly zeroed out automatically on the client and validated on the server.
- **Save-on-Print Protection:** Switching to Print Preview or pressing `Ctrl+P` on an unsaved quote automatically triggers `frm.save()`, ensuring all section titles and child rows are persisted to the database and displayed accurately in the print preview without data loss upon returning to Desk.
- **Double-Layer Title Persistence:** In addition to immediate `locals` synchronization, active section titles are cached in `sessionStorage` to prevent title loss across rapid route switches.
- **No Accidental Row Modal:** Clicking anywhere on a section row focuses the title input instead of opening the child row edit modal (`GridRowForm`).
- **Natural Column Sizing:** Hides standard cell contents on section rows using `visibility: hidden; pointer-events: none;`, keeping Frappe’s column resizing engine perfectly synchronized across all rows.

### Supported Child Tables
- `Quotation Item`
- `Sales Order Item`
- `Sales Invoice Item`
- `Purchase Order Item`
- `Purchase Invoice Item`
- `Delivery Note Item`
- `Purchase Receipt Item`

### Section Functions & Implementation Reference

#### Server-Side (`emc_utils/sections/sections.py`)
| Function | Purpose |
| :--- | :--- |
| `patch_all()` | Bootstraps global patches for Document validation and AccountsController. |
| `patch_document_mandatory()` | Bypasses Frappe's `_get_missing_mandatory_fields` for rows where `is_section == 1`. |
| `patch_accounts_controller()` | Patches `AccountsController.validate_qty_is_not_zero` to allow zero quantity on section rows. |
| `before_validate_sections(doc, method=None)` | Document event triggered before validation; zeroes financial fields and syncs `section_title` to `item_name` and `description`. |
| `before_print_sections(doc, method=None, print_settings=None)` | Prepares section rows for printing by injecting the `.emc-print-section-header` container and blanking unneeded data columns. |
| `is_section_row(row)` | Jinja helper method exposed in `frappe.is_section_row(item)`. |

#### Client-Side (`emc_utils/sections/sections.js`, `quotation.js`, `sales_order.js`)
| Function | Purpose |
| :--- | :--- |
| `emc.format_row(grid_row)` | Renders the `.emc-section-cell` overlay banner, binds inline typing events, and enforces non-truncated badge styling. |
| `emc.add_section(grid)` | Appends a new child row with default values (`is_section: 1`, `qty: 0`, `rate: 0`) and focuses the title field. |
| `emc.setup_grid_buttons(grid)` | Adds the **Add section** button next to Frappe's native **Add Row** button. |
| `frm.print_doc` (hooked) | Checks `frm.is_dirty()`; if unsaved changes exist, executes `frm.save()` before navigating to the print route. |

---

## Feature 2: Company Switcher & Multi-Company Scoping

Designed for ERPNext environments running multiple subsidiaries, holding companies, or branches.

### Key Highlights
- **Desk Header Menu:** Adds a **Companies** toggle submenu at the top of the Desk sidebar.
- **Tree-Aware Filtering:** Supports flat and nested company structures. Selecting a group company automatically includes all trading child companies under it.
- **Automatic Scoping:** Filters list views, reports, and link lookups using `permission_query_conditions` for all company-scoped doctypes (Sales, Purchases, Invoices, General Ledger, Stock).
- **Cross-Session Persistence:** Selected scope is saved to User Defaults (`company_switcher_scope`) and persists across devices and browser sessions.

### Company Switcher Functions & Implementation Reference

#### Server-Side (`emc_utils/company_switcher/company_switcher.py`)
| Function | Purpose |
| :--- | :--- |
| `get_companies()` | Returns all company records including tree boundaries (`lft`, `rgt`, `is_group`, `parent_company`). |
| `get_allowed_companies(user=None)` | Returns trading companies permitted for the user based on Frappe User Permissions. |
| `get_scope(user=None)` | Retrieves the user's currently selected company scope from User Defaults. |
| `get_switcher()` | Whitelisted RPC returning company tree hierarchy and active scope to the client. |
| `set_scope(companies)` | Whitelisted RPC saving the user's selected companies and updating default company. |
| `get_permission_query_conditions(user=None)` | Generates SQL conditions restricting doctype queries to the active company scope. |
| `boot_session(bootinfo)` | Injects company switcher metadata and per-company print format mappings into `frappe.boot`. |

---

## Feature 3: Frappe v16 Print Format Designer Integration

`emc_utils` provides complete out-of-the-box compatibility with the new visual **Print Format Designer** introduced in Frappe v16 (`print_format_builder_beta: 1`).

### 1. The Pre-Configured Sample Format: `Quotation with Sections`
During app installation and migration (`bench migrate`), `emc_utils` installs a standard sample format:
- **DocType:** `Quotation`
- **Format Name:** `Quotation with Sections`
- **Builder Engine:** Beta Print Format Builder (`print_format_builder_beta = 1`)
- **Mode:** `standard = "No"` (allowing direct visual edits and saves without requiring Frappe developer mode).

### 2. Sample Print Formats for Print Format Designer (v16.50+)

`emc_utils` provides 4 sample print formats ready for the new **Frappe v16 Print Format Designer**:
- **`Quotation with Sections`**: Classical layout with inline total pill on the section bar (`sec-total-position: header`).
- **`Quotation with Section Subtotals`**: Classical layout with dedicated subtotal summary rows at the end of each section aligned with the Amount column (`sec-total-position: bottom`).
- **`Quotation Modern with Sections`**: Direct non-standard clone of ERPNext's official **Quotation Modern** layout with executive header total pills.
- **`Quotation Modern with Subtotals`**: Minimalist Modern layout featuring dedicated section subtotal rows and clean accounting alignment.

All formats are non-standard (`standard: "No"`), allowing you to visually drag, drop, reorder fields, change column widths, and customize fonts and colors directly in Print Format Designer without developer mode or file overrides.

To customize or review the layout visually:
1. Navigate to **Print Format List** in Desk.
2. Open any of the 4 formats above.
3. Click the **Edit Format** button.
4. You will see the full visual drag-and-drop designer canvas:
   - Drag and drop fields (Company logo, Customer address, Terms and Conditions).
   - Reorder or add child table columns.
   - Adjust page sizes (A4, Letter) and margins.

### 3. Customizing Section Styling in Print Format Designer
Configure section visual styling directly from the **Child Table > Style > Custom CSS** field in Print Format Designer. Both shorthand (`sec-`) and standard CSS custom property (`--sec-`) formats are supported:

#### Section Custom CSS Options Reference

| Option | Shorthand | CSS Variable | Values / Description |
| :--- | :--- | :--- | :--- |
| **Row Background** | `sec-bg:` | `--sec-bg:` | Color hex / rgb (e.g. `#eff6ff`) |
| **Row Border** | `sec-border:` | `--sec-border:` | Top & bottom border color (e.g. `#bfdbfe`) |
| **Border Width** | `sec-border-width:` | `--sec-border-width:` | Border thickness (e.g. `1.5px`) |
| **Title Color** | `sec-title-color:` | `--sec-title-color:` | Text color of section title (e.g. `#1e40af`) |
| **Title Size** | `sec-title-size:` | `--sec-title-size:` | Font size (e.g. `14px`, `1rem`) |
| **Title Weight** | `sec-title-weight:` | `--sec-title-weight:` | Font weight (`normal`, `600`, `700`, `bold`) |
| **Title Transform** | `sec-title-transform:` | `--sec-title-transform:` | Text casing (`uppercase`, `capitalize`, `none`) |
| **Section Header Visibility** | `sec-display:` | `--sec-display:` | `show` (default) or `none` to hide section headers |
| **Row Number Visibility** | `sec-no-display:` / `sec-no:` | `--sec-no-display:` | `none` (default: skip numbering on section rows) or `show` |
| **Item Numbering Mode** | `sec-item-no:` | `--sec-item-no:` | `continuous` (default: 1, 2, 3, 4...), `section` (reset per section 1, 2...), or `original` (database idx) |
| **Badge Visibility** | `sec-badge-display:` | `--sec-badge-display:` | Set to `none` to hide the `[SECTION]` badge |
| **Badge Background** | `sec-badge-bg:` | `--sec-badge-bg:` | Badge pill background color (e.g. `#2563eb`) |
| **Badge Color** | `sec-badge-color:` | `--sec-badge-color:` | Badge text color (e.g. `#ffffff`) |
| **Badge Size** | `sec-badge-size:` | `--sec-badge-size:` | Badge font size (e.g. `8.5px`) |
| **Badge Radius** | `sec-badge-radius:` | `--sec-badge-radius:` | Pill border radius (e.g. `4px`) |
| **Section Total Position** | `sec-total-position:` | `--sec-total-position:` | `bottom` (dedicated row), `header` (inline on section bar), `both`, or `none` |
| **Section Total Price** | `sec-total:` / `sec-total-display:` | `--sec-total-display:` | Set to `none` to hide section total, or `show` to display |
| **Section Total Label** | `sec-total-label:` | `--sec-total-label-display:` | Set to `none` to hide "Section Total:" label and show amount only |
| **Section Total Color** | `sec-total-color:` | `--sec-total-color:` | Total price text color (e.g. `#0f172a`, `#1e40af`) |
| **Section Total Background** | `sec-total-bg:` | `--sec-total-bg:` | Pill/badge background color (e.g. `#dbeafe`) |
| **Section Total Size** | `sec-total-size:` | `--sec-total-size:` | Total price font size (e.g. `12.5px`) |
| **Subtotal Row Background** | `sec-subtotal-bg:` | `--sec-subtotal-bg:` | Background color of dedicated subtotal row (e.g. `#f8fafc`) |
| **Subtotal Row Top Border** | `sec-subtotal-border:` | `--sec-subtotal-border:` | Top border color of dedicated subtotal row |
| **Subtotal Row Bottom Border** | `sec-subtotal-border-bottom:` | `--sec-subtotal-border-bottom:` | Bottom border style (e.g. `2px solid #0f172a`, `3px double #94a3b8`) |
| **Subtotal Row Color** | `sec-subtotal-color:` | `--sec-subtotal-color:` | Text and amount color of dedicated subtotal row |
| **Subtotal Row Size** | `sec-subtotal-size:` | `--sec-subtotal-size:` | Font size of subtotal title (e.g. `13px`) |
| **Subtotal Badge Visibility** | `sec-subtotal-badge:` | `--sec-subtotal-badge-display:` | `show` (default) or `none` to hide `[SUBTOTAL]` pill badge |
| **Subtotal Badge Background** | `sec-subtotal-badge-bg:` | `--sec-subtotal-badge-bg:` | Subtotal pill badge background color |
| **Subtotal Badge Color** | `sec-subtotal-badge-color:` | `--sec-subtotal-badge-color:` | Subtotal pill badge text color |
| **Subtotal Amount Size** | `sec-subtotal-amount-size:` | `--sec-subtotal-amount-size:` | Subtotal amount font size (e.g. `13.5px`) |

#### Ready-to-Use Presets

**1. Title-Only Row (No Badge, No Row Number, Full-Width Banner)**
```css
border: 1px solid #e5e7eb; padding: 6px;
sec-bg: #eff6ff;
sec-border: #bfdbfe;
sec-badge-display: none;
sec-no-display: none;
sec-title-color: #1e40af;
sec-title-size: 14px;
sec-title-weight: 700;
```

**2. Modern Contrast (Pill Badge & Row Number)**
```css
sec-bg: #f8fafc;
sec-border: #cbd5e1;
sec-badge-bg: #0f172a;
sec-badge-color: #ffffff;
sec-title-color: #0f172a;
sec-title-size: 13.5px;
```

**3. Minimalist Line (White Background, Border-Only)**
```css
sec-bg: #ffffff;
sec-border: #e2e8f0;
sec-badge-display: none;
sec-no-display: none;
sec-title-color: #111827;
sec-title-size: 13.5px;
```

**4. Dedicated Subtotal Row (Bottom of Section)**
```css
sec-bg: #f8fafc;
sec-border: #cbd5e1;
sec-title-color: #0f172a;
sec-total-position: bottom;
sec-subtotal-bg: #f1f5f9;
sec-subtotal-color: #0f172a;
```

#### Built-in Print Protection & Failsafe
- **Zero Financial Values Blanked:** The Python `before_print` hook suppresses quantities (`0`), rates (`Br 0.00`), amounts (`Br 0.00`), and units on section rows before Jinja renders the table.
- **Server-Side CSS Injection:** When custom section styles are detected, styles are injected into the document `<head>` stylesheet, ensuring section rows expand cleanly without breaking merged column layouts (`Item + Description`).

### 4. Compatibility with Traditional Jinja Print Formats
If you maintain classic or custom Jinja print templates, you can format section rows using `frappe.is_section_row(row)`:
```html
<tbody>
  {% for item in doc.items %}
    {% if frappe.is_section_row(item) %}
      <tr class="section-row" style="background:#f1f5f9; font-weight:bold;">
        <td colspan="6" style="padding:10px;">
          <span class="badge" style="background:#000; color:#fff; padding:2px 6px; border-radius:4px;">SECTION</span>
          {{ item.section_title or item.item_name }}
        </td>
      </tr>
    {% else %}
      <tr>
        <td>{{ item.idx }}</td>
        <td>{{ item.item_name }}</td>
        <td>{{ item.item_code }}</td>
        <td>{{ item.qty }}</td>
        <td>{{ item.get_formatted("rate") }}</td>
        <td>{{ item.get_formatted("amount") }}</td>
      </tr>
    {% endif %}
  {% endfor %}
</tbody>
```

---

## Installation & Setup

### 1. Install via Bench
From your Frappe bench directory:

```bash
# Fetch repository
bench get-app https://github.com/girumtibebu/emc_utils.git

# Install app on target site
bench --site emcy.localhost install-app emc_utils

# Run database migrations (sets up custom fields, property setters, and sample print formats)
bench --site emcy.localhost migrate

# Clear cache
bench --site emcy.localhost clear-cache
```

### 2. Updating / Upgrading
When pulling the latest updates from GitHub:

```bash
cd apps/emc_utils
git pull origin main
bench --site emcy.localhost migrate
bench --site emcy.localhost clear-cache
```

---

## Extending `emc_utils`: Adding New Customizations

Thanks to the modular architecture, adding a new customization (e.g. `barcode_scanner` or `approval_flow`) takes 4 simple steps:

1. **Create the feature package:**
   ```bash
   mkdir -p emc_utils/my_feature
   touch emc_utils/my_feature/__init__.py
   touch emc_utils/my_feature/my_feature.py
   touch emc_utils/my_feature/setup.py
   ```
2. **Define setup routines in `my_feature/setup.py`:**
   Add any custom fields, property setters, or records your feature needs.
3. **Connect to the root orchestrator (`emc_utils/setup.py`):**
   ```python
   from emc_utils.my_feature.setup import setup_feature as setup_my_feature

   def after_migrate():
       ...
       setup_my_feature()
   ```
4. **Register assets & hooks in `emc_utils/hooks.py`:**
   Add JavaScript or CSS files under `app_include_js` / `app_include_css` or DocType hooks under `doc_events`.

---

## License

This project is licensed under the [MIT License](license.txt).
