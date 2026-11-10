// EMC Utilities - Quotation Client Script
frappe.ui.form.on("Quotation", {
    refresh(frm) {
        if (window.emc_utils?.setup_form_grid_sections) {
            window.emc_utils.setup_form_grid_sections(frm);
        }
    },
    items_on_form_rendered(frm) {
        if (window.emc_utils?.setup_form_grid_sections) {
            window.emc_utils.setup_form_grid_sections(frm);
        }
    }
});
