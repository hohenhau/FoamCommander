#!/usr/bin/python

import sys
from utilities.commandLineArgsParser import detect_and_parse_arguments
from utilities.classFlowMetrics import FlowMetrics


# TODO: Change this to use focoProperties

def estimate_flow_metrics(args=None):
    """
    Creates flow metrics for CFD simulation. Uses arguments passed externally if available,
    otherwise calls detect_and_parse_arguments to get arguments.

    :param args: Arguments passed externally (if any)
    :return: FlowMetrics object
    """
    # If args are not passed, use the detect_and_parse_arguments function to retrieve them
    if not args:
        args = detect_and_parse_arguments()  # This will handle the argument parsing

    # Create FlowMetrics object using the arguments
    flow_metrics = FlowMetrics(args)
    print(flow_metrics)
    return flow_metrics


if __name__ == "__main__":
    estimate_flow_metrics()
