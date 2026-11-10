// EMC Utilities - Quotation & Sales Order Child Table Section Enhancement

(function () {
    const CSS = `
        .grid-row.emc-grid-section-row {
            background-color: #f1f5f9 !important;
            border-top: 2px solid #94a3b8 !important;
            border-bottom: 2px solid #94a3b8 !important;
            border-left: 4px solid #1e293b !important;
            margin-top: 3px !important;
            margin-bottom: 3px !important;
            min-height: 38px !important;
        }
        .emc-grid-section-row .emc-hidden-col {
            display: none !important;
        }
        .emc-grid-section-row .emc-section-cell {
            flex: 1 1 auto !important;
            display: flex !important;
            align-items: center !important;
            padding: 4px 10px !important;
        }
        .emc-section-inner {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
        }
        .emc-section-tag {
            font-size: 10px !important;
            font-weight: 700 !important;
            letter-spacing: 0.8px !important;
            padding: 2px 7px !important;
            border-radius: 4px !important;
            background: #334155 !important;
            color: #ffffff !important;
            text-transform: uppercase !important;
            user-select: none !important;
            flex-shrink: 0 !important;
        }
        .emc-section-input {
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: #0f172a !important;
            background: transparent !important;
            border: 1px dashed transparent !important;
            box-shadow: none !important;
            height: 28px !important;
            padding: 2px 8px !important;
            width: 100% !important;
            transition: all 0.15s ease-in-out !important;
        }
        .emc-section-input:focus,
        .emc-section-input:hover {
            background: #ffffff !important;
            border: 1px solid #2563eb !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }
        .btn-add-section {
            font-weight: 600 !important;
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            color: #1e293b !important;
            margin-left: 6px !important;
        }
        .btn-add-section:hover {
            background-color: #e2e8f0 !important;
        }
    `;

    frappe.dom.set_style(CSS, "emc_utils_style");

    function format_section_row(grid_row) {
        if (!grid_row || !grid_row.row || !grid_row.doc) return;
        if (!grid_row.doc.is_section) return;

        const $row = grid_row.row;
        $row.addClass("emc-grid-section-row");

        // Hide regular data columns, keep checkbox and row number
        $row.find(".col:not(.row-check):not(.row-index):not(.emc-section-cell):not(.btn-open-row-col)")
            .addClass("emc-hidden-col");

        let $cell = $row.find(".emc-section-cell");
        if (!$cell.length) {
            $cell = $(`
                <div class="col emc-section-cell">
                    <div class="emc-section-inner">
                        <span class="emc-section-tag">${__("SECTION")}</span>
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
        $input.val(title);

        $input.off("change.emc blur.emc keydown.emc")
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
    }

    function format_all_rows(grid) {
        if (!grid || !grid.grid_rows) return;
        grid.grid_rows.forEach(row => format_section_row(row));
    }

    function add_section(grid) {
        const row = grid.add_new_row(null, null, false, null, true);
        if (row) {
            frappe.model.set_value(row.doctype, row.name, "is_section", 1);
            frappe.model.set_value(row.doctype, row.name, "section_title", __("New Section"));
            frappe.model.set_value(row.doctype, row.name, "item_name", __("New Section"));
            frappe.model.set_value(row.doctype, row.name, "qty", 0);
            frappe.model.set_value(row.doctype, row.name, "rate", 0);
            frappe.model.set_value(row.doctype, row.name, "amount", 0);

            grid.refresh();

            setTimeout(() => {
                const grid_row = grid.grid_rows_by_docname && grid.grid_rows_by_docname[row.name];
                if (grid_row && grid_row.row) {
                    format_section_row(grid_row);
                    const $inp = grid_row.row.find(".emc-section-input");
                    if ($inp.length) {
                        $inp.focus().select();
                    }
                }
            }, 80);
        }
    }

    function setup_grid(frm, table_fieldname = "items") {
        if (!frm || !frm.fields_dict || !frm.fields_dict[table_fieldname]) return;
        const grid = frm.fields_dict[table_fieldname].grid;
        if (!grid || !grid.wrapper) return;

        // Add Section button next to Add row
        const $add_row_btn = grid.wrapper.find(".grid-add-row");
        if ($add_row_btn.length && !grid.wrapper.find(".btn-add-section").length) {
            const $btn = $(`
                <button class="btn btn-xs btn-default btn-add-section" type="button">
                    <svg class="icon icon-sm" style="margin-right: 4px; vertical-align: -2px;"><use href="#icon-layer"></use></svg>
                    ${__("Add Section")}
                </button>
            `);

            $btn.insertAfter($add_row_btn);
            $btn.on("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                add_section(grid);
            });
        }

        // Format any existing section rows
        format_all_rows(grid);

        // Hook render_result_rows so sorting and refreshing keeps sections styled
        if (!grid.__emc_hooked) {
            const orig_render = grid.render_result_rows;
            grid.render_result_rows = function () {
                orig_render.apply(this, arguments);
                format_all_rows(this);
            };
            grid.__emc_hooked = true;
        }
    }

    // Export helpers
    window.emc_utils_setup_grid = setup_grid;

    frappe.ui.form.on("Quotation", {
        refresh(frm) {
            setup_grid(frm, "items");
        },
        items_on_form_rendered(frm) {
            setup_grid(frm, "items");
        }
    });

    frappe.ui.form.on("Sales Order", {
        refresh(frm) {
            setup_grid(frm, "items");
        },
        items_on_form_rendered(frm) {
            setup_grid(frm, "items");
        }
    });
})();
