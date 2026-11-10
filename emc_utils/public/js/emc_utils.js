// EMC Utilities - Universal Child Table Sections Module
window.emc_utils = window.emc_utils || {};

(function (emc) {
    const CSS = `
        /* Espresso Section Row */
        .grid-row.emc-grid-section-row {
            background-color: var(--surface-gray-2, #f8fafc) !important;
            border-top: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            border-bottom: 1px solid var(--outline-gray-2, #e2e8f0) !important;
            border-left: 3px solid var(--surface-gray-10, #334155) !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            min-height: 38px !important;
        }

        /* Hide standard child columns in section row, keep index & check */
        .grid-row.emc-grid-section-row .col:not(.row-check):not(.row-index):not(.emc-section-cell) {
            display: none !important;
        }

        .emc-grid-section-row .emc-section-cell {
            flex: 1 1 auto !important;
            display: flex !important;
            align-items: center !important;
            padding: 3px 10px !important;
            overflow: hidden !important;
        }

        .emc-section-inner {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
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

    // 2. Format a single grid row with Frappe UI badge and section input
    emc.format_row = function (grid_row) {
        if (!grid_row || !grid_row.row || !grid_row.doc) return;
        const $row = grid_row.row;

        if (grid_row.doc.is_section) {
            $row.addClass("emc-grid-section-row");

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

                $cell = $(`
                    <div class="col emc-section-cell">
                        <div class="emc-section-inner">
                            ${badge_html}
                            <input type="text" class="form-control input-sm emc-section-input" placeholder="${__("Type section heading / title...")}" />
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

            const title = grid_row.doc.section_title || grid_row.doc.item_name || "";
            const $input = $cell.find(".emc-section-input");
            if ($input.val() !== title) {
                $input.val(title);
            }

            $input.off("input.emc change.emc blur.emc keydown.emc")
                .on("input.emc", function () {
                    const val = $(this).val();
                    grid_row.doc.section_title = val;
                    grid_row.doc.item_name = val;
                    grid_row.doc.description = val;
                })
                .on("change.emc blur.emc", function () {
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
            $row.find(".emc-section-cell").remove();
        }
    };

    // 3. Add Section button (Frappe UI / Espresso button)
    emc.setup_grid_buttons = function (grid) {
        if (!grid || !grid.wrapper) return;

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

    // 4. Add section row with safe default values
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

    // 5. Permanent GridRow and Grid prototype hooks
    emc.install_patches = function () {
        emc.patch_check_mandatory();

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

    // 6. Direct grid setup helper
    emc.setup_grid = function (grid) {
        if (!grid) return;
        emc.install_patches();
        emc.setup_grid_buttons(grid);
        if (grid.grid_rows) {
            grid.grid_rows.forEach((r) => emc.format_row(r));
        }
    };

    // 7. Form setup entrypoint
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
