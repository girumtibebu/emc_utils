frappe.provide("emc_utils");

emc_utils.setup_grid_sections = function(grid) {
    if (!grid || !grid.docfields) return;

    const has_section_field = grid.docfields.some(df => df.fieldname === "is_section");
    if (!has_section_field) return;

    // Check if grid is editable
    const is_editable = grid.is_editable && grid.is_editable();
    if (!is_editable || grid.cannot_add_rows) return;

    // Inject 'Add Section' button if not already present
    const $add_row_btn = grid.wrapper.find(".grid-add-row");
    if ($add_row_btn.length && !grid.wrapper.find(".grid-add-section").length) {
        const $btn = $(`
            <button class="btn btn-xs btn-default grid-add-section mr-2" type="button" style="font-weight: 500;">
                <svg class="icon icon-sm" style="margin-right: 4px; vertical-align: -2px;"><use href="#icon-layer"></use></svg>
                ${__("Add Section")}
            </button>
        `);
        $btn.insertAfter($add_row_btn);

        $btn.on("click", function(e) {
            e.preventDefault();
            e.stopPropagation();

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
                        const $inp = grid_row.row.find(".emc-section-input");
                        if ($inp.length) {
                            $inp.focus().select();
                        }
                    }
                }, 100);
            }
        });
    }
};

emc_utils.render_section_row = function(grid_row) {
    if (!grid_row || !grid_row.row || !grid_row.doc) return;

    grid_row.row.addClass("emc-grid-section-row");

    // Hide standard columns except index and check (so drag & drop works cleanly)
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

// Hook into Frappe Grid refresh & render
(function() {
    if (frappe.ui && frappe.ui.form && frappe.ui.form.Grid) {
        const orig_refresh = frappe.ui.form.Grid.prototype.refresh;
        frappe.ui.form.Grid.prototype.refresh = function() {
            orig_refresh.apply(this, arguments);
            emc_utils.setup_grid_sections(this);
        };
    }

    $(document).on("grid-row-render", function(e, grid_row) {
        if (grid_row && grid_row.doc && grid_row.doc.is_section) {
            emc_utils.render_section_row(grid_row);
        }
    });
})();
