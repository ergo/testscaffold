# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import sqlalchemy as sa
from testscaffold.models.entry import Entry
from ziggurat_foundations.models.base import get_db_session
from ziggurat_foundations.models.services.resource import ResourceService as RService
from paginate_sqlalchemy import SqlalchemyOrmPage

log = logging.getLogger(__name__)


class EntryService(RService):

    @classmethod
    def total_count(cls, db_session=None):
        db_session = get_db_session(db_session)
        return db_session.query(Entry).count()

    @classmethod
    def get_paginator(cls, page=1, item_count=None, items_per_page=50,
                      db_session=None,
                      filter_params=None, **kwargs):
        """ returns paginator over users belonging to the group"""
        if filter_params is None:
            filter_params = {}
        db_session = get_db_session(db_session)
        query = db_session.query(Entry)
        query = query.order_by(Entry.resource_id)
        return SqlalchemyOrmPage(query, page=page, item_count=item_count,
                                 items_per_page=items_per_page,
                                 **kwargs)