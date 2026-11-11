// EMC Utilities - Sales Order Form Enhancement
frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        if (window.emc_utils && window.emc_utils.setup_form_grid_sections) {
            window.emc_utils.setup_form_grid_sections(frm);
        }
    }
});
