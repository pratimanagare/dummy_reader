import getopt
import json
import sys
import time
import os
import opentracing
from opentracing.propagation import Format

from src import func_impl
from src.common.logging_and_tracing import CustomLogging


def main():
    try:
        # Input Setup
        options, args = getopt.getopt(
            sys.argv[1:], "f:c:u:i:o:r:", [
                "funcopt=", "config=", "user_config=","runtime_config=", "input_paths=", "output_path="])
        funcopt = config_json = user_json = runtime_json = input_paths = output_path = ""
        
        for opt, arg in options:
            if opt in ('-f', '--funcopt'):
                funcopt = json.loads(arg)
            elif opt in ('-c', '--config'):
                config_json = json.loads(arg)
            elif opt in ('-u', '--user_config'):
                user_json = json.loads(arg)
            elif opt in ('-i', '--input_paths'):
                input_paths = json.loads(arg)
            elif opt in ('-r', '--runtime'):
                print(arg)
                runtime_json = json.loads(arg)
            elif opt in ('-o', '--output_path'):
                output_path = arg

        if funcopt == "":
            raise Exception('Missing input option -f or funcopt.')

        if config_json == "":
            raise Exception('Missing input option -c or config.')
        
        if user_json == "":
            raise Exception('Missing input option -u or user_config.')

        if runtime_json == "":
            raise Exception('Missing input option -r or runtime.')

        if input_paths == "":
            raise Exception('Missing input option -i or input_paths.')

        if output_path == "":
            raise Exception('Missing input option -o or output_path.')
            
        if not os.path.exists(output_path):
            raise FileNotFoundError(output_path, "does not exist.")
        
        logging_obj = CustomLogging(funcopt)
        logging_obj.create_default_loggers()
#         info_logger = logging_obj.get_logger("info")
        status_logger = logging_obj.get_logger("status")
        error_logger = logging_obj.get_logger("error")
        config_logger = logging_obj.get_logger("config")
        
            
        logging_obj.create_tracer(funcopt['func_name'])
        tracer = logging_obj.get_tracer()

        config_logger.info(config_json)
#         info_logger.info("Function started")
        status_logger.info("Function started")

        parent_span = tracer.extract(format=Format.TEXT_MAP,carrier = funcopt)
        if parent_span:
            span = tracer.start_span('main',references=opentracing.child_of(parent_span))
        else:
            span = tracer.start_span('main')
            
        with tracer.scope_manager.activate(span, True) as scope:
            span.set_tag('', funcopt)
            span.log_kv({'info': 'string-format', 'value': 'Function started'})
            if funcopt['task'] == 'train':
                func_impl.train(logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
            elif funcopt['task'] == 'train_and_validate':
                func_impl.train_and_validate(funcopt, logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
            elif funcopt['task'] == 'validate':
                func_impl.validate(logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
            elif funcopt['task'] == 'test':
                func_impl.test(logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
            elif funcopt['task'] == 'predict':
                func_impl.predict(logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
            else:
                func_impl.run(logging_obj, config_json, user_json, runtime_json, input_paths, output_path)
                
        span.finish()
#         info_logger.info("Function completed successfully")
        status_logger.info("Function completed successfully")
        
    except:
        if 'status_logger' in vars() or 'status_logger' in globals():
            status_logger.exception("Failure")
            error_logger.exception("Failure")
        else:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("ERROR: Class: ", exc_type, " Message :", exc_obj, " Filename: ", fname, "Line No: ", exc_tb.tb_lineno)
            
        sys.exit(100)
    finally:
        if 'status_logger' in vars() or 'status_logger' in globals():
#             info_logger.info("Cleaning up resources..")
            status_logger.info("Cleaning up resources..")

        if 'tracer' in vars() or 'tracer' in globals():
            time.sleep(2)
            tracer.close()
            
        if 'status_logger' in vars() or 'status_logger' in globals():
#             info_logger.info("Main exited")
            status_logger.info("Main exited")


if __name__ == "__main__":
    main()