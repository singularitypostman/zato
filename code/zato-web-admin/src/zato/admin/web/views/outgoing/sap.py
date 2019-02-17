# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sap import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, \
     Index as _Index, method_allowed
from zato.common import SAP
from zato.common.odb.model import OutgoingSAP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-sap'
    template = 'zato/outgoing/sap.html'
    service_name = 'zato.outgoing.sap.get-list'
    output_class = OutgoingSAP

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', 'sysnr', 'sysid', 'user', 'client', 'router', 'pool_size')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'default_instance': SAP.DEFAULT.INSTANCE,
            'default_pool_size': SAP.DEFAULT.POOL_SIZE,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'sysnr', 'user', 'sysid', 'client', 'router', 'pool_size')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the outgoing SAP RFC connection [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'out-sap-create'
    service_name = 'zato.outgoing.sap.create'

class Edit(_CreateEdit):
    url_name = 'out-sap-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.sap.edit'

class Delete(_Delete):
    url_name = 'out-sap-delete'
    error_message = 'Could not delete the outgoing SAP RFC connection'
    service_name = 'zato.outgoing.sap.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.sap.change-password')

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.outgoing.sap.ping', id, 'Could not ping the SAP RFC connection, e:`{}`')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)
