# -*- coding: utf-8 -*-
"""
    pip_services4_mongodb.build.DefaultMongoDbFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor

from pip_services4_mongodb.connect.MongoDbConnection import MongoDbConnection


class DefaultMongoDbFactory(Factory):
    """
    Creates MongoDb components by their descriptors.
    See :class:`Factory <pip_services4_components.build.Factory.Factory>`, :class:`MongoDbConnection <pip_services4_mongodb.persistence.MongoDbConnection.MongoDbConnection>`
    """
    MongoDbConnectionDescriptor: Descriptor = Descriptor("pip-services", "connection", "mongodb", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super(DefaultMongoDbFactory, self).__init__()
        self.register_as_type(DefaultMongoDbFactory.MongoDbConnectionDescriptor, MongoDbConnection)
