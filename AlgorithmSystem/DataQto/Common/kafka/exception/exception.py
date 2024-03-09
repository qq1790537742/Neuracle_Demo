class CommunicationException(Exception):
    """Base class of communication exceptions"""
    pass

class ConsumerException(CommunicationException):
    """Base class of communication-consumer exception"""
    pass

class TopicNotAvailableException(ConsumerException):
    """Raise when subscribing a topic which is not available"""
    def __init__(self, message):
        self.message = message

class NoConfigFileException(Exception):
    """Raise when there is no such configure file in the param path"""
    pass

class WrongConfigContextException(Exception):
    """Raise when there is no such configure file in the param path"""
    pass

class TopicQueryFailed(Exception):
    """Raise when calling CommunicationInitial.topicQuery method failed"""

    def __init__(self, message):
        self.message = message

class TopicCreateFailed(Exception):
    """Raise when calling CommunicationInitial.topicCreate method failed"""
    def __init__(self, message):
        self.message = message

class TopicDeleteFailed(Exception):
    """Raise when calling CommunicationInitial.topicDelete method failed"""
    def __init__(self, message):
        self.message = message

class ProducerException(CommunicationException):
    """Base class of communication-producer exception"""
    pass

class WrongMessageValueType(ProducerException):
    """Raise when calling CommunicationProducer.send(topic, value) with
        a value param of no-bytes type
    """
    def __init__(self, wrongValueType):
        self.message = "Wrong message type: {}".format(wrongValueType)