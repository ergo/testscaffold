# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from datetime import datetime

import pyramid.httpexceptions

from ziggurat_foundations.models.services.user_permission import \
    UserPermissionService

from testscaffold.util import safe_integer
from testscaffold.models.user_permission import UserPermission
from testscaffold.services.user import UserService
from testscaffold.validation.schemes import UserSearchSchema

USERS_PER_PAGE = 50


log = logging.getLogger(__name__)


class UsersShared(object):
    """
    Used by API and admin views
    """

    def __init__(self, request):
        self.request = request
        self.page = None

    def collection_list(self):
        request = self.request
        self.page = safe_integer(request.GET.get('page', 1))
        filter_params = UserSearchSchema().load(request.GET.mixed()).data
        user_paginator = UserService.get_paginator(
            page=self.page,
            items_per_page=USERS_PER_PAGE,
            # url_maker gets passed to SqlalchemyOrmPage
            url_maker=lambda p: request.current_route_url(_query={"page": p}),
            filter_params=filter_params,
            db_session=request.dbsession
        )
        return user_paginator

    def user_get(self, user_id):
        request = self.request
        user = UserService.by_id(safe_integer(user_id),
                                 db_session=request.dbsession)
        if not user:
            raise pyramid.httpexceptions.HTTPNotFound()

        return user

    def populate_instance(self, instance, data):
        # this is safe and doesn't overwrite user_password with cleartext
        instance.populate_obj(data)
        log.info('user_populate_instance',
                 extra={'action': 'updated',
                        'x': datetime.now(),
                        'y': datetime.utcnow().date(),
                        'user_id': instance.id})
        if data.get('password'):
            # set hashed password
            instance.set_password(data['password'])
            log.info('user_GET_PATCH', extra={'action': 'password_updated'})

    def delete(self, instance):
        log.info('user_delete', extra={'user_id': instance.id,
                                       'user_name': instance.user_name})
        instance.delete(self.request.dbsession)
        self.request.session.flash({'msg': 'User removed.',
                                    'level': 'success'})

    def permission_get(self, user, permission):
        permission = UserPermissionService.by_user_and_perm(
            user.id, permission, db_session=self.request.dbsession)
        if not permission:
            raise pyramid.httpexceptions.HTTPNotFound()
        return permission

    def permission_post(self, user, permission):
        try:
            self.permission_get(user, permission)
        except pyramid.httpexceptions.HTTPNotFound:
            log.info('user_permission_post',
                     extra={'user_id': user.id,
                            'user_name': user.user_name,
                            'permission': permission})
            permission_inst = UserPermission(perm_name=permission)
            user.user_permissions.append(permission_inst)
            self.request.session.flash({'msg': 'Permission granted for user.',
                                        'level': 'success'})
        return permission

    def permission_delete(self, user, permission):
        permission_inst = UserPermissionService.by_user_and_perm(
            user.id, permission.perm_name, db_session=self.request.dbsession)
        if permission_inst:
            log.info('user_permission_delete',
                     extra={'user_id': user.id,
                            'user_name': user.user_name,
                            'permission': permission})
            user.user_permissions.remove(permission_inst)
            self.request.session.flash(
                {'msg': 'Permission withdrawn from user.',
                 'level': 'success'})