# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import request, route

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class CustomerPortalExtended(CustomerPortal):
    @route(
        ["/my/identifications"], type="http", auth="user", website=True, methods=["GET"]
    )
    def identifications(self):
        values = self._prepare_portal_layout_values()
        values["get_error"] = portal.get_error
        values["id_numbers"] = request.env["portal_identification_number"].search(
            [("partner_id", "=", request.env.user.partner_id.id)]
        )

        return request.render(
            "ssi_partner_identification_portal.portal_my_identifications",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/identification", "/my/identification/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def identification(self, **post):
        id = post.get("id")
        category_obj = request.env["res.partner.id_category"].sudo()
        partner_obj = request.env["res.partner"].sudo()
        id_number_obj = request.env["portal_identification_number"]
        values = self._prepare_portal_layout_values()
        error_messages = []
        values.update(
            {
                "error_message": "",
                "category_ids": category_obj.search([]),
                "partner_issued_ids": partner_obj.search([]),
                "current_id_number_id": id_number_obj,
            }
        )
        current_id_number_id = id_number_obj
        values["status_list"] = id_number_obj._fields["status"].selection
        if id:
            id = int(id)
            current_id_number_id = id_number_obj.search([("id", "=", id)])
            values.update(
                {
                    "current_id_number_id": current_id_number_id,
                }
            )

        if request.httprequest.method == "POST":
            category_id = category_obj.search(
                [("id", "=", int(post.get("category", "0")))]
            )
            if not category_id:
                error_messages.append("Category not found.")
            id_number_vals = {
                "partner_id": request.env.user.partner_id.id,
                "category_id": category_id.id,
                "name": post.get("name"),
                "date_issued": post.get("date_issued") or False,
                "place_issuance": post.get("place_issuance"),
                "valid_from": post.get("valid_from") or False,
                "valid_until": post.get("valid_until") or False,
                "status": post.get("status"),
                "comment": post.get("comment"),
            }
            if post.get("partner_issued"):
                partner_issued_id = partner_obj.sudo().search(
                    [("id", "=", int(post.get("partner_issued", "0")))]
                )
                if not partner_issued_id:
                    error_messages.append("Issued partner not found.")
                id_number_vals.update(
                    {
                        "partner_issued_id": partner_issued_id.id,
                    }
                )
            if error_messages:
                values["error_message"] = "\n".join(error_messages)
                return request.render(
                    "ssi_partner_identification_portal.portal_my_identification",
                    values,
                    headers={"X-Frame-Options": "DENY"},
                )
            if not current_id_number_id:
                id_number_obj.create(id_number_vals)
            else:
                current_id_number_id.write(id_number_vals)
            return request.redirect("/my/identifications")

        return request.render(
            "ssi_partner_identification_portal.portal_my_identification",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/identification/remove/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def remove_identification(self, **post):
        id = post.get("id")
        id_number_id = request.env["portal_identification_number"].search(
            [("id", "=", int(id))]
        )
        id_number_id.unlink()
        return request.redirect("/my/identifications")
