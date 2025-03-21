from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable
from pip_services4_observability.log import CompositeLogger
from pip_services4_observability.count import CompositeCounters

from ..data import RequestV1, ResponseV1
from ..logic import IBasicService


class BasicService(IBasicService, IConfigurable, IReferenceable):
    """
    Implements the business logic operations of the controller.
    """

    def __init__(self):
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._default_response = ''

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: Configuration parameters to be set.
        """
        self._logger.configure(config)
        self._default_response = config.get_as_string_with_default('configuration.response', self._default_response)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: References to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)

    def do_something(self, context: Optional[IContext], request: RequestV1) -> ResponseV1:
        """
        Some API function of module.

        :param context: The context.
        :param request: A request object.
        :return: A response object.
        """
        response = ResponseV1()
        response.value = self._default_response

        if request is not None:
            response.value = request.value or self._default_response
            self._logger.info(context, f"Processed request: {response.value}")
        else:
            err = ValueError("NullPointerException")
            self._logger.error(context, err, "Processed null request")
            raise err

        self._counters.increment_one('basic.did_something')
        return response