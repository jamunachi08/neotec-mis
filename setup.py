from setuptools import setup, find_packages

setup(
    name="neotec_mis",
    version="0.1.0",
    description="Neotec MIS Builder - Advanced MIS and financial report format builder for ERPNext/Frappe v15+ and v16+.",
    author="Neotec / IRSAA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
