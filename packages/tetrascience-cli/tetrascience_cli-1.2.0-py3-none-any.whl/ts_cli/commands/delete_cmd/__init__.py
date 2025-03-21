import argparse
import os
import textwrap

import inquirer
import simplejson as json
from inquirer import errors

from ts_cli.api import TsApi
from ts_cli.commands.utils import existing_folder_type, private_namespace_type
from ts_cli.config.api_config import ApiConfig
from ts_cli.config.update_artifact_config import UpdateArtifactConfig
from ts_cli.config.util import to_version
from ts_cli.util.emit import emit_critical, emit_info, emit_warning


def add_delete_parser(subparsers):
    """
    Adds the `delete` subparser
    :param subparsers:
    :return:
    """

    delete_cmd_args(
        subparsers.add_parser(
            "delete",
            help="Delete artifact identified by namespace/slug:version",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                """
            Delete an artifact from the Tetra Data Platform. For example:
            
                ts-cli delete .
            
            where "." is the path to the artifact souce code.
            The source code positional argument defaults to the current working directory.
            
            The following artifact configuration fields are required:
                type, namespace, slug, version
            The delete command will sequentially check each of the following locations
              for each configuration:
                1. The respective command argument.
                    Example: --type protocol
                2. A manifest.json file in the root of the artifact directory
                3. A protocol.{yaml,yml,json} file in the root of the artifact directory
                4. A schema.json file in the root of the artifact directory
                5. A pyproject.toml file in the root of the artifact directory
            For the namespace field, the delete command will additionally look for
              a configured org (see below).
            For the version field, the delete command will additionally look for a
              pyproject.toml file in the root of the artifact directory
            Use --interactive to be walked through setting up each of the fields
            
            The following TDP API configuration fields are required:
                org, api_url, auth_token, ignore_ssl
            The delete command will sequentially check each of the following locations
              for each configuration:
                1. The respective command argument.
                    Example: --org my-org --auth-token q1w2e3 --api-url https://api.tdp
                    Note that ignore_ssl is set to true by the flag --ignore-ssl,
                      and set to false with --enforce-ssl
                2. The yaml or json formatted configuration file
                    provided in a command argument.
                    Example: --config ./config.json
                3. In the process's environment variables.
                    The fields are prefixed with "TS_" and in all uppercase.
                    Example: export TS_ORG=my-org TS_API_URL=https://api.tdp
                4. The yaml or json formatted file at "~/.config/tetrascience/config"
            """
            ),
        )
    )


def delete_cmd_args(parser: argparse.ArgumentParser):
    """
    Adds delete command arguments to the parser
    :param parser:
    :return:
    """
    artifact_config = parser.add_argument_group("Artifact Configuration")
    artifact_config.add_argument(
        "--type",
        type=str,
        choices=["connector", "ids", "protocol", "task-script", "tetraflow"],
        help="artifact type",
    )
    artifact_config.add_argument(
        "--namespace",
        type=private_namespace_type,
        help="Artifact namespace configuration",
    )
    artifact_config.add_argument(
        "--slug", type=str.lower, help="Artifact slug configuration"
    )
    artifact_config.add_argument(
        "--version", type=to_version, help="Artifact version configuration"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="interactively set up Artifact configuration",
    )
    parser.add_argument(
        "source",
        type=existing_folder_type,
        help="path to folder to the artifact on your local machine",
        nargs="?",
        default=os.getcwd(),
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="skip actual artifact deletion"
    )

    api_config = parser.add_argument_group("API Configuration")
    ssl_group = api_config.add_mutually_exclusive_group()
    ssl_group.add_argument(
        "--ignore-ssl",
        "-k",
        action="store_true",
        help="ignore the SSL certificate verification",
    )
    ssl_group.add_argument(
        "--enforce-ssl",
        "-e",
        dest="ignore_ssl",
        action="store_false",
        help="do not ignore SSL certificate verification",
    )
    api_config.set_defaults(ignore_ssl=None)
    api_config.add_argument(
        "--profile", help="The name of the configuration profile to use", type=str
    )
    api_config.add_argument("--org", help="org slug", type=str)
    api_config.add_argument("--api-url", help="platform API URL", type=str)
    api_config.add_argument("--auth-token", help="authorization token", type=str)
    api_config.add_argument(
        "--config",
        "-c",
        help="yaml or json formatted file with an API configuration",
        type=argparse.FileType("r"),
    )
    parser.set_defaults(func=delete)


def confirm(config: UpdateArtifactConfig):
    confirmation_string = config.to_string()

    emit_warning("Deleting an artifact is a permanent action and cannot be undone")
    emit_warning("To continue, enter the following string")
    emit_info(confirmation_string)

    def is_confirmed(_, value):
        if not value == confirmation_string:
            raise errors.ValidationError("", "Entered confirmation does not match")
        return True

    values = inquirer.prompt(
        [inquirer.Text("confirmation", message="Confirmation", validate=is_confirmed)]
    )
    if values is None:
        raise emit_critical("Deletion interupted")


def delete(args):
    """
    The actual delete command implementation
    :return:
    """
    artifact_config = UpdateArtifactConfig(args, interactive=args.interactive)
    api_config = ApiConfig(args)
    ts_api = TsApi(api_config)

    confirm(artifact_config)

    if args.dry_run is not True:
        response = ts_api.delete_artifact(artifact_config)
        print(json.dumps(response, indent="\t", sort_keys=True), flush=True)
    else:
        emit_critical("Skipping artifact deletion because 'dry-run' flag was set")
