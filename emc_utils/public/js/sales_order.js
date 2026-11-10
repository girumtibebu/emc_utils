// EMC Utilities - Sales Order Client Script
frappe.ui.form.on("Sales Order", {
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
