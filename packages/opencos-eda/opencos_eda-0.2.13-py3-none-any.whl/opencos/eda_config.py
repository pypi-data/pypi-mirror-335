import os
import sys
import argparse
import mergedeep

from opencos import util

class Defaults:
    config_yml =  'eda_config_defaults.yml'

    supported_config_keys = set([
        'defines',
        'dep_command_enables',
        'dep_tags_enables',
        'deps_legacy_supported',
        'deps_markup_supported',
        'deps_subprocess_shell',
        'dep_sub',
        'vars',
        'tools',
        'auto_tools_order',
        'inferred_top_file_ext',
    ])
    supported_config_auto_tools_order_keys = set([
        'exe', 'handlers', 'requires_env', 'requires_py', 'requires_cmd',
        'disable-tools-multi',
    ])
    supported_config_tool_keys = set([
        'defines',
        'log-bad-strings',
        'log-must-strings',
        'sim-libraries',
        'compile-args',
        'compile-waves-args',
        'compile-waivers',
        'elab-args',
        'elab-waves-args',
        'simulate-args',
        'simulate-waves-args',
        'simulate-waivers',
        'coverage-args',
    ])


def find_eda_config_yml_fpath(filename:str, package_search_only=False, package_search_enabled=True) -> str:
    '''Locates the filename (.yml) either from fullpath provided or from the sys.path
    opencos package paths.'''

    # Check fullpath, unless we're only checking the installed pacakge dir.
    if package_search_only:
        pass
    elif os.path.exists(filename):
        return os.path.abspath(filename)

    leaf_filename = os.path.split(filename)[1]

    if leaf_filename != filename:
        # filename had subdirs, and we didn't find it already.
        util.error(f'eda_config: Could not find {filename=}')
        return None

    # Search in . or pacakge installed dir
    thispath = os.path.dirname(__file__) # this is not an executable, should be in packages dir.

    if package_search_only:
        paths = [thispath]
    elif package_search_enabled:
        paths = ['', thispath]
    else:
        paths = ['']


    for dpath in paths:
        fpath = os.path.join(dpath, leaf_filename)
        if os.path.exists(fpath):
            return fpath

    util.error(f'eda_config: Could not find {leaf_filename=} in opencos within {paths=}')
    return None


def check_config(config:dict, filename='') -> None:
    # sanity checks:
    for key in config:
        if key not in Defaults.supported_config_keys:
            util.error(f'eda_config.get_config({filename=}): has unsupported {key=}' \
                       + f' {Defaults.supported_config_keys=}')

    for row in config.get('auto_tools_order', []):
        for tool, table in row.items():
            for key in table:
                if key not in Defaults.supported_config_auto_tools_order_keys:
                    util.error(f'eda_config.get_config({filename=}): has unsupported {key=}' \
                               + f' in auto_tools_order, {tool=},' \
                               + f' {Defaults.supported_config_auto_tools_order_keys=}')

    for tool,table in config.get('tools', {}).items():
        for key in table:
            if key not in Defaults.supported_config_tool_keys:
                util.error(f'eda_config.get_config({filename=}): has unsupported {key=}' \
                           + f' in config.tools.{tool=}, ' \
                           + f' {Defaults.supported_config_tool_keys=}')


def get_config(filename) -> dict:
    fpath = find_eda_config_yml_fpath(filename)
    user_config = util.yaml_safe_load(fpath)
    check_config(user_config, filename=filename)

    # The final thing we do is update key 'config-yml' with the full path used.
    # This way we don't have to pass around --config-yml as some special arg
    # in eda.CommandDesign.args, and eda.CommandMulti can use when re-invoking 'eda'.
    user_config['config-yml'] = fpath
    return user_config


def get_config_handle_defaults(filename) -> dict:
    user_config = get_config(filename)
    user_config = get_config_merged_with_defaults(user_config)
    return user_config


def merge_config(dst_config:dict, overrides_config:dict, additive_strategy=False) -> None:
    '''Mutates dst_config, uses Strategy.TYPESAFE_REPLACE'''
    # TODO(drew): It would be cool if I could have Sets be additive, but oh well,
    # this gives the user more control over replacing entire lists.
    strategy = mergedeep.Strategy.TYPESAFE_REPLACE
    if additive_strategy:
        strategy = mergedeep.Strategy.TYPESAFE_ADDITIVE
    mergedeep.merge(dst_config, overrides_config, strategy=strategy)


def get_config_merged_with_defaults(config:dict) -> dict:
    default_fpath = find_eda_config_yml_fpath(Defaults.config_yml, package_search_only=True)
    default_config = util.yaml_safe_load(default_fpath)
    merge_config(default_config, overrides_config=config)
    # This technically mutated updated into default_config, so return that one:
    return default_config

def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='opencos eda config options', add_help=False, allow_abbrev=False)
    parser.add_argument('--config-yml', type=str, default=Defaults.config_yml,
                        help=f'YAML filename to use for configuration (default {Defaults.config_yml})')
    return parser

def get_argparser_short_help() -> str:
    return util.get_argparser_short_help(parser=get_argparser())


def get_eda_config(args:list, quiet=False) -> (dict, list):
    '''Returns an config dict and a list of args to be passed downstream
    to eda.main and eda.process_tokens.

    Handles args for:
      --config-yml=<YAMLFILE>
    '''

    parser = get_argparser()
    try:
        parsed, unparsed = parser.parse_known_args(args + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        util.error(f'problem attempting to parse_known_args for {args=}')

    util.debug(f'eda_config.get_eda_config: {parsed=} {unparsed=}  from {args=}')

    if parsed.config_yml:
        if not quiet:
            util.info(f'eda_config: --config-yml={parsed.config_yml} observed')
        fullpath = find_eda_config_yml_fpath(parsed.config_yml)
        config = get_config(fullpath)
        if not quiet:
            util.info(f'eda_config: using config: {fullpath}')

        # Calling get_config(fullpath) will add fullpath to config['config-yml'], so the
        # arg for --config-yml does not need to be re-added.
    else:
        config = None


    return config, unparsed
