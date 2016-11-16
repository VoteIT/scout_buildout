# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander
import deform
from arche.views.base import DefaultEditForm
from betahaus.viewcomponent import view_action
from pyramid.response import Response
from pyramid.view import view_config
from voteit.core.models.interfaces import IProposal
from voteit.core.models.proposal import Proposal
from voteit.core.security import MODERATE_MEETING
from voteit.core.security import VIEW


class SupportSchema(colander.Schema):
    widget = deform.widget.FormWidget(
        template='form_modal',
        readonly_template='readonly/form_modal'
    )
    prop_support_for = colander.SchemaNode(
        colander.Integer(),
        title = "Stöd för",
        missing = 0,
        default = 0,
    )
    prop_support_against = colander.SchemaNode(
        colander.Integer(),
        title = "Emot",
        missing = 0,
        default = 0,
    )


@view_config(context=IProposal,
             name='edit_support',
             permission=MODERATE_MEETING,
             renderer='arche:templates/form.pt')
class EditSupportForm(DefaultEditForm):
    use_ajax = True
    ajax_options = """
        {success:
          function (rText, sText, xhr, form) {
            arche.load_flash_messages();
           }
        }
    """

    @property
    def title(self):
        return self.context.title

    def get_schema(self):
        return SupportSchema

    def save_success(self, appstruct):
        self.context.update(**appstruct)
        return _remove_modal_response(self.request)

    def cancel(self, *args):
        return _remove_modal_response(self.request)
    cancel_success = cancel_failure = cancel


def _remove_modal_response(request, *args):
    body="""
<script type="text/javascript">
  arche.destroy_modal();
  arche.load_flash_messages(); //If any from modal interaction
  voteit.load_target('[data-proposals-area]');
</script>"""
    return Response(body=body)


@view_action('metadata_listing', 'prop_support',
             permission = VIEW,
             interface = IProposal,
             priority = 32)
def prop_support_va(context, request, va, **kw):
    output = ""
    if context.prop_support_for or context.prop_support_against:
        output += """
        &nbsp;
        <span class="label label-approved" title="Antal som stödjer förslaget">
            <span class="glyphicon glyphicon-thumbs-up"></span>
            {}
        </span>
        &nbsp;
        <span class="label label-denied">
            <span class="glyphicon glyphicon-thumbs-down"></span>
            {}
        </span>
        """.format(context.prop_support_for, context.prop_support_against)
    if request.is_moderator:
        output += """&nbsp;<a href="{}" title="Redigera stöd" data-open-modal>
            <span class="glyphicon glyphicon-edit"><span></a>
        """.format(request.resource_url(context, 'edit_support'))
    return output


def includeme(config):
    config.scan(__name__)

    def get_prop_support_for(self):
        return self.get_field_value('prop_support_for', 0)
    def set_prop_support_for(self, value):
        self.set_field_value('prop_support_for', int(value))
    Proposal.prop_support_for = property(get_prop_support_for, set_prop_support_for)

    def get_prop_support_against(self):
        return self.get_field_value('prop_support_against', 0)
    def set_prop_support_against(self, value):
        self.set_field_value('prop_support_against', int(value))
    Proposal.prop_support_against = property(get_prop_support_against, set_prop_support_against)
