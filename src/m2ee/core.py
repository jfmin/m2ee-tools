# Copyright (c) 2009-2015, Mendix bv
# All Rights Reserved.
# http://www.mendix.com/
#

from log import logger

from config import M2EEConfig
from client import M2EEClient


class M2EE():

    def __init__(self):
        self.config = M2EEConfig()
        self.client = M2EEClient(
            self.config.url,
            self.config.password
        )

    def check_alive(self):
        m2ee_alive = self.client.ping()

        if not m2ee_alive:
            logger.error("The application is not accessible for "
                         "administrative requests.")
            logger.error("If this is not caused by a configuration error "
                         "(e.g. wrong admin_port) setting, it could be caused "
                         "by JVM Heap Space / Out of memory errors. Please "
                         "review the application logfiles. In case of JVM "
                         "errors, you should consider restarting the "
                         "application process, because it is likely to be in "
                         "an undetermined broken state right now.")
        return m2ee_alive

    def _configure_logging(self):
        # try configure logging
        # catch:
        # - logsubscriber already exists -> ignore
        #   (TODO:functions to restart logging when config is changed?)
        # - logging already started -> ignore
        logger.debug("Setting up logging...")
        logging_config = self.config.get_logging_config()
        if len(logging_config) == 0:
            logger.warn("No logging settings found, this is probably not what "
                        "you want.")
        else:
            for log_subscriber in logging_config:
                m2eeresponse = self.client.create_log_subscriber(
                    log_subscriber)
                result = m2eeresponse.get_result()
                if result == 3:  # logsubscriber name exists
                    pass
                elif result != 0:
                    m2eeresponse.display_error()
            self.client.start_logging()

    def set_log_level(self, subscriber, node, level):
        params = {"subscriber": subscriber, "node": node, "level": level}
        return self.client.set_log_level(params)

    def get_log_levels(self):
        params = {"sort": "subscriber"}
        m2ee_response = self.client.get_log_settings(params)
        return m2ee_response.get_feedback()
