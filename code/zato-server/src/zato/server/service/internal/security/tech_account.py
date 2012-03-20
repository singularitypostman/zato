# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster, TechnicalAccount
from zato.common.odb.query import tech_acc_list
from zato.common.util import tech_account_password
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of technical accounts defined in the ODB. The items are
    sorted by the 'name' attribute.
    """
    class SimpleIO:
        input_required = ('cluster_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            
            definition_list = Element('definition_list')
            definitions = tech_acc_list(session, self.request.input.cluster_id, False)
            
            for definition in definitions:
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
    
                definition_list.append(definition_elem)
    
            self.response.payload = etree.tostring(definition_list)
    
class GetByID(AdminService):
    """ Returns a technical account of a given ID.
    """
    class SimpleIO:
        input_required = ('tech_account_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            tech_account = session.query(TechnicalAccount.id, 
                TechnicalAccount.name, TechnicalAccount.is_active).\
                filter(TechnicalAccount.id==self.request.input.tech_account_id).\
                one()
            
            tech_account_elem = Element('tech_account')
            tech_account_elem.id = tech_account.id;
            tech_account_elem.name = tech_account.name;
            tech_account_elem.is_active = tech_account.is_active;
            
            self.response.payload = etree.tostring(tech_account_elem)
    
class Create(AdminService):
    """ Creates a new technical account.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active')

    def handle(self):
        salt = uuid4().hex
        input = self.request.input
        input.password = tech_account_password(uuid4().hex, salt)
        
        with closing(self.odb.session()) as session:
            cluster = session.query(Cluster).filter_by(id=cluster_id).first()
            
            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==input.cluster_id).\
                filter(TechnicalAccount.name==input.name).first()
            
            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(input.name))
            
            tech_account_elem = Element('tech_account')
            
            try:
                tech_account = TechnicalAccount(None, input.name, input.is_active, input.password, salt, cluster=cluster)
                session.add(tech_account)
                session.commit()
                
                tech_account_elem.id = tech_account.id
                
            except Exception, e:
                msg = 'Could not create a technical account, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.TECH_ACC_CREATE
                input.password = password
                input.sec_type = 'tech_acc'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            self.response.payload = etree.tostring(tech_account_elem)

class Edit(AdminService):
    """ Updates an existing technical account.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'tech_account_id', 'name', 'is_active')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==input.cluster_id).\
                filter(TechnicalAccount.name==input.name).\
                filter(TechnicalAccount.id!=input.tech_account_id).\
                first()
            
            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(input.name))
            
            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==input.tech_account_id).\
                one()
            old_name = tech_account.name
            
            tech_account.name = name
            tech_account.is_active = input.is_active

            tech_account_elem = Element('tech_account')            
            
            try:
                session.add(tech_account)
                session.commit()

                tech_account_elem.id = tech_account.id                
                
            except Exception, e:
                msg = "Could not update the technical account, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            else:
                input.action = SECURITY.TECH_ACC_EDIT
                input.old_name = old_name
                input.sec_type = 'tech_acc'
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
            
            self.response.payload = etree.tostring(tech_account_elem)
    
class ChangePassword(ChangePasswordBase):
    """ Changes the password of a technical account.
    """
    def handle(self):
        salt = uuid4().hex
        def _auth(instance, password):
            instance.password = tech_account_password(password, salt)
            instance.salt = salt

        return self._handle(TechnicalAccount, _auth, 
                            SECURITY.TECH_ACC_CHANGE_PASSWORD, salt=salt)
    
class Delete(AdminService):
    """ Deletes a technical account.
    """
    class SimpleIO:
        input_required = ('tech_account_id', 'zato_admin_tech_account_name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==input.tech_account_id).\
                one()
            
            if tech_account.name == input.zato_admin_tech_account_name:
                msg = "Can't delete account [{0}], at least one client console uses it".\
                    format(input.zato_admin_tech_account_name)
                raise Exception(msg)
            
            try:
                session.delete(tech_account)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the account, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise
            else:
                input.action = SECURITY.TECH_ACC_DELETE
                input.name = tech_account.name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
