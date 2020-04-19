import pandas as pd
import os
import time
import pickle

def run(logging_obj, config_json, user_json, runtime_json, input_paths, output_path):
    data=pd.read_csv(input_paths[0])
    for i in range(config_json["loop"]):
        time.sleep(config_json["sleep_time"])
        info_logger=logging_obj.get_logger("info")
        info_logger.info("looping round %d"%i)
    output_path=os.path.join(output_path,"sample_data.pickle")
    with open(output_path, "wb") as out_file:
        pickle.dump(data, out_file)