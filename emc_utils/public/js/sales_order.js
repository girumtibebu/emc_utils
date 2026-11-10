frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (window.emc_utils) {
            window.emc_utils.setup_form_grid_sections(frm);
        }
    }
});
