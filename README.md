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
├── print_format/                   # 🖨️ Four master print templates (EMC and ALT)
│   ├── __init__.py                 # Public domain exports
│   ├── setup.py                   # Automated installer/updater for sample print formats
│   ├── quotation_sections.json    # Visual designer format_data layout (header totals)
│   ├── quotation_subtotals.json   # Visual designer format_data layout (dedicated subtotal rows)
│   ├── quotation_modern_sections.json
│   ├── quotation_modern_subtotals.json
│   └── quotation_sections.css     # Section print styling exposed in designer's Custom CSS panel
│
├── print_format/                   # 📄 Bundled Standard Print Formats (auto-synced to site)
│   ├── quotation_with_sections/
│   ├── quotation_with_section_subtotals/
│   ├── quotation_modern_with_sections/
│   └── quotation_modern_with_subtotals/
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

## Feature 3: Print Templates

Four master templates, each honouring the print check boxes on Quotation and Sales Order:

- **EMC Quotation Template - Master** and **EMC Sales Order Template - Master** (EMC branding).
- **ALT Quotation Template - Master** and **ALT Sales Order Template - Master** (ALT branding, same logic).

Each honours Print Payment Terms, Print Terms and Conditions, Show Signature on Print and Print Without VAT.

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

## Changelog

### 1.2.1

- ALT masters now use the Alter layout: the Alter Space design for Quotation and the Alter Sales Order design (staging) for Sales Order, with the same toggles, sections and signature logic as EMC.
- Desk Print Settings split into labelled groups: "Table columns" and "Printed blocks". The signature link sits next to its toggle.

### 1.2.0

- Print formats reduced to the four master templates: EMC and ALT, Quotation and Sales Order.
- Removed the other EMC template variants, the Decor and Alter formats, the Modern/Sections samples and the sample installer (`print_designer/`).
- New ALT Quotation and Sales Order masters, cloned from the EMC masters with ALT branding.
- Existing live print format records are not deleted by the app update.

### 1.1.0

**Print (Quotation and Sales Order)**
- New check boxes: **Print Payment Terms**, **Print Terms and Conditions**, and **Show Signature on Print** (all default on). The payment schedule, terms and signature blocks honour them in every EMC template and in the Decor template.
- New **Print Signature** link (required, default set in `print_settings.py`) to the **Signature** doctype.
- **Signature** is now a doctype in `EMC Utils` (it was a custom doctype on live). Its signature images are site data and are not in the repo.
- VAT, Agency Fee and Grand Total logic and the bolder Grand Total in the Master templates (from commits 50fad6b and 49f4708).
- Print Settings layout: table options on the left, printed blocks on the right; "Hide Quantity Column" moved into the table group.

**Print formats**
- Restored the **Decor** bold quotation theme, now in `print_format/quotation_bold_decor/`.
- Added **Alter Space Quotation Template** (`quotation_alter_space/`) and **Alter Sales Order** (`sales_order_alter/`).
- Section CSS for the four Modern/Sections formats updated to the live version.

**Maintenance**
- Removed duplicate copies of `print_settings.py` and the print format and doctype folders outside the module folder.
- Removed the two unused test files (`test_crm.py`, `test_print_blocks.py`); git history keeps them.

---

## License

This project is licensed under the [MIT License](license.txt).
