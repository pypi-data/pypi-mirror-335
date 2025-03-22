import json
from argparse import ArgumentParser
from sys import argv

from .api import PubMedAPI, METHODS


def argparser(args=argv[1:]) -> dict:
    """ Parse command line arguments. """
    parser = ArgumentParser(description="Query PubMed API.")

    parser.add_argument("ids",
                        action="store",
                        help="IDs to query (separated by whitespaces).",
                        metavar="ID",
                        nargs="+")

    parser.add_argument("-o", "--output-file",
                        action="store",
                        default="PubMedAPI.json",
                        metavar="OUTPUT_FILE",
                        help="File to write results to (default: 'PubMedAPI.json').")

    parser.add_argument("-m", "--method",
                        action="store",
                        choices=METHODS,
                        default="api",
                        help="Method to obtain data with (default: 'api').")

    parser.add_argument("-w", "--max-workers",
                        action="store",
                        metavar="WORKERS",
                        help=f"Number of processes to use (optional).",
                        type=int)

    parser.add_argument("-c", "--chunksize",
                        action="store",
                        metavar="SIZE",
                        help=f"Number of objects sent to each worker (optional).",
                        type=int)

    parser.add_argument("--email",
                        action="store",
                        metavar="ADDRESS",
                        help=f"Your e-mail address (required to query API only).")

    parser.add_argument("--tool",
                        action="store",
                        default="PubMedAPI",
                        metavar="NAME",
                        help=f"Tool name (optional, used to query API only).")

    parser.add_argument("--quiet",
                        action="store_false",
                        dest="verbose",
                        help=f"Does not print results (limited to a single item only by default).")

    parser.add_argument("--log-level",
                        action="store",
                        choices=["critical", "error", "warning", "info", "debug"],
                        help=f"Logging level (optional).")

    return parser.parse_args(args)


def main():
    """ Starts command line interface. """
    args = dict(vars(argparser()))
    pm = PubMedAPI(email=args.pop("email"), tool=args.pop("tool"), log_level=args.pop("log_level"))
    output_file = args.pop("output_file")
    verbose = args.pop("verbose")

    data = pm(args.pop("ids"), **args)
    with open(output_file, "w") as f:
        json.dump(data, f)

    if verbose and len(data) == 1:
        print(json.dumps(data, indent=2))
