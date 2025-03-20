import argparse
import asyncio
import logging
import sys

from loguru import logger

from xxy.__about__ import __version__
from xxy.agent import build_table
from xxy.config import load_config
from xxy.data_source.folder import FolderDataSource
from xxy.result_writer.csv import CsvResultWriter


def config_log_level(v: int) -> None:
    logger.remove()
    log_format = "<level>{message}</level>"
    if v >= 4:
        logger.add(sys.stderr, level="TRACE", format=log_format)
    elif v >= 3:
        logger.add(sys.stderr, level="DEBUG", format=log_format)
    elif v >= 2:
        logger.add(sys.stderr, level="INFO", format=log_format)
    elif v >= 1:
        logger.add(sys.stderr, level="SUCCESS", format=log_format)
    else:
        logger.add(sys.stderr, level="WARNING", format=log_format)

    if v < 4:
        # avoid "WARNING! deployment_id is not default parameter."
        langchain_logger = logging.getLogger("langchain.chat_models.openai")
        langchain_logger.disabled = True


async def command_query(args: argparse.Namespace) -> None:
    data_source = FolderDataSource(args.folder_path)
    with CsvResultWriter(args.o) as result_writer:
        await build_table(data_source, args.t, args.d, args.n, result_writer)


async def command_config(args: argparse.Namespace) -> None:
    load_config(gen_cfg=True)


async def amain() -> None:
    parser = argparse.ArgumentParser(description="xxy-" + __version__)
    parser.add_argument("-v", action="count", default=0, help="verbose level.")
    parser.add_argument(
        "-c",
        default="",
        help="Configuration file path. if not provided, use `~/.xxy_cfg.json` .",
    )
    subparsers = parser.add_subparsers(required=True, help="sub-command help")

    # create the parser for the "foo" command
    parser_query = subparsers.add_parser("query", help="Query entity from documents.")
    parser_query.set_defaults(func=command_query)
    parser_query.add_argument(
        "folder_path",
        help="Folder path to search for documents.",
    )
    parser_query.add_argument(
        "-t",
        nargs="*",
        help="Target company",
    )
    parser_query.add_argument(
        "-d",
        nargs="+",
        required=True,
        help="Report date",
    )
    parser_query.add_argument(
        "-n",
        nargs="+",
        required=True,
        help="Entity name",
    )
    parser_query.add_argument(
        "-o",
        default="output.csv",
        help="Output file path",
    )
    parser_config = subparsers.add_parser(
        "config",
        help="Edit configuration file.",
    )
    parser_query.add_argument(
        "--gen",
        help="Regenerate config from environment variables.",
    )
    parser_config.set_defaults(func=command_config)
    args = parser.parse_args()

    config_log_level(args.v)
    await args.func(args)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
