# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Company Partner's Public Offering Information",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_master_data_mixin",
        "ssi_partner",
    ],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "views/company_public_offering_type_views.xml",
        "views/res_partner_views.xml",
    ],
    "demo": [],
}
