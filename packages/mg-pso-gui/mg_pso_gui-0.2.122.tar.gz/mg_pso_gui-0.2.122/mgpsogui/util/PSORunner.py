
import sys
from multiprocessing import Process, Queue
from queue import Empty
import threading
import time
import os
from .recosu.sampling.sampling import run_sampler
from .recosu.pso import global_best
from csip import Client
import traceback
import urllib
import shutil
import json
import numpy as np

ZERO_BEST = [
    'rmse',
    'trmse',
    'pbias'
]

POSITIVE_BEST = [
    'kge',
    'nslog',
    'nslog1p',
    'ns'
]

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def run_process(stdout_queue, stderr_queue, results_queue, data, folder, mode):
    """_summary_

    Args:
        stdout_queue (_type_): _description_
        stderr_queue (_type_): _description_
        results_queue (_type_): _description_
        data (_type_): _description_
        folder (_type_): _description_
        mode (_type_): _description_
    """
    try:

        # Redirect stdout and stderr to files
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        read_stdout, write_stdout = os.pipe()
        read_stderr, write_stderr = os.pipe()
        
        sys.stdout = os.fdopen(write_stdout, 'w')
        sys.stderr = os.fdopen(write_stderr, 'w')
        
        stdout_thread = threading.Thread(target=enqueue_output, args=(os.fdopen(read_stdout, 'r'), stdout_queue))
        stderr_thread = threading.Thread(target=enqueue_output, args=(os.fdopen(read_stderr, 'r'), stderr_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        if mode == "Sampling: Halton":
            run_sampling(data, "halton", folder, results_queue)
        elif mode == "Sampling: Random":
            run_sampling(data, "random", folder, results_queue)
        elif mode == "Sensitivity Analysis":
            run_sensitivity_analysis(data, folder, results_queue)
        elif mode == "Optimization":
            run_optimization(data, folder, results_queue)
        else:
            print("Invalid mode")

        stdout_thread.join()
        stderr_thread.join()
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    except Exception as e:
        print("An exception occurred: ", flush=True)
        print(str(e))
        # Print stack trace
        import traceback
        traceback.print_exc()

        # Write all of this information to a crash file
        with open(os.path.join(folder, 'crash.txt'), 'w') as f:
            f.write(str(e))
            f.write("\n")
            traceback.print_exc(file=f)
    finally:
        stdout_thread.join()
        stderr_thread.join()
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr

def process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, list_name):
    """_summary_

    Args:
        data (_type_): _description_
        parameter_map (_type_): _description_
        args (_type_): _description_
        options (_type_): _description_
        oh_strategy (_type_): _description_
        config (_type_): _description_
        metainfo (_type_): _description_
        list_name (_type_): _description_
    """
    for obj in data[list_name]:
        name = obj['name']
        type = obj['type']
        destination = obj['destination']
        original_value = obj['value']
        converted_value = original_value
        if type == "integer":
            converted_value = int(converted_value)
        elif type == "float":
            converted_value = float(converted_value)
        elif type == "boolean":
            converted_value = True if converted_value == "True" else False

        if destination == "args":
            args['param'].append({"name": name, "value": converted_value})
        elif destination == "kwargs":
            parameter_map[name] = original_value
        elif destination == "conf":    
            config[name] = converted_value
        elif destination == "metainfo":
            metainfo[name] = converted_value
        elif destination == "options":
            option_name = name.replace("options_", "")
            options[option_name] = converted_value
        elif destination == "oh_strategy":
            strategy_name = name.replace("strategy_", "")
            oh_strategy[strategy_name] = converted_value

def process_steps(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """

    steps = data['steps']
    output_steps = []
    for step in steps:
        output_step = {}
        output_step['param'] = []
        output_step['objfunc'] = []
        for parameter in step['parameter_objects']:
            parameter_object = {}
            type = parameter['type']
            if type != "list":
                parameter_object['name'] = parameter['name']
                parameter_object['bounds'] = (float(parameter['min_bound']), float(parameter['max_bound']))
                output_step['param'].append(parameter_object)
            else:
                parameter_object['name'] = parameter['name']
                parameter_object['bounds'] = (float(parameter['min_bound']), float(parameter['max_bound']))
                parameter_object['type'] = "list"
                parameter_object['calibration_strategy'] = parameter['calibration_strategy']
                parameter_object['default_value'] = [float(x) for x in parameter['default_value'].replace("[", "").replace("]", "").split(",")]
                output_step['param'].append(parameter_object)
            
        for function in step['objective_functions']:
            out_object = {}
            out_object['name'] = function['name']
            out_object['of'] = function['objective_function']
            out_object['weight'] = float(function['weight'])
            out_object['data'] = [
                function["data_observed"],
                function["data_simulated"]
            ]
            output_step['objfunc'].append(out_object)
        output_steps.append(output_step)
    return output_steps

def pp(parameter, parameter_map, default=None):
    """_summary_

    Args:
        parameter (_type_): _description_
        parameter_map (_type_): _description_
        default (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if parameter in parameter_map.keys():
        if parameter_map[parameter] != ""  \
        and parameter_map[parameter] != "None" \
        and parameter_map[parameter] != "null" \
        and parameter_map[parameter] != "NULL":
            return parameter_map[parameter]
        else:
            return default
    return default

def run_sampling(data, mode, folder, results_queue):
    """_summary_

    Args:
        data (_type_): _description_
        mode (_type_): _description_
        folder (_type_): _description_
        results_queue (_type_): _description_
    """

    parameter_map = {}
    args = {
        "param": [],
        "url": data["url"],
        "files": {}
    }
    options = {}
    oh_strategy = {}
    config = {}
    metainfo = {}

    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "model_parameters")
    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "hyperparameters")
    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "service_parameters")

    output_steps = process_steps(data)
    if len(output_steps) > 1:
        output_steps = [output_steps[0]]

    trace_file = os.path.join(folder, 'results', mode + '_trace.csv')
    file_output_mode = data["sampling_output_mode"]
    if file_output_mode == "Append":
        # Backup trace file if it exists
        if os.path.exists(trace_file):
            shutil.copyfile(trace_file, trace_file + ".bak")
        
    #config['step_trace'] = os.path.join(folder, 'pso_step_trace.json') # Do we need this?

    print("Parsing Parameters...\n", flush=True)
    print("steps: ", flush=True)
    print(json.dumps(output_steps, indent=4))
    print("args: ", flush=True)
    print(json.dumps(args, indent=4))
    print("options: ", flush=True)
    print(json.dumps(options, indent=4))
    print("oh_strategy: ", flush=True)
    print(json.dumps(oh_strategy, indent=4))
    print("config: ", flush=True)
    print(json.dumps(config, indent=4))
    print("metainfo: ", flush=True)
    print(json.dumps(metainfo, indent=4))
    print("kwargs: ", flush=True)
    print(json.dumps(parameter_map, indent=4))

    print("Running Sampling..\n", flush=True)
    trace = run_sampler(output_steps, 
                        args, 
                        int(pp('count', parameter_map)), 
                        int(pp('num_threads', parameter_map)), 
                        mode, 
                        conf=config, 
                        metainfo=metainfo if len(metainfo) > 0 else None,
                        trace_file=trace_file,
                        offset=int(pp('offset', parameter_map)))
    results_queue.put(trace)
    print(trace, flush=True)
    print("\n", flush=True)

    if file_output_mode == "Append" and os.path.exists(trace_file + ".bak"):
        # Read the backup file
        with open(trace_file + ".bak", 'r') as f2:
            backup_lines = f2.readlines()
        
        # Read the trace file
        with open(trace_file, 'r') as f:
            trace_lines = f.readlines()
        
        # Extract headers
        backup_header = backup_lines[0]
        trace_header = trace_lines[0]
        
        # Combine data ensuring headers are not duplicated
        with open(trace_file, 'w') as f:
            f.write(backup_header)
            f.writelines(backup_lines[1:])
            f.writelines(trace_lines[1:] if trace_header == backup_header else trace_lines)
        
        # Remove the backup file
        os.remove(trace_file + ".bak")

def run_optimization(data, folder, results_queue):
    """_summary_

    Args:
        data (_type_): _description_
        folder (_type_): _description_
        results_queue (_type_): _description_
    """
    parameter_map = {}
    args = {
        "param": [],
        "url": data["url"],
        "files": {}
    }
    options = {}
    oh_strategy = {}
    config = {}
    metainfo = {}

    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "model_parameters")
    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "hyperparameters")
    process_list(data, parameter_map, args, options, oh_strategy, config, metainfo, "service_parameters")

    output_steps = process_steps(data)

    config['step_trace'] = os.path.join(folder, 'pso_step_trace.json')

    print("Parsing Parameters...\n", flush=True)
    print("steps: ", flush=True)
    print(json.dumps(output_steps, indent=4))
    print("args: ", flush=True)
    print(json.dumps(args, indent=4))
    print("options: ", flush=True)
    print(json.dumps(options, indent=4))
    print("oh_strategy: ", flush=True)
    print(json.dumps(oh_strategy, indent=4))
    print("config: ", flush=True)
    print(json.dumps(config, indent=4))
    print("metainfo: ", flush=True)
    print(json.dumps(metainfo, indent=4))
    print("kwargs: ", flush=True)
    print(json.dumps(parameter_map, indent=4))

    print("Running MG-PSO Optimization...\n", flush=True)
    optimizer, trace = global_best(output_steps,   
            rounds=(int(pp('min_rounds', parameter_map)), int(pp('max_rounds', parameter_map))),              
            args=args,      
            n_particles=int(pp('n_particles', parameter_map, 10)),
            iters=int(pp('iters', parameter_map, 1)),  
            n_threads=int(pp('n_threads', parameter_map, 4)),      
            rtol=float(pp('rtol', parameter_map, 0.001)),      
            ftol=float(pp('ftol', parameter_map, -np.inf)),      
            ftol_iter=int(pp('ftol_iter', parameter_map, 1)),      
            rtol_iter=int(pp('rtol_iter', parameter_map, 1)),      
            options=options,
            oh_strategy=oh_strategy, 
            metainfo=metainfo if len(metainfo) > 0 else None,
            cost_target=float(pp('cost_target', parameter_map, -np.inf)),   
            conf=config
        )
    
    results_queue.put(trace)
    print(trace, flush=True)
    pass



def run_sensitivity_analysis(data, folder, results_queue):
    """_summary_

    Args:
        data (_type_): _description_
        folder (_type_): _description_
        results_queue (_type_): _description_
    """
    print("Running Sensitivity Analysis", flush=True)

    shutil.copyfile(data["sensitivity_analysis_path"], os.path.join(folder, 'results', 'trace.csv'))
    trace_path = os.path.join(folder, 'results', 'trace.csv')

    output_steps = process_steps(data)
    if len(output_steps) > 1:
        output_steps = [output_steps[0]]

    # Get list of parameters from steps
    parameters = []
    for param in output_steps[0]['param']:
        parameters.append(param['name'])

    positive_best = []
    zero_best = []

    for obj in output_steps[0]['objfunc']:
        if obj['of'] in POSITIVE_BEST:
            positive_best.append(obj['of'])
        elif obj['of'] in ZERO_BEST:
            zero_best.append(obj['of'])

    request_json = {
        "metainfo": {
            "service_url": None,
            "description": "",
            "name": "",
            "mode": "async"
        },
        "parameter": [
            {
            "name": "parameters",
            "value": parameters
            },
            {
            "name": "positiveBestMetrics",
            "value": positive_best
            },
            {
            "name": "zeroBestMetrics",
            "value": zero_best
            }
        ]
    }
    
    with open(os.path.join(folder, 'results', 'request.json'), 'w') as json_file:
        json.dump(request_json, json_file, indent=4)
    
    request_path = os.path.join(folder, 'results', 'request.json')

    output_directory = os.path.join(folder, 'results')

    print("Starting ", data['url'], request_path, trace_path, output_directory, flush=True)

    sensitivity_analysis(data['url'], request_path, trace_path, output_directory)

    print("Finished Sensitivity Analysis", flush=True)








def create_request(request_file: str) -> Client:
    request: Client = Client.from_file(request_file)
    return request

def download_output(response: Client, target_directory) -> None:
    data_names: list[str] = response.get_data_names()
    for name in data_names:
        url = response.get_data_value(name)
        file_path = os.path.join(target_directory, name)
        urllib.request.urlretrieve(url, file_path)

def sensitivity_analysis(url, request_file, trace_file, output_directory):
    request: Client = create_request(request_file)
    files: list[str] = [trace_file] if os.path.isfile(trace_file) else []
    conf = {
        'service_timeout': 60.0,  # (sec)
    }
    result: Client = Client()
    try:
        result = request.execute(url, files=files, sync=True, conf=conf)
    except Exception as ex:
        traceback.print_exc()
        exit(1)

    if result.is_finished():
        download_output(result, output_directory)