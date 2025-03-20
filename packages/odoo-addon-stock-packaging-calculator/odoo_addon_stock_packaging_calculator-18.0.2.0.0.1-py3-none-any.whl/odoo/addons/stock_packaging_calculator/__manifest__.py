# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Stock packaging calculator",
    "summary": "Compute product quantity to pick by packaging",
    "version": "18.0.2.0.0",
    "development_status": "Beta",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product_packaging_calculator"],
    "external_dependencies": {
        "python": [
            "openupgradelib",
        ],
    },
}
