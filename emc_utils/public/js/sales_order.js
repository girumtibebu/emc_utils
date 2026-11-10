// EMC Utilities - Sales Order Sections Enhancement
(function () {
    const CSS = `
        /* Expand child table grid container and form grid to fit all columns */
        .form-grid-container > .form-grid {
            width: max-content !important;
            min-width: 100% !important;
        }

        .form-grid .grid-body .rows > .grid-row {
            width: 100% !important;
        }

        /* Espresso Section Row in Child Table */
        .grid-row.emc-grid-section-row,
        .data-row.emc-grid-section-row {
            background-color: var(--surface-gray-2, #f8fafc) !important;
            border-top: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            border-bottom: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            border-left: 3px solid var(--surface-gray-10, #334155) !important;
            min-height: 38px !important;
        }

        [data-theme="dark"] .grid-row.emc-grid-section-row,
        [data-theme="dark"] .data-row.emc-grid-section-row,
        .dark .grid-row.emc-grid-section-row,
        .dark .data-row.emc-grid-section-row {
            background-color: var(--surface-gray-3, #1e293b) !important;
            border-top-color: var(--outline-gray-2, #334155) !important;
            border-bottom-color: var(--outline-gray-2, #334155) !important;
            border-left-color: var(--surface-gray-10, #94a3b8) !important;
        }

        .data-row.emc-grid-section-row {
            width: 100% !important;
            min-width: 100% !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }

        /* Checkbox and Index columns stay sticky on left */
        .data-row.emc-grid-section-row .row-check,
        .data-row.emc-grid-section-row .row-index {
            background-color: inherit !important;
            z-index: 3 !important;
        }

        /* Section Title & Badge: Sticky positioning at left 71px (right next to row-index) */
        .data-row.emc-grid-section-row .emc-section-cell {
            position: sticky !important;
            left: 71px !important;
            z-index: 2 !important;
            flex: 0 1 auto !important;
            width: auto !important;
            min-width: 280px !important;
            max-width: calc(100vw - 160px) !important;
            display: flex !important;
            align-items: center !important;
            padding: 3px 10px !important;
            background-color: inherit !important;
        }

        .emc-section-inner {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
        }

        /* Hide standard child table data columns in section rows */
        .data-row.emc-grid-section-row .col.grid-static-col:not(.row-index) {
            display: none !important;
        }

        /* Keep the open form pencil button pinned at the far right */
        .data-row.emc-grid-section-row .col:last-child {
            max-width: 30px !important;
            min-width: 30px !important;
            position: sticky !important;
            right: 0 !important;
            z-index: 3 !important;
            background-color: inherit !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-left: auto !important;
        }

        /* Frappe UI / Espresso Badge for Section */
        .emc-section-badge {
            cursor: grab !important;
            flex-shrink: 0 !important;
            letter-spacing: 0.04em !important;
            font-weight: 600 !important;
        }

        /* Clean Espresso-compatible Input with Guaranteed High-Contrast Visibility */
        .emc-section-input {
            font-size: 13px !important;
            font-weight: 600 !important;
            color: var(--text-color, #111827) !important;
            -webkit-text-fill-color: var(--text-color, #111827) !important;
            text-align: left !important;
            background: transparent !important;
            border: 1px dashed transparent !important;
            border-radius: var(--radius-sm, 6px) !important;
            box-shadow: none !important;
            height: 28px !important;
            padding: 2px 8px !important;
            width: 100% !important;
            min-width: 180px !important;
            transition: all 0.15s ease-in-out !important;
        }

        .emc-section-input:focus,
        .emc-section-input:hover {
            background: #ffffff !important;
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            border: 1px solid var(--outline-primary, var(--primary-color, #2563eb)) !important;
            box-shadow: var(--shadow-xs, 0 1px 2px rgba(0,0,0,0.05)) !important;
        }

        [data-theme="dark"] .emc-section-input,
        .dark .emc-section-input {
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
        }

        [data-theme="dark"] .emc-section-input:focus,
        .dark .emc-section-input:focus {
            background: #1e293b !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
    `;

    frappe.dom.set_style(CSS, "emc_utils_style");

    // 1. Bypass client-side mandatory checks for section rows on form save
    function patch_check_mandatory() {
        if (!frappe.ui?.form || frappe.ui.form.__emc_check_mandatory_patched) return;

        const orig_check_mandatory = frappe.ui.form.check_mandatory;
        frappe.ui.form.check_mandatory = function (frm) {
            const orig_get_all_docs = frappe.model.get_all_docs;
            frappe.model.get_all_docs = function (doc) {
                const all = orig_get_all_docs.call(frappe.model, doc);
                return all.filter((d) => !d.is_section);
            };

            try {
                return orig_check_mandatory.call(this, frm);
            } finally {
                frappe.model.get_all_docs = orig_get_all_docs;
            }
        };

        frappe.ui.form.__emc_check_mandatory_patched = true;
    }

    // 2. Format a single grid row with Frappe UI badge and section input
    function format_row(grid_row) {
        if (!grid_row || !grid_row.row || !grid_row.doc) return;
        const $row = grid_row.row;
        const $wrapper = grid_row.wrapper;

        if (grid_row.doc.is_section) {
            $row.addClass("emc-grid-section-row");
            if ($wrapper) $wrapper.addClass("emc-grid-section-row");

            // Hide standard child table data columns in section row
            $row.find(".grid-static-col:not(.row-index)").hide();

            // Match width with grid header row so background and sticky elements span entire scrollable grid
            if (grid_row.grid && grid_row.grid.wrapper) {
                const header_row = grid_row.grid.wrapper.find(".grid-heading-row .data-row");
                const w = header_row.outerWidth();
                if (w && w > 0) {
                    $row.css("min-width", w + "px");
                }
            }

            let $cell = $row.find(".emc-section-cell");
            if (!$cell.length) {
                let badge_html = "";
                if (frappe.ui?.badge?.html) {
                    badge_html = frappe.ui.badge.html({
                        label: __("SECTION"),
                        theme: "gray",
                        size: "sm",
                        variant: "solid",
                        css_class: "sortable-handle emc-section-badge",
                    });
                } else {
                    badge_html = `<span class="es-badge sortable-handle emc-section-badge" data-size="sm" data-variant="solid"><span class="es-badge__label">${__("SECTION")}</span></span>`;
                }

                const title = grid_row.doc.section_title || grid_row.doc.item_name || "";

                $cell = $(`
                    <div class="col emc-section-cell">
                        <div class="emc-section-inner">
                            ${badge_html}
                            <input type="text" class="form-control emc-section-input" value="${frappe.utils.escape_html(title)}" placeholder="${__("Section Title...")}">
                        </div>
                    </div>
                `);

                const $row_index = $row.find(".row-index");
                if ($row_index.length) {
                    $cell.insertAfter($row_index);
                } else {
                    $row.append($cell);
                }
            }

            // Ensure the open form button (edit pencil) is visible and at the end of the row
            if (grid_row.open_form_button && grid_row.open_form_button.length) {
                grid_row.open_form_button.show();
                if ($row.children().last()[0] !== grid_row.open_form_button[0]) {
                    $row.append(grid_row.open_form_button);
                }
            }

            // Bind input and keyboard events
            $cell
                .find(".emc-section-input")
                .off("click.emc mousedown.emc input.emc blur.emc keydown.emc")
                .on("click.emc mousedown.emc", function (e) {
                    e.stopPropagation();
                })
                .on("input.emc blur.emc", function () {
                    const val = $(this).val();
                    if (grid_row.doc.section_title !== val) {
                        frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "section_title", val);
                        frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "item_name", val);
                        frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "description", val);
                    }
                })
                .on("keydown.emc", function (e) {
                    if (e.key === "Enter") {
                        $(this).blur();
                        e.preventDefault();
                    }
                });
        } else {
            $row.removeClass("emc-grid-section-row");
            if ($wrapper) $wrapper.removeClass("emc-grid-section-row");
            $row.find(".emc-section-cell").remove();
            $row.find(".grid-static-col:not(.row-index)").show();
            $row.css("min-width", "");
        }
    }

    // 3. Add section row with safe default values
    function add_section(grid) {
        const row = grid.add_new_row(null, null, false, null, true);
        if (row) {
            frappe.model.set_value(row.doctype, row.name, "is_section", 1);
            frappe.model.set_value(row.doctype, row.name, "section_title", __("New Section"));
            frappe.model.set_value(row.doctype, row.name, "item_name", __("New Section"));
            frappe.model.set_value(row.doctype, row.name, "description", __("New Section"));
            frappe.model.set_value(row.doctype, row.name, "qty", 0);
            frappe.model.set_value(row.doctype, row.name, "rate", 0);
            frappe.model.set_value(row.doctype, row.name, "amount", 0);
            frappe.model.set_value(row.doctype, row.name, "uom", "Unit");
            frappe.model.set_value(row.doctype, row.name, "conversion_factor", 1);

            grid.refresh();

            setTimeout(() => {
                const grid_row = grid.grid_rows_by_docname && grid.grid_rows_by_docname[row.name];
                if (grid_row && grid_row.row) {
                    format_row(grid_row);
                    const $inp = grid_row.row.find(".emc-section-input");
                    if ($inp.length) {
                        $inp.focus().select();
                    }
                }
            }, 80);
        }
    }

    // 4. Setup grid buttons & rows
    function setup_grid(frm, table_fieldname = "items") {
        patch_check_mandatory();

        if (!frm || !frm.fields_dict || !frm.fields_dict[table_fieldname]) return;
        const grid = frm.fields_dict[table_fieldname].grid;
        if (!grid || !grid.wrapper) return;

        const $grid_buttons = grid.wrapper.find(".grid-buttons");
        if ($grid_buttons.length) {
            let $btn = $grid_buttons.find(".grid-add-section");
            if (!$btn.length) {
                let btn_html = "";
                if (frappe.ui?.button?.html) {
                    btn_html = frappe.ui.button.html({
                        label: __("Add section"),
                        size: "sm",
                        css_class: "grid-add-section",
                    });
                } else {
                    btn_html = `<button class="btn es-button grid-add-section" type="button">${__("Add section")}</button>`;
                }
                $btn = $(btn_html);

                const $add_multiple = $grid_buttons.find(".grid-add-multiple-rows");
                const $add_row = $grid_buttons.find(".grid-add-row");

                if ($add_multiple.length) {
                    $btn.insertAfter($add_multiple);
                } else if ($add_row.length) {
                    $btn.insertAfter($add_row);
                } else {
                    $grid_buttons.append($btn);
                }

                $btn.on("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    add_section(grid);
                });
            }

            // Ensure button is visible
            $btn.removeClass("hidden d-none");
        }

        // Format all existing rows
        if (grid.grid_rows) {
            grid.grid_rows.forEach((r) => format_row(r));
        }

        // Hook GridRow render_row permanently for this form
        if (frappe.ui?.form?.GridRow && !frappe.ui.form.GridRow.__emc_patched) {
            const orig_render_row = frappe.ui.form.GridRow.prototype.render_row;
            frappe.ui.form.GridRow.prototype.render_row = function () {
                const res = orig_render_row.apply(this, arguments);
                format_row(this);
                return res;
            };
            frappe.ui.form.GridRow.__emc_patched = true;
        }

        // Hook grid refresh so sorting, filtering, and column configuration maintains proper formatting
        if (!grid.__emc_hooked) {
            const orig_refresh = grid.refresh;
            grid.refresh = function () {
                orig_refresh.apply(this, arguments);
                setup_grid(frm, table_fieldname);
            };
            grid.__emc_hooked = true;
        }
    }

    frappe.ui.form.on("Sales Order", {
        onload(frm) {
            setup_grid(frm, "items");
        },
        refresh(frm) {
            setup_grid(frm, "items");
        },
        items_render(frm) {
            setup_grid(frm, "items");
        }
    });
})();
