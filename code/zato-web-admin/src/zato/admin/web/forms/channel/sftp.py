# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_services, add_topics
from zato.common import SFTP

_default = SFTP.CHANNEL.DEFAULT

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:22%'}), initial=_default.ADDRESS)

    service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    topic_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    idle_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=_default.IDLE_TIMEOUT)
    keep_alive_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=_default.KEEP_ALIVE_TIMEOUT)

    host_key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    sftp_command = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.SFTP_COMMAND)

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_services(self, req)
        add_topics(self, req, by_id=False)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())