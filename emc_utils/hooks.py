app_name = "emc_utils"
app_title = "EMC Utilities"
app_publisher = "emc"
app_description = "Universal child table sections, print enhancements, and desk tools"
app_email = "girum@eternal-media.com"
app_license = "mit"

app_include_js = "/assets/emc_utils/js/emc_utils.js"
app_include_css = "/assets/emc_utils/css/emc_utils.css"

doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Order": "public/js/sales_order.js",
}

boot_session = "emc_utils.sections.boot_session"

after_install = "emc_utils.setup.after_install"
after_migrate = "emc_utils.setup.after_migrate"

doc_events = {
    "*": {
        "before_validate": "emc_utils.sections.before_validate_sections",
    }
}

jinja = {
    "methods": [
        "emc_utils.sections.is_section_row",
    ]
}
