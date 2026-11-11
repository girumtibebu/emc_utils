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
            width: calc(100% - 71px) !important;
            max-width: none !important;
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

        /* Frappe UI / Espresso Badge for Section - Prevent any truncation or constraints */
        .emc-section-badge,
        .emc-section-badge span,
        .emc-section-badge .es-badge__label {
            width: auto !important;
            min-width: unset !important;
            max-width: none !important;
            display: inline-flex !important;
            align-items: center !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        .emc-section-badge {
            cursor: default !important;
            flex-shrink: 0 !important;
            letter-spacing: 0.04em !important;
            font-weight: 600 !important;
            user-select: none !important;
        }

        [data-theme="dark"] .emc-section-badge,
        .dark .emc-section-badge {
            background-color: var(--surface-gray-4, #334155) !important;
            color: var(--text-color, #f1f5f9) !important;
            border: 1px solid var(--outline-gray-2, #475569) !important;
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
            max-width: none !important;
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

        /* Read-only / Submitted Document Section Title */
        .emc-section-input[readonly],
        .emc-section-input:disabled {
            background: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
            cursor: default !important;
            pointer-events: none !important;
            user-select: text !important;
        }

        /* Responsive Mobile Layout */
        @media (max-width: 768px) {
            .data-row.emc-grid-section-row .emc-section-cell {
                left: 36px !important;
                width: calc(100% - 36px) !important;
                padding: 2px 8px !important;
            }
            .emc-section-inner {
                gap: 8px !important;
            }
            .emc-section-input {
                font-size: 13px !important;
                min-width: 130px !important;
                padding: 2px 6px !important;
            }
            .emc-section-badge {
                font-size: 9px !important;
                padding: 1px 5px !important;
            }
            .grid-buttons {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 6px !important;
            }
            .grid-buttons .grid-add-section,
            .grid-buttons .grid-add-row {
                flex: 1 1 auto !important;
                text-align: center !important;
                min-width: 100px !important;
            }
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

            let badge_html = "";
            if (frappe.ui?.badge?.html) {
                badge_html = frappe.ui.badge.html({
                    label: __("SECTION"),
                    theme: "gray",
                    size: "sm",
                    variant: "solid",
                    css_class: "emc-section-badge",
                });
            } else {
                badge_html = `<span class="es-badge emc-section-badge" data-size="sm" data-variant="solid"><span class="es-badge__label">${__("SECTION")}</span></span>`;
            }

            let title = grid_row.doc.section_title || grid_row.doc.item_name || grid_row.doc.description || "";

            if (!grid_row.doc.section_title && title) {
                grid_row.doc.section_title = title;
                grid_row.doc.item_name = title;
                grid_row.doc.description = title;
            }

            let $cell = $row.find(".emc-section-cell");
            if (!$cell.length) {
                $cell = $(`
                    <div class="emc-section-cell">
                        <div class="emc-section-inner">
                            ${badge_html}
                            <input type="text" class="form-control emc-section-input" value="${frappe.utils.escape_html(title)}" placeholder="${__("Section Title...")}">
                        </div>
                    </div>
                `);

                $row.append($cell);
            } else {
                const $inp = $cell.find(".emc-section-input");
                if ($inp.length && $inp.val() !== title && !$inp.is(":focus")) {
                    $inp.val(title);
                }
            }

            const is_row_editable =
                !grid_row.grid?.df?.read_only &&
                (!grid_row.doc || grid_row.doc.docstatus === 0) &&
                (!grid_row.frm || (!grid_row.frm.is_read_only() && grid_row.frm.doc.docstatus === 0)) &&
                (typeof grid_row.grid?.is_editable === "function" ? grid_row.grid.is_editable() : true);

            const $section_input = $cell.find(".emc-section-input");
            if (!is_row_editable) {
                $section_input.prop("readonly", true).prop("disabled", true);
            } else {
                $section_input.prop("readonly", false).prop("disabled", false);
            }

            // Bind input and keyboard events strictly to the current row doc
            $cell
                .off("click.emc mousedown.emc")
                .on("click.emc mousedown.emc", function (e) {
                    e.stopPropagation();
                });

            $cell
                .find(".emc-section-input")
                .off("input.emc blur.emc change.emc keydown.emc")
                .on("input.emc blur.emc change.emc", function () {
                    const val = $(this).val();
                    grid_row.doc.section_title = val;
                    grid_row.doc.item_name = val;
                    grid_row.doc.description = val;

                    if (grid_row.frm) {
                        grid_row.frm.dirty();
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
        if (!grid || !grid.wrapper || !grid.df) return;

        // Intercept frm.print_doc so dirty changes (sections & rows) are saved before switching to print preview
        if (grid.frm && !grid.frm.__emc_print_doc_hooked) {
            const orig_print_doc = grid.frm.print_doc;
            grid.frm.print_doc = function () {
                if (this.is_dirty()) {
                    return this.save().then(() => {
                        orig_print_doc.apply(this, arguments);
                    });
                }
                return orig_print_doc.apply(this, arguments);
            };
            grid.frm.__emc_print_doc_hooked = true;
        }

        const $grid_buttons = grid.wrapper.find(".grid-buttons");
        if (!$grid_buttons.length) return;

        let $btn = $grid_buttons.find(".grid-add-section");
        const $add_row = $grid_buttons.find(".grid-add-row");

        const is_editable =
            !grid.df.read_only &&
            !grid.cannot_add_rows &&
            (!grid.frm || (!grid.frm.is_read_only() && grid.frm.doc && grid.frm.doc.docstatus === 0)) &&
            (typeof grid.is_editable === "function" ? grid.is_editable() : true);

        const add_row_hidden =
            !$add_row.length ||
            $add_row.is(":hidden") ||
            $add_row.hasClass("hidden") ||
            $add_row.hasClass("d-none") ||
            $add_row.css("display") === "none";

        if (!is_editable || add_row_hidden) {
            if ($btn.length) {
                $btn.addClass("hidden d-none").hide();
            }
            return;
        }

        if (!$btn.length) {
            let btn_html = "";
            if (frappe.ui?.button?.html) {
                btn_html = frappe.ui.button.html({
                    label: __("Add section"),
                    size: "sm",
                    css_class: "grid-add-section",
                });
            } else {
                btn_html = `<button class="btn es-button btn-xs btn-secondary grid-add-section" type="button">${__("Add section")}</button>`;
            }

            $btn = $(btn_html);

            const $add_multiple = $grid_buttons.find(".grid-add-multiple-rows");

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

        $btn.removeClass("hidden d-none").show();
    };

    // 5. Add section row with safe default values
    emc.add_section = function (grid) {
        const row = grid.add_new_row(null, null, false, null, true);
        if (row) {
            row.is_section = 1;
            row.section_title = __("New Section");
            row.item_name = __("New Section");
            row.description = __("New Section");
            row.qty = 0;
            row.rate = 0;
            row.amount = 0;
            row.uom = "Unit";
            row.conversion_factor = 1;

            if (grid.frm) {
                grid.frm.dirty();
            }

            grid.refresh();

            setTimeout(() => {
                const grid_row = grid.grid_rows_by_docname && row.name && grid.grid_rows_by_docname[row.name];
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
