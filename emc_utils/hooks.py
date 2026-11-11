from emc_utils.constants import SCOPED_DOCTYPES
from emc_utils import __version__

app_name = "emc_utils"
app_title = "EMC Utilities"
app_publisher = "emc"
app_description = "Company switcher, child table sections, print enhancements, and desk tools"
app_email = "girum@eternal-media.com"
app_license = "mit"

required_apps = ["erpnext"]

app_include_js = [
    f"/assets/emc_utils/js/sections.js?v={__version__}",
    f"/assets/emc_utils/js/company_switcher.js?v={__version__}",
]

app_include_css = [
    f"/assets/emc_utils/css/sections.css?v={__version__}",
    f"/assets/emc_utils/css/company_switcher.css?v={__version__}",
]

doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Order": "public/js/sales_order.js",
}

boot_session = "emc_utils.sections.boot_session"

# Company scope list query conditions
_condition = "emc_utils.company_switcher.company_switcher.get_permission_query_conditions"
permission_query_conditions = {doctype: _condition for doctype in SCOPED_DOCTYPES}
permission_query_conditions["*"] = _condition

after_install = "emc_utils.setup.after_install"
after_migrate = "emc_utils.setup.after_migrate"

doc_events = {
    "*": {
        "before_validate": "emc_utils.sections.before_validate_sections",
        "before_print": "emc_utils.sections.before_print_sections",
    }
}

jinja = {
    "methods": [
        "emc_utils.sections.is_section_row",
    ]
}
