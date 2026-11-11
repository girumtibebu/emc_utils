__version__ = "0.0.1"

# Initialize monkey patches
try:
    from emc_utils.sections.sections import patch_all
    patch_all()
except Exception:
    pass
