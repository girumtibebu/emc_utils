// EMC Utilities - Quotation Form Enhancement
frappe.ui.form.on("Quotation", {
    refresh: function (frm) {
        if (window.emc_utils && window.emc_utils.setup_form_grid_sections) {
            window.emc_utils.setup_form_grid_sections(frm);
        }
    }
});
