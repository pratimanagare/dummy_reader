import logging
from jaeger_client import Config
import logging.config
from pythonjsonlogger import jsonlogger
import os

class CustomLogging:
    
    def __init__(self,funcopt):
        self.funcopt=funcopt
        self.switcher = {}
        
    def create_default_loggers(self):
        logging.config.fileConfig('conf/logging.ini', disable_existing_loggers=False)
        
        format_str = '%(message)%(levelname)%(name)%(asctime)'
        json_formatter = jsonlogger.JsonFormatter(format_str)

        log_dir = os.path.join(self.funcopt['app_home'],
                               "logs",
                              self.funcopt['uuid'],
                              self.funcopt['func_name'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        info_logger = logging.getLogger("info")
        info_handler = logging.FileHandler(os.path.join(log_dir, "info.log"))
        info_handler.setFormatter(json_formatter)
        info_logger.addHandler(info_handler)
        info_logger = logging.LoggerAdapter(info_logger, self.funcopt)

        error_logger = logging.getLogger("error")
        error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"))
        error_handler.setFormatter(json_formatter)
        error_logger.addHandler(error_handler)
        error_logger = logging.LoggerAdapter(error_logger, self.funcopt)

        status_logger = logging.getLogger("status")
        status_handler = logging.FileHandler(os.path.join(log_dir, "status.log"))
        status_handler.setFormatter(json_formatter)
        status_logger.addHandler(status_handler)
        status_logger = logging.LoggerAdapter(status_logger, self.funcopt)

        config_logger = logging.getLogger("config")
        config_handler = logging.FileHandler(os.path.join(log_dir, "config.log"))
        config_handler.setFormatter(json_formatter)
        config_logger.addHandler(config_handler)
        config_logger = logging.LoggerAdapter(config_logger, self.funcopt)

        self.switcher["info"]=info_logger
        self.switcher["status"]=status_logger
        self.switcher["error"]=error_logger
        self.switcher["config"]=config_logger
    
    def get_logger(self, name):
        return self.switcher.get(name, "No such logger exists.")

    def create_logger(self, logger_name, log_file, level=logging.INFO):
        if logger_name in self.switcher.keys():
            raise Exception("Logger already exists! To setup logger, please call setup_logger().")
            
        logger = logging.getLogger(logger_name)
        format_str = '%(message)%(levelname)%(name)%(asctime)'
        json_formatter = jsonlogger.JsonFormatter(format_str)
        
        fileHandler = logging.FileHandler(log_file, mode='w')
        fileHandler.setFormatter(json_formatter)
        logger.setLevel(level)
        logger.addHandler(fileHandler)
        self.switcher[logger_name]=logger
        
    #Jaeger tracer
    def init_tracer(self, service):
        logging.getLogger('').handlers = []
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)

        config = Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'logging': True,
            },
            service_name=service,
        )
        return config.initialize_tracer()

    def create_tracer(self, algo_name):
        self.tracer = self.init_tracer(algo_name)
    
    def get_tracer(self):
        return self.tracer