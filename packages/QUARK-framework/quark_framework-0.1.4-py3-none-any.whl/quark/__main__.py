import argparse
from typing import Any, Union, Tuple
from time import perf_counter

from quark.plugin_manager import factory, loader
import yaml

def create_benchmark_parser(parser: argparse.ArgumentParser):
    parser.add_argument("-c", "--config", help="Provide valid config file instead of interactive mode")
    parser.add_argument('-cc', '--createconfig', help='If you want o create a config without executing it',
                        required=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('-s', '--summarize', nargs='+', help='If you want to summarize multiple experiments',
                        required=False)
    parser.add_argument('-m', '--modules', help="Provide a file listing the modules to be loaded")
    parser.add_argument('-rd', '--resume-dir', nargs='?', help='Provide results directory of the job to be resumed')
    parser.add_argument('-ff', '--failfast', help='Flag whether a single failed benchmark run causes QUARK to fail',
                        required=False, action=argparse.BooleanOptionalAction)

    parser.set_defaults(goal='benchmark')

# In the config file, a pipeline module can be specified in two ways:
# -A single string is interpreted as a single module without parameters
# -A dictionary with a single key-value pair is interpreted as a single module where the value is another dictionary containing the parameters
PipelineModule = Union[str, dict[str, dict[str, Any]]]

PipelineLayer = Union[PipelineModule, list[PipelineModule]]
ModuleInfo = Tuple[str, dict[str, Any]]

def _init_module(module: PipelineModule) -> ModuleInfo:
    match module:
        case str():  # Single module
            return((module, {}))
        case dict():  # Single module with parameters
            name = next(iter(module))
            params = module[name]
            return ((name, params))


# TODO rename to extract_module_info or somethgin like that
def _init_pipeline(pipeline: list[PipelineLayer]) -> list[list[ModuleInfo]]:
    # Create backup of the pipeline
    initialized_pipelines = [[]]
    for layer in pipeline:
        modules = []
        match layer:
            case list():  # Multiple modules
                modules = [_init_module(module) for module in layer]
            case _:  # Single module
                modules = [_init_module(layer)]
        initialized_pipelines = [p + [module] for p in initialized_pipelines for module in modules]

    return initialized_pipelines



def start() -> None:
    """
    Main function that triggers the benchmarking process
    """

    print(" ============================================================ ")
    print(r"             ___    _   _      _      ____    _  __           ")
    print(r"            / _ \  | | | |    / \    |  _ \  | |/ /           ")
    print(r"           | | | | | | | |   / _ \   | |_) | | ' /            ")
    print(r"           | |_| | | |_| |  / ___ \  |  _ <  | . \            ")
    print(r"            \__\_\  \___/  /_/   \_\ |_| \_\ |_|\_\           ")
    print("                                                              ")
    print(" ============================================================ ")
    print("  A Framework for Quantum Computing Application Benchmarking  ")
    print("                                                              ")
    print("        Licensed under the Apache License, Version 2.0        ")
    print(" ============================================================ ")

    parser = argparse.ArgumentParser()
    create_benchmark_parser(parser)

    args = parser.parse_args()

    with open(args.config) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    loader.load_plugins(data["plugins"])

    if "pipelines" in data:
        pipelines = data["pipelines"]
    elif "pipeline" in data:
        pipelines = data["pipeline"]
    else:
        raise ValueError("No pipeline found in configuration file")

    if isinstance(pipelines, list):
        pipelines = {"pipeline": pipelines}

    for pipeline_group, pipelines in pipelines.items():
        print(f"Running pipeline group: {pipeline_group}")
        pipelines = _init_pipeline(pipelines)
        for i, pipeline in enumerate(pipelines):
            print(f"Running pipeline {i+1}")
            # Initialize the pipeline
            print(pipeline)
            pipeline = [factory.create(name, args) for (name, args) in pipeline]
            last_result = None
            preprocessing_times = []
            posprocessing_times = []
            for module in pipeline:
                t1 = perf_counter()
                last_result = module.preprocess(last_result)
                preprocessing_times.append(perf_counter() - t1)

            last_result = None
            for module in reversed(pipeline):
                t1 = perf_counter()
                last_result = module.postprocess(last_result)
                posprocessing_times.append(perf_counter() - t1)

            print(f"Result: {last_result}")
            print(f"Preprocessing times: {preprocessing_times}")
            print(f"Posprocessing times: {posprocessing_times}")
            print(f"Total time: {sum(preprocessing_times) + sum(posprocessing_times)}")
            print(" ============================================================ ")

    print(" ============================================================ ")
    print(" ====================  QUARK finished!   ==================== ")
    print(" ============================================================ ")
    exit(0)



if __name__ == '__main__':
    start()
