# EMC Utilities (`emc_utils`)

[![Frappe Framework](https://img.shields.io/badge/Frappe-v15%20%7C%20v16-blue.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15%20%7C%20v16-brightgreen.svg)](https://erpnext.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A unified utility app for Frappe Framework & ERPNext that replaces fragmented client/server scripts with upgrade-safe, configurable modules:

- **Universal Child Table Sections:** Add clean, draggable visual section dividers and headings directly inside transactional child tables (Quotations, Sales Orders, Invoices, Purchase Orders, etc.) with Frappe UI / Espresso design elements.
- **Company Switcher & Multi-Company Scoping:** Switch between companies from the Desk sidebar and scope document lists and link searches to selected companies (supporting flat and group hierarchies).
- **Per-Company Print Formats:** Configure brand-specific default print formats per company.
- **Sectioned Modern Print Templates:** Full-width section dividers that seamlessly translate from Desk view to PDF and print formats.

---

## Features

### 1. Universal Child Table Sections

Organize long transactional item tables into logical groups and categories (e.g., *Phase 1: Hardware*, *Phase 2: Installation*, *Optional Accessories*).

- **Frappe UI / Espresso Design:** Uses native Espresso buttons (`.es-button`), pill badges (`.es-badge`), and design tokens matching Frappe v16's modern Desk aesthetic.
- **Inline Title Editing:** Click and type section headings directly inline with real-time sync. Supports both Light and Dark Desk themes with high-contrast typography.
- **Drag-and-Drop Reordering:** Section rows include drag handles on the `SECTION` badge and row number, allowing items to be dragged and organized between sections using SortableJS.
- **Zero Financial Impact:** Quantities, rates, amounts, net totals, and stock quantities on section rows are strictly zeroed out automatically—protecting invoice totals, taxes, and ledgers.
- **Multi-Layer Validation Protection:**
  - Dynamic `Property Setter` layer: `reqd: 0` with `mandatory_depends_on: eval:!doc.is_section`.
  - Client-side save validation bypass (`frappe.ui.form.check_mandatory`).
  - Server-side mandatory check bypass (`Document._get_missing_mandatory_fields`).
  - Quantity validation bypass (`AccountsController.validate_qty_is_not_zero`).

#### Supported Child Tables Out-of-the-Box:
- `Quotation Item`
- `Sales Order Item`
- `Sales Invoice Item`
- `Purchase Order Item`
- `Purchase Invoice Item`
- `Delivery Note Item`
- `Purchase Receipt Item`

---

### 2. Company Switcher & Multi-Company Scoping

Designed for ERPNext setups running multiple operating entities or holding groups.

- **Desk Sidebar Integration:** A "Companies" toggle menu is embedded into the Desk sidebar header menu.
- **Flexible Scope:** Select all companies, individual companies, or entire parent groups (ticking a group automatically includes all child companies).
- **Automatic List Filtering:** Narrows list views, reports, and link lookups using `permission_query_conditions` for all company-scoped doctypes (Selling, Buying, Accounts, Stock, CRM, HR, Assets).
- **Cross-Device Persistence:** Choices are saved to user defaults (`company_switcher_scope`) and follow users across devices and sessions.

---

### 3. Per-Company Default Print Formats

Print documents with company-specific templates without changing site-wide defaults:
- Configurable on each **Company** record under the **Print Formats** section.
- Supports per-company defaults for Quotations, Sales Orders, Sales Invoices, Delivery Notes, and Purchase Orders.
- Automatically applied on form refresh (`apply_company_print_format`).

---

### 4. Modern Sectioned Print Formats & Print Designe

Sections translate cleanly into printable documents and PDFs:

- **Included Jinja Template:** `Quotation Modern with Sections` renders full-width banner rows (`colspan`) with badge styling, clean typography, and continuous numbering that skips section divider rows.
- **Jinja Helper Function:** Exposes `frappe.is_section_row(row)` in `jinja.methods`, allowing custom print formats to detect section rows with:
  ```jinja
  {% if is_section_row(item) %}
    <tr class="section-divider-row">
      <td colspan="5"><strong>{{ item.section_title or item.item_name }}</strong></td>
    </tr>
  {% else %}
    <!-- Regular item row -->
  {% endif %}
  ```
- **Print Designer (Visual Builder) Compatibility:**
  - In visual table column settings, use conditional expressions:
    ```jinja
    {% if row.is_section %}{{ row.section_title }}{% else %}{{ row.item_code }}{% endif %}
    ```
  - In numeric columns (`Qty`, `Rate`, `Amount`):
    ```jinja
    {% if not row.is_section %}{{ row.get_formatted("amount", doc) }}{% endif %}
    ```

---

## Installation

Inside your bench directory:

```bash
# 1. Get the app from GitHub
bench get-app https://github.com/girumtibebu/emc_utils.git

# 2. Install on your target site
bench --site <your-site> install-app emc_utils

# 3. Run migrations to install custom fields and property setters
bench --site <your-site> migrate

# 4. Clear cache and restart bench
bench --site <your-site> clear-cache
bench restart
```

---

## Development & Architecture

```text
emc_utils/
├── company_scope.py     # Company switcher backend logic, tree traversal & query filters
├── constants.py         # Scoped doctypes and print format fields
├── hooks.py             # App hooks, asset bundles, boot_session, permission queries
├── sections.py          # Child table validation patches, zeroing logic, Jinja methods
├── setup.py             # Custom fields and property setters installation
├── print_format/        # Jinja print format templates (e.g. Quotation Modern with Sections)
└── public/
    ├── js/
    │   ├── company_switcher.js  # Sidebar header company toggle menu
    │   ├── emc_utils.js         # Core child table section styling and event hooks
    │   ├── quotation.js         # Quotation form client script hook
    │   └── sales_order.js       # Sales Order form client script hook
    └── css/
        └── emc_utils.css        # Desk utility styles
```

---

## License

This project is licensed under the [MIT License](license.txt).
