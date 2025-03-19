# -*- coding: utf-8 -*-
from pip_services4_components.refer import Descriptor
from pip_services4_components.build import Factory

from aichatchatting.topics.logic.TopicsService import TopicsService
from aichatchatting.topics.persistence.TopicsMemoryPersistence import TopicsMemoryPersistence
from aichatchatting.topics.persistence.TopicsMongoDbPersistence import TopicsMongoDbPersistence
from aichatchatting.chatprocessor.logic.BasicService import BasicService


class AIChatChattingFactory(Factory):
    __MemoryPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'memory', '*', '1.0')
    __MongoDbPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'mongodb', '*', '1.0')
    __ServiceDescriptor = Descriptor('aichatchatting-topics', 'service', 'default', '*', '1.0')

    __ChatprocessorServiceDescriptor = Descriptor("aichatchatting-chatprocessor", "service", "*", "*", "1.0")


    def __init__(self):
        super().__init__()

        self.register_as_type(self.__MemoryPersistenceDescriptor, TopicsMemoryPersistence)
        self.register_as_type(self.__MongoDbPersistenceDescriptor, TopicsMongoDbPersistence)
        self.register_as_type(self.__ServiceDescriptor, TopicsService)

        self.register_as_type(self.__ChatprocessorServiceDescriptor, BasicService)
