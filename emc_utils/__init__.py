__version__ = "1.0.2"

# Initialize monkey patches
try:
    from emc_utils.sections.sections import patch_all
    patch_all()
except Exception:
    pass
