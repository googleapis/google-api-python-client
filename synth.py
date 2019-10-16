import synthtool as s
from synthtool import gcp

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library()
s.move(
    templated_files,
    excludes=[
        "noxfile.py",  # GAPIC library specific
        "CONTRIBUTING.rst",
        "MANIFEST.in",
        "docs/conf.py",
    ],
)
