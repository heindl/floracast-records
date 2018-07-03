import abc
from florecords.features.request import FeatureRequest
# Outlines required methods

class BaseFeatureGenerator(object):
    __metaclass__  = abc.ABCMeta

    @abc.abstractproperty
    def schema(self):
        """
        Return an array of schema tuples
        (label, type, required|nullable)
        """

    @abc.abstractmethod
    def fan_out(
            self,
            request, # type: FeatureRequest
    ):
        """
        Yield a new array of requests, generally based on the dates. These will be combined again later.
        """

    @abc.abstractmethod
    def partition_key(
            self,
            request, # type: FeatureRequest
    ):
       """
       Return a key to group feature requests for efficient processing by the generator.
       In most cases, each fetcher will request one date.
       """

    @abc.abstractmethod
    def database_key_from_request(
            self,
            request, # type: FeatureRequest
    ):
        """
       The key with which to match the original record in the database.
       """

    @abc.abstractmethod
    def database_key_from_saved(
            self,
            record, # type: Dictionary
    ):
        """
       The key with which to match the original record in the database.
       """


    @abc.abstractmethod
    def fetch(
            self,
            requests, # type: List[FeatureRequest]
    ):
        """
        Generate new features for each request, and yield each request with the
        new data amended.
        """