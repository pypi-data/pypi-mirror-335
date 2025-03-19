# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import request, route

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class CustomerPortalExtended(CustomerPortal):
    @route(["/my/academics"], type="http", auth="user", website=True, methods=["GET"])
    def academics(self):
        values = self._prepare_portal_layout_values()
        values["get_error"] = portal.get_error
        values["academic_ids"] = request.env["portal_partner_academic"].search(
            [("partner_id", "=", request.env.user.partner_id.id)]
        )

        return request.render(
            "ssi_partner_experience_portal.portal_my_academics",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/academic", "/my/academic/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def academic(self, **post):
        id = post.get("id")
        partner_obj = request.env["res.partner"].sudo()
        academic_obj = request.env["portal_partner_academic"]
        education_level_obj = request.env["partner.formal_education_level"]
        field_of_study_obj = request.env["partner.field_of_study"]
        values = self._prepare_portal_layout_values()
        error_messages = []
        values.update(
            {
                "error_message": "",
                "partner_address_ids": partner_obj.search([("is_company", "=", True)]),
                "education_level_ids": education_level_obj.search([]),
                "field_of_study_ids": field_of_study_obj.search([]),
                "current_academic_id": academic_obj,
            }
        )
        current_academic_id = academic_obj
        if id:
            id = int(id)
            current_academic_id = academic_obj.search([("id", "=", id)])
            values.update(
                {
                    "current_academic_id": current_academic_id,
                }
            )

        if request.httprequest.method == "POST":
            academic_vals = {
                "partner_id": request.env.user.partner_id.id,
                "location": post.get("location"),
                "date_start": post.get("date_start") or False,
                "expire": post.get("expire"),
                "date_end": post.get("date_end") or False,
                "diploma": post.get("diploma"),
                "gpa": post.get("gpa"),
                "activities": post.get("activities"),
                "note": post.get("note"),
            }
            if post.get("partner_address"):
                partner_address_id = partner_obj.sudo().search(
                    [("id", "=", int(post.get("partner_address", "0")))]
                )
                if not partner_address_id:
                    error_messages.append("Institution not found.")
                academic_vals.update(
                    {
                        "partner_address_id": partner_address_id.id,
                    }
                )
            if post.get("education_level"):
                education_level_id = education_level_obj.sudo().search(
                    [("id", "=", int(post.get("education_level", "0")))]
                )
                if not education_level_id:
                    error_messages.append("Education level not found.")
                academic_vals.update(
                    {
                        "education_level_id": education_level_id.id,
                    }
                )
            if post.get("field_of_study"):
                field_of_study_id = field_of_study_obj.sudo().search(
                    [("id", "=", int(post.get("field_of_study", "0")))]
                )
                if not field_of_study_id:
                    error_messages.append("Field of Study not found.")
                academic_vals.update(
                    {
                        "field_of_study_id": field_of_study_id.id,
                    }
                )
            if error_messages:
                values["error_message"] = "\n".join(error_messages)
                return request.render(
                    "ssi_partner_experience_portal.portal_my_academic",
                    values,
                    headers={"X-Frame-Options": "DENY"},
                )
            if not current_academic_id:
                academic_obj.create(academic_vals)
            else:
                current_academic_id.write(academic_vals)
            return request.redirect("/my/academics")

        return request.render(
            "ssi_partner_experience_portal.portal_my_academic",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/academic/remove/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def remove_academic(self, **post):
        id = post.get("id")
        academic_id = request.env["portal_partner_academic"].search(
            [("id", "=", int(id))]
        )
        academic_id.unlink()
        return request.redirect("/my/academics")

    @route(["/my/experiences"], type="http", auth="user", website=True, methods=["GET"])
    def experiences(self):
        values = self._prepare_portal_layout_values()
        values["get_error"] = portal.get_error
        values["experience_ids"] = request.env["portal_partner_experience"].search(
            [("partner_id", "=", request.env.user.partner_id.id)]
        )

        return request.render(
            "ssi_partner_experience_portal.portal_my_experiences",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/experience", "/my/experience/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def experience(self, **post):
        id = post.get("id")
        partner_obj = request.env["res.partner"].sudo()
        experience_obj = request.env["portal_partner_experience"]
        values = self._prepare_portal_layout_values()
        error_messages = []
        values.update(
            {
                "error_message": "",
                "partner_address_ids": partner_obj.search([("is_company", "=", True)]),
                "current_experience_id": experience_obj,
            }
        )
        current_experience_id = experience_obj
        if id:
            id = int(id)
            current_experience_id = experience_obj.search([("id", "=", id)])
            values.update(
                {
                    "current_experience_id": current_experience_id,
                }
            )

        if request.httprequest.method == "POST":
            experience_vals = {
                "partner_id": request.env.user.partner_id.id,
                "job_position": post.get("job_position"),
                "job_level": post.get("job_level"),
                "location": post.get("location"),
                "date_start": post.get("date_start") or False,
                "expire": post.get("expire"),
                "date_end": post.get("date_end") or False,
                "note": post.get("note"),
            }
            if post.get("partner_address"):
                partner_address_id = partner_obj.sudo().search(
                    [("id", "=", int(post.get("partner_address", "0")))]
                )
                if not partner_address_id:
                    error_messages.append("Institution not found.")
                experience_vals.update(
                    {
                        "partner_address_id": partner_address_id.id,
                    }
                )
            if error_messages:
                values["error_message"] = "\n".join(error_messages)
                return request.render(
                    "ssi_partner_experience_portal.portal_my_experience",
                    values,
                    headers={"X-Frame-Options": "DENY"},
                )
            if not current_experience_id:
                experience_obj.create(experience_vals)
            else:
                current_experience_id.write(experience_vals)
            return request.redirect("/my/experiences")

        return request.render(
            "ssi_partner_experience_portal.portal_my_experience",
            values,
            headers={"X-Frame-Options": "DENY"},
        )

    @route(
        ["/my/experience/remove/<int:id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def remove_experience(self, **post):
        id = post.get("id")
        experience_id = request.env["portal_partner_experience"].search(
            [("id", "=", int(id))]
        )
        experience_id.unlink()
        return request.redirect("/my/experiences")
