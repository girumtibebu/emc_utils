frappe.provide("emc_utils");

(function() {
    console.log("[emc_utils] Initializing EMC Utilities module...");

    emc_utils.install_patches = function() {
        if (!window.frappe || !frappe.ui || !frappe.ui.form) return false;

        if (frappe.ui.form.Grid && !frappe.ui.form.Grid.__emc_patched) {
            const orig_refresh = frappe.ui.form.Grid.prototype.refresh;
            frappe.ui.form.Grid.prototype.refresh = function() {
                orig_refresh.apply(this, arguments);
                emc_utils.setup_grid_buttons(this);
            };
            frappe.ui.form.Grid.__emc_patched = true;
            console.log("[emc_utils] Grid.prototype.refresh patched.");
        }

        if (frappe.ui.form.GridRow && !frappe.ui.form.GridRow.__emc_patched) {
            const orig_render_row = frappe.ui.form.GridRow.prototype.render_row;
            frappe.ui.form.GridRow.prototype.render_row = function(refresh) {
                const res = orig_render_row.apply(this, arguments);
                if (this.doc && this.doc.is_section) {
                    emc_utils.render_section_row(this);
                }
                return res;
            };
            frappe.ui.form.GridRow.__emc_patched = true;
            console.log("[emc_utils] GridRow.prototype.render_row patched.");
        }

        return true;
    };

    emc_utils.setup_form_grid_sections = function(frm) {
        if (!frm || !frm.fields) return;
        emc_utils.install_patches();

        frm.fields.forEach(field => {
            if (field.df && field.df.fieldtype === "Table" && field.grid) {
                emc_utils.setup_grid_buttons(field.grid);

                // Format existing section rows
                if (field.grid.grid_rows) {
                    field.grid.grid_rows.forEach(grid_row => {
                        if (grid_row && grid_row.doc && grid_row.doc.is_section) {
                            emc_utils.render_section_row(grid_row);
                        }
                    });
                }
            }
        });
    };

    emc_utils.setup_grid_buttons = function(grid) {
        if (!grid || !grid.wrapper || !grid.docfields) return;

        const has_section = grid.docfields.some(df => df.fieldname === "is_section");
        if (!has_section) return;

        const is_editable = grid.is_editable ? grid.is_editable() : true;
        if (!is_editable || grid.cannot_add_rows) return;

        // Use Frappe native add_custom_button API
        const btn_label = __("Add Section");
        const $btn = grid.add_custom_button(btn_label, function() {
            emc_utils.add_section_to_grid(grid);
        });

        if ($btn) {
            $btn.addClass("btn-add-section")
                .html(`<svg class="icon icon-sm" style="margin-right: 4px; vertical-align: -2px;"><use href="#icon-layer"></use></svg> ${btn_label}`)
                .css({ "font-weight": "600", "color": "#1e293b", "background-color": "#f1f5f9" });

            // Ensure it sits right next to the standard Add Row button
            const $add_row_btn = grid.wrapper.find(".grid-add-row");
            if ($add_row_btn.length && $btn.parent().length) {
                $btn.insertAfter($add_row_btn);
            }
        }
    };

    emc_utils.add_section_to_grid = function(grid) {
        const new_row = grid.add_new_row(null, null, false, null, true);
        if (new_row) {
            frappe.model.set_value(new_row.doctype, new_row.name, "is_section", 1);
            frappe.model.set_value(new_row.doctype, new_row.name, "section_title", __("New Section"));
            frappe.model.set_value(new_row.doctype, new_row.name, "item_name", __("New Section"));
            frappe.model.set_value(new_row.doctype, new_row.name, "qty", 0);
            frappe.model.set_value(new_row.doctype, new_row.name, "rate", 0);
            frappe.model.set_value(new_row.doctype, new_row.name, "amount", 0);

            grid.refresh();

            setTimeout(() => {
                const grid_row = grid.grid_rows_by_docname && grid.grid_rows_by_docname[new_row.name];
                if (grid_row && grid_row.row) {
                    emc_utils.render_section_row(grid_row);
                    const $inp = grid_row.row.find(".emc-section-input");
                    if ($inp.length) {
                        $inp.focus().select();
                    }
                }
            }, 80);
        }
    };

    emc_utils.render_section_row = function(grid_row) {
        if (!grid_row || !grid_row.row || !grid_row.doc) return;

        grid_row.row.addClass("emc-grid-section-row");

        // Hide data columns, keep sortable drag handles and check
        grid_row.row.find(".col:not(.row-check):not(.row-index):not(.emc-section-cell):not(.btn-open-row-col)")
            .addClass("emc-hidden-col");

        let $cell = grid_row.row.find(".emc-section-cell");
        if (!$cell.length) {
            $cell = $(`
                <div class="col emc-section-cell">
                    <div class="emc-section-inner">
                        <span class="emc-section-tag">${__("SECTION")}</span>
                        <input type="text" class="form-control input-sm emc-section-input" placeholder="${__("Type section heading / title...")}" />
                    </div>
                </div>
            `);

            const $row_index = grid_row.row.find(".row-index");
            if ($row_index.length) {
                $cell.insertAfter($row_index);
            } else {
                grid_row.row.append($cell);
            }
        }

        const current_title = grid_row.doc.section_title || grid_row.doc.item_name || "";
        const $input = $cell.find(".emc-section-input");
        $input.val(current_title);

        $input.off("change.emc blur.emc keydown.emc")
            .on("change.emc blur.emc", function() {
                const val = $(this).val();
                if (grid_row.doc.section_title !== val) {
                    frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "section_title", val);
                    frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "item_name", val);
                    frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "description", val);
                }
            })
            .on("keydown.emc", function(ev) {
                if (ev.key === "Enter") {
                    $(this).blur();
                    ev.preventDefault();
                }
            });
    };

    // Install immediately if ready, or on lifecycle triggers
    emc_utils.install_patches();

    $(document).on("form-refresh", function(e, frm) {
        emc_utils.setup_form_grid_sections(frm);
    });

    $(document).on("grid-row-render", function(e, grid_row) {
        if (grid_row && grid_row.doc && grid_row.doc.is_section) {
            emc_utils.render_section_row(grid_row);
        }
    });

    $(document).on("app_ready startup", function() {
        emc_utils.install_patches();
    });
})();
