// EMC Utilities - Universal Child Table Sections Module
window.emc_utils = window.emc_utils || {};

(function (emc) {
    const CSS = `
        /* Espresso Section Row in Child Table */
        .grid-row.emc-grid-section-row {
            background-color: var(--surface-gray-2, #f8fafc) !important;
            border-top: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            border-bottom: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            cursor: default !important;
            min-height: 38px !important;
        }

        [data-theme="dark"] .grid-row.emc-grid-section-row,
        .dark .grid-row.emc-grid-section-row {
            background-color: var(--surface-gray-3, #1e293b) !important;
            border-top-color: var(--outline-gray-2, #334155) !important;
            border-bottom-color: var(--outline-gray-2, #334155) !important;
        }

        .data-row.emc-grid-section-row {
            position: relative !important;
            background-color: transparent !important;
            cursor: default !important;
        }

        /* Row checkbox and index: stay visible and sticky on left */
        .data-row.emc-grid-section-row .row-check,
        .data-row.emc-grid-section-row .row-index {
            position: sticky !important;
            background-color: var(--surface-gray-2, #f8fafc) !important;
            z-index: 4 !important;
        }

        [data-theme="dark"] .data-row.emc-grid-section-row .row-check,
        [data-theme="dark"] .data-row.emc-grid-section-row .row-index,
        .dark .data-row.emc-grid-section-row .row-check,
        .dark .data-row.emc-grid-section-row .row-index {
            background-color: var(--surface-gray-3, #1e293b) !important;
        }

        /* Hide contents of data columns and action button in section row while preserving exact underlying column widths */
        .data-row.emc-grid-section-row .col.grid-static-col:not(.row-index),
        .data-row.emc-grid-section-row .col:last-child {
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Section overlay banner: spans from left 71px to the right end of the row */
        .data-row.emc-grid-section-row .emc-section-cell {
            position: absolute !important;
            top: 0 !important;
            bottom: 0 !important;
            left: 71px !important;
            right: 0 !important;
            z-index: 3 !important;
            display: flex !important;
            align-items: center !important;
            padding: 2px 14px !important;
            background-color: var(--surface-gray-2, #f8fafc) !important;
            border: none !important;
            cursor: default !important;
        }

        [data-theme="dark"] .data-row.emc-grid-section-row .emc-section-cell,
        .dark .data-row.emc-grid-section-row .emc-section-cell {
            background-color: var(--surface-gray-3, #1e293b) !important;
        }

        .emc-section-inner {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            width: 100% !important;
            flex: 1 1 auto !important;
        }

        /* Frappe UI / Espresso Badge for Section */
        .emc-section-badge {
            cursor: grab !important;
            flex-shrink: 0 !important;
            letter-spacing: 0.04em !important;
            font-weight: 600 !important;
            user-select: none !important;
        }

        /* Clean Espresso-compatible Input with Full-Width Expansion and Guaranteed High-Contrast Visibility */
        .emc-section-input {
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: var(--text-color, #111827) !important;
            -webkit-text-fill-color: var(--text-color, #111827) !important;
            text-align: left !important;
            background: transparent !important;
            border: 1px dashed transparent !important;
            border-radius: var(--radius-sm, 6px) !important;
            box-shadow: none !important;
            height: 30px !important;
            padding: 2px 10px !important;
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 250px !important;
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
    emc.patch_check_mandatory = function () {
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
    };

    // 2. Permanently prevent section rows from opening modal/form view
    emc.patch_grid_row_toggle_view = function () {
        if (frappe.ui?.form?.GridRow && !frappe.ui.form.GridRow.__emc_toggle_view_patched) {
            const orig_toggle_view = frappe.ui.form.GridRow.prototype.toggle_view;
            frappe.ui.form.GridRow.prototype.toggle_view = function (show, callback) {
                if (this.doc && this.doc.is_section) {
                    return this;
                }
                return orig_toggle_view.apply(this, arguments);
            };
            frappe.ui.form.GridRow.__emc_toggle_view_patched = true;
        }
    };

    // 3. Format a single grid row with Frappe UI badge and section input
    emc.format_row = function (grid_row) {
        if (!grid_row || !grid_row.row || !grid_row.doc) return;
        const $row = grid_row.row;
        const $wrapper = grid_row.wrapper;

        if (grid_row.doc.is_section) {
            $row.addClass("emc-grid-section-row");
            if ($wrapper) $wrapper.addClass("emc-grid-section-row");

            // Disable row click opening modal
            $row.off("click.emc_row").on("click.emc_row", function (e) {
                if ($(e.target).hasClass("grid-row-check") || $(e.target).is(":checkbox")) {
                    return;
                }
                e.preventDefault();
                e.stopImmediatePropagation();
                $row.find(".emc-section-input").focus();
                return false;
            });

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
                    <div class="emc-section-cell">
                        <div class="emc-section-inner">
                            ${badge_html}
                            <input type="text" class="form-control emc-section-input" value="${frappe.utils.escape_html(title)}" placeholder="${__("Section Title...")}">
                        </div>
                    </div>
                `);

                $row.append($cell);
            }

            // Bind input and keyboard events
            $cell
                .off("click.emc mousedown.emc")
                .on("click.emc mousedown.emc", function (e) {
                    e.stopPropagation();
                });

            $cell
                .find(".emc-section-input")
                .off("input.emc blur.emc keydown.emc")
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
            $row.off("click.emc_row");
            $row.find(".emc-section-cell").remove();
        }
    };

    // 4. Setup grid buttons (Add section)
    emc.setup_grid_buttons = function (grid) {
        if (!grid || !grid.wrapper || !grid.df || grid.df.read_only) return;

        const $grid_buttons = grid.wrapper.find(".grid-buttons");
        if (!$grid_buttons.length) return;

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
                emc.add_section(grid);
            });
        }

        $btn.removeClass("hidden d-none");
    };

    // 5. Add section row with safe default values
    emc.add_section = function (grid) {
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
                    emc.format_row(grid_row);
                    const $inp = grid_row.row.find(".emc-section-input");
                    if ($inp.length) {
                        $inp.focus().select();
                    }
                }
            }, 80);
        }
    };

    // 6. Permanent GridRow and Grid prototype hooks
    emc.install_patches = function () {
        emc.patch_check_mandatory();
        emc.patch_grid_row_toggle_view();

        if (frappe.ui?.form?.GridRow && !frappe.ui.form.GridRow.__emc_patched) {
            const orig_render_row = frappe.ui.form.GridRow.prototype.render_row;
            frappe.ui.form.GridRow.prototype.render_row = function () {
                const res = orig_render_row.apply(this, arguments);
                emc.format_row(this);
                return res;
            };
            frappe.ui.form.GridRow.__emc_patched = true;
        }

        if (frappe.ui?.form?.Grid && !frappe.ui.form.Grid.__emc_patched) {
            const orig_refresh = frappe.ui.form.Grid.prototype.refresh;
            frappe.ui.form.Grid.prototype.refresh = function () {
                orig_refresh.apply(this, arguments);
                emc.setup_grid_buttons(this);
                if (this.grid_rows) {
                    this.grid_rows.forEach((r) => emc.format_row(r));
                }
            };

            const orig_setup_toolbar = frappe.ui.form.Grid.prototype.setup_toolbar;
            frappe.ui.form.Grid.prototype.setup_toolbar = function () {
                orig_setup_toolbar.apply(this, arguments);
                emc.setup_grid_buttons(this);
            };

            frappe.ui.form.Grid.__emc_patched = true;
        }
    };

    // 7. Direct grid setup helper
    emc.setup_grid = function (grid) {
        if (!grid) return;
        emc.install_patches();
        emc.setup_grid_buttons(grid);
        if (grid.grid_rows) {
            grid.grid_rows.forEach((r) => emc.format_row(r));
        }
    };

    // 8. Form setup entrypoint
    emc.setup_form_grid_sections = function (frm) {
        if (!frm || !frm.fields) return;
        emc.install_patches();

        frm.fields.forEach((field) => {
            if (field.df?.fieldtype === "Table" && field.grid) {
                emc.setup_grid(field.grid);
            }
        });
    };

    // Auto-install immediately and on lifecycle events
    emc.install_patches();
    $(document).on("form-refresh", (_e, frm) => emc.setup_form_grid_sections(frm));
    $(document).on("grid-row-render", (_e, grid_row) => emc.format_row(grid_row));
    $(document).on("app_ready startup", () => emc.install_patches());
})(window.emc_utils);
