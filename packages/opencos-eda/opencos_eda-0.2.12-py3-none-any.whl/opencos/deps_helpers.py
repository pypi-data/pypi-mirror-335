import os
import sys
import re
import shutil

from opencos import eda_config
from opencos.util import debug, info, warning, error, ShellCommandList

class Defaults:
    supported_dep_keys_by_type = {
        dict: set(['commands']),
        str: set(['*']),
    }
    supported_tag_keys = set([
        'with-tools',
        'args',
        'defines',
        'incdirs',
        'replace-config-tools',
        'additive-config-tools',
    ])
    supported_command_keys = set([
        'shell',
        'work-dir-add-srcs', 'work-dir-add-sources',
        'peakrdl',
        'var-subst-args',
        'var-subst-os-env',
        'tee',
    ])

# Conditional imports, where someone may not have 'peakrdl' package installed.
# attempt to gracefull handle this instead of dying on missing module/package:
try:
    import peakrdl
except:
    pass

thispath = os.path.dirname(__file__)
peakrdl_cleanup_py = os.path.join(thispath, 'peakrdl_cleanup.py')


def dep_str2list(value) -> list():
    if value is None:
        return []
    if type(value) is str:
        return re.split('\n+| +', value) # convert \n separated to list, also split on spaces
    else:
        return value


def deps_target_get_deps_list(entry, default_key:str='deps', target_node:str='',
                              deps_file:str='', entry_must_have_default_key:bool=False) -> list():
    # For convenience, if key 'deps' in not in an entry, and entry is a list or string, then
    # assume it's a list of deps
    debug(f'{deps_file=} {target_node=}: {entry=} {default_key=}')
    deps = list()
    if type(entry) is str:
        deps = dep_str2list(entry)
    elif type(entry) is list:
        deps = entry # already a list
    elif type(entry) is dict:

        if entry_must_have_default_key:
            assert default_key in entry, f'{target_node=} in {deps_file=} does not have a key for {default_key=} in {entry=}'
        deps = entry.get(default_key, list())
        deps = dep_str2list(deps)

    # Strip commented out list entries, strip blank strings, preserve non-strings
    ret = list()
    for dep in deps:
        if type(dep) is str:
            if dep.startswith('#') or dep == '':
                continue
        ret.append(dep)
    return ret


def deps_list_target_sanitize(entry, default_key:str='deps', target_node:str='', deps_file:str='') -> dict():
    # Since we support target entries that can be dict(), list(), or str(), sanitize
    # them so they are a dict(), with a key named 'deps' that has a list of deps.
    if type(entry) is dict:
        return entry

    if type(entry) is str:
        mylist = dep_str2list(entry) # convert str to list()
        return {default_key: mylist}

    if type(entry) is list:
        # it's already a list
        return {default_key: entry}

    assert False, f"Can't convert to list {entry=} {default_key=} {target_node=} {deps_file=}"


def path_substitutions_relative_to_work_dir(exec_list : list, info_str : str, target_path : str):

    # Look for path substitutions, b/c we later "work" in self.args['work-dir'], but
    # files should be relative to our target_path.
    for iter,word in enumerate(exec_list):
        m = re.search(r'(\.+\/+[^"\;\:\|\<\>\*]*)$', word)
        if m:
            # ./, ../, file=./../whatever  It might be a filepath.
            # [^"\;\:\|\<\>\*] is looking for non-path like characters, so we dont' have a trailing
            #  " : ; < > |
            # try and see if this file exists. Note that files in the self.args['work-dir'] don't
            # need this, and we can't assume dir levels in the work-dir.
            try:
                try_path = os.path.abspath(os.path.join(os.path.abspath(target_path), m.group(1)))
                if os.path.isfile(try_path):
                    # make the substitution
                    exec_list[iter] = word.replace(m.group(1), try_path)
                    debug(f'path substitution {info_str=} {target_path=}: replaced - {word=} is now ={exec_list[iter]}')
            except:
                pass

    return exec_list


def line_with_var_subst(line : str, replace_vars_dict=dict(), replace_vars_os_env=False,
                        target_node='', target_path='') -> str:
    # We can try for replacing any formatted strings, using self.args, and os.environ?
    # We have to do this per-word, so that missing replacements or tcl-like things, such
    # as '{}' wouldn't bail if trying to do line.format(**dict)
    if '{' not in line:
        return line

    if replace_vars_os_env:
        replace_dict = dict()
        replace_dict.update(os.environ)
        replace_dict.update(replace_vars_dict)
    else:
        replace_dict = replace_vars_dict

    words = line.split()
    for iter,word in enumerate(words):
        try:
            words[iter] = word.format(**replace_dict)
        except:
            pass

    new_line = ' '.join(words)
    if new_line != line:
        debug(f'{target_node=} {target_path=} performed string format replacement, {line=} {new_line=}')
        return new_line
    else:
        debug(f'{target_node=} {target_path=} string format replacement attempted, no replacement. {line=}')
        return line


class DepsProcessor:
    def __init__(self, command_design_ref, deps_entry:dict, target:str,
                 target_path:str, target_node:str, deps_file:str):
        '''
        command_design_ref (eda.CommandDesign),
        deps_entry (dict, target in DEPS.yml file)
        target_node (str) -- key in DEPS.yml that got us the deps_entry, used for debug
        deps_file (str) -- file, used for debug
        '''

        self.command_design_ref = command_design_ref
        self.deps_entry = deps_entry
        self.target = target
        self.target_path = target_path
        self.target_node = target_node # for debug
        self.deps_file = deps_file # for debug

        assert type(deps_entry) is dict, \
            f'{deps_entry=} for {target_node=} in {deps_file=} must be a dict()'
        assert command_design_ref is not None, \
            f'called DepsProcessor.__init__, but no ref to CommandDesign object (is None)'

        # named eda commands in the target:
        # If this deps_entry has a 'sim', 'build', etc command entry for this target, grab that because it
        # can set defines or other things specific to an eda command ('sim', for example)
        self.entry_eda_command = self.deps_entry.get(command_design_ref.command_name, dict())

        # alias some of the self.command_design_ref values
        self.command_name = self.command_design_ref.command_name # str, for debug
        self.args         = self.command_design_ref.args         # dict
        self.config       = self.command_design_ref.config       # dict
        self.set_arg      = self.command_design_ref.set_arg      # method
        self.error        = self.command_design_ref.error        # method.

    def apply_defines(self, defines_dict:dict):
        if type(defines_dict) is not dict:
            self.error(f"{defines_dict=} is not type dict, can't apply defines,",
                       f"{self.target_node=} in {self.deps_file=}")
        for k,v in defines_dict.items():
            if v is None or v == '':
                # TODO(drew): this can be simplified if 'DEPS' files are deprecated.
                self.command_design_ref.process_plusarg(f'+define+{k}')
            else:
                self.command_design_ref.process_plusarg(f'+define+{k}={v}')

    def apply_incdirs(self, incdirs_list:list):
        if type(incdirs_list) not in [str, list]:
            self.error(f"{incdirs_list=} is not type str/list, can't apply incdirs",
                       f"{self.target_node=} in {self.deps_file=}")
        incdirs_list = dep_str2list(incdirs_list)
        for x in incdirs_list:
            abspath = os.path.abspath(os.path.join(self.target_path, x))
            if abspath not in self.command_design_ref.incdirs:
                self.command_design_ref.incdirs.append(abspath)
                debug(f'Added include dir {abspath} from {self.target_node=} {self.deps_file=}')

    def apply_args(self, args_list:list) -> list:
        if type(args_list) not in [str, list]:
            self.error(f"{args_list=} is not type str/list, can't apply args",
                       f"{self.target_node=} in {self.deps_file=}")
        args_list = dep_str2list(args_list)
        unparsed = self.command_design_ref.run_argparser_on_list(tokens=args_list)
        if len(unparsed) > 0:
            # This is only a warning - because things like CommandFlist may not have every
            # one of their self.args.keys() set for a given target, such as a 'sim' target that
            # has --optimize, which is not an arg for CommandFlist. But we'd still like to get an flist
            # from that target.
            warning(f'For {self.command_design_ref.command_name}:' \
                    + f' {self.target_node=} in {self.deps_file=} has unknown args {unparsed=}')
        return unparsed


    def process_deps_entry(self):

        # Supported target keys:
        # -- tags (or equivalent, to support multiple define/incdir/deps for a target)
        #    -- supports tag-name, with-tools, args, defines, incdirs, deps
        #         ** to be applied if a tool matches.
        #    -- TODO(drew): other features in docs/DEPS.md not yet implemented.
        # -- multi: ignore: - commands
        # -- Named eda commands
        #    -- (partially done) sim or other eda commands (eda.py command specific things)
        #        basically, check the command, and apply/merge values to 'entry'?
        # -- args
        # -- defines
        # -- incdirs
        # -- top.
        # -- commands (not in deps)
        # -- deps

        # TODO(drew): This does not yet support conditional inclusions based on defines,
        # like the old DEPS files did with pattern:
        #    SOME_DEFINE ?  dep_if_define_present : dep_if_define_not_present
        # I would like to deprecate that in favor of 'tags'. However, likely will need
        # to walk the entire DEPS.yml once to populate all args/defines, and then re-
        # walk them to add/prune the correct tag based dependencies, or rely on it being
        # entirely top-down.

        # DEPS.yml entries have ordered keys, and process these in-order
        # with how the <target> defined it.
        remaining_deps_list = list() # deps items we find that are not yet processed.
        for key in self.deps_entry.keys():
            if key == 'tags':
                remaining_deps_list += self.process_tags()
            elif key == 'defines':
                self.process_defines()
            elif key == 'incdirs':
                self.process_incdirs()
            elif key == 'top':
                self.process_top()
            elif key == 'args':
                self.process_args()
            elif key == 'commands':
                self.process_commands()
            elif key == 'deps':
                remaining_deps_list += self.process_deps_return_discovered_deps()

        # We return the list of deps that still need to be resolved (['full_path/some_target', ...])
        return remaining_deps_list

    def process_tags(self) -> list:
        '''Returns List of added deps, applies tags (dict w/ details, if any) to self.command_desing_ref.

        Tags are only supported as a Table within a target. Current we only support:
        'args', 'replace-config-tools', 'additive-config-tools', 'with-tools'.
        '''

        deps_tags_enables = self.config.get('dep_tags_enables', {})
        ret_deps_added_from_tags = list()

        entry_tags = dict() # from yml table
        entry_tags.update(self.deps_entry.get('tags', dict()))
        for tagname,value in entry_tags.items():
            debug(f'process_tags(): {self.target_node=} {tagname=} in {self.deps_file=}' \
                  + f' observed: {value=}')
            assert type(value) is dict, \
                f'{tagname=} {value=} value must be a dict for {self.target_node=} in {self.deps_file=}'
            tags_dict_to_apply = value.copy()

            for key in value.keys():
                if key not in Defaults.supported_tag_keys:
                    self.error(f'{self.target_node=} {tagname=} in {self.deps_file=}:',
                               f'has unsupported {key=} {Defaults.supported_tag_keys=}')

            with_tools = dep_str2list(value.get('with-tools', list()))
            if len(with_tools) > 0 and not deps_tags_enables.get('with-tools', None):
                with_tools = []
                warning(f'{self.target_node=} {tagname=} in {self.deps_file=}:',
                        f' skipped due to with-tools disabled.')

            apply_tag_items = False

            tool = self.args.get('tool', None)
            if tool in with_tools:
                apply_tag_items = True
            else:
                # Each item of with-tools can also be in the form {tool (str)}:{TOOL.tool_version (str)}
                # this matches Tool.get_full_tool_and_versions()
                if getattr(self.command_design_ref, 'get_full_tool_and_versions', None):
                    tool_full_version = self.command_design_ref.get_full_tool_and_versions()
                    if tool_full_version and tool_full_version in with_tools:
                        apply_tag_items = True

            if not apply_tag_items:
                debug(f'process_tags(): {self.target_node=} {tagname=} in {self.deps_file=}',
                      f' skipped for {tool=}')
            else:
                debug(f'process_tags(): {self.target_node=} {tagname=} in {self.deps_file=}',
                      f' applying tags for {tool=}, {tags_dict_to_apply.keys()=}')


            if apply_tag_items:
                # We have matched something (with-tools, etc).
                # apply these in the original order of the keys:
                for key in tags_dict_to_apply.keys():

                    if key == 'defines':
                        # apply defines:
                        self.apply_defines(value.get('defines', {}))

                    elif key == 'incdirs':
                        # apply incdirs:
                        self.apply_incdirs(value.get('incdirs', []))

                    elif key == 'args':
                        # apply args
                        args_list = dep_str2list(value.get('args', list()))
                        if len(args_list) > 0 and not deps_tags_enables.get('args', None):
                            args_list = []
                            warning(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                                    + f' skipped args due to args disabled.')
                        if len(args_list) > 0:
                            # This will apply knowns args to the target dep:
                            info(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                                 + f'applying args b/c {with_tools=} for {args_list=}')
                            unparsed = self.apply_args(args_list)

                    elif key == 'deps':

                        # apply deps (includes commands, stray +define+ +incdir+)
                        # treat the same way we treat self.process_deps_return_discovered_deps
                        deps_list = deps_target_get_deps_list(entry=value,
                                                              target_node=self.target_node,
                                                              deps_file=self.deps_file)
                        ret_deps_added_from_tags += self.get_remaining_and_apply_deps(deps_list)

                # for replace-config-tools or additive-config-tools from tags, these don't need to
                # handle in order of tags keys:

                # apply replace-config-tools
                # This will replace lists (compile-waivers).
                tool_config = value.get('replace-config-tools', {}).get(tool, None)
                if tool_config and not deps_tags_enables.get('replace-config-tools', None):
                    tool_config = None
                    warning(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                            + f' skipped replace-config-tools b/c it is disabled.')
                if tool_config and type(tool_config) is dict:
                    # apply it to self.tool_config:
                    info(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                         + f'applying replace-config-tools for {tool=}: {tool_config}')
                    eda_config.merge_config(self.command_design_ref.tool_config, tool_config)
                    # Since we altered command_design_ref.tool_config, need to call update on it:
                    self.command_design_ref.update_tool_config()
                    debug(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                          + f'Updated {self.command_design_ref.tool_config=}')

                # apply additive-config-tools
                # This will append to lists (compile-waivers)
                tool_config = value.get('additive-config-tools', {}).get(tool, None)
                if tool_config and not deps_tags_enables.get('additive-config-tools', None):
                    tool_config = None
                    warning(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                            + f' skipped additive-config-tools b/c it is disabled.')
                if tool_config and type(tool_config) is dict:
                    # apply it to self.tool_config:
                    info(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                         + f'applying additive-config-tools for {tool=}: {tool_config}')
                    eda_config.merge_config(self.command_design_ref.tool_config, tool_config,
                                            additive_strategy=True)
                    # Since we altered command_design_ref.tool_config, need to call update on it:
                    self.command_design_ref.update_tool_config()
                    debug(f'{self.target_node=} {tagname=} in {self.deps_file=}:' \
                          + f'Updated {self.command_design_ref.tool_config=}')

        return ret_deps_added_from_tags


    def process_defines(self):
        '''Returns None, applies defines (dict, if any) from self.deps_entry to self.command_design_ref.'''

        # Defines:
        # apply command specific defines, with higher priority than the a deps_entry['sim']['defines'] entry,
        # do this with dict1.update(dict2):
        entry_defines = dict()
        entry_defines.update(self.deps_entry.get('defines', dict()))
        entry_defines.update(self.entry_eda_command.get('defines', dict()))
        assert type(entry_defines) is dict, \
            f'{entry_defines=} for {self.target_node=} in {self.deps_file=} must be a dict()'

        self.apply_defines(entry_defines)

    def process_incdirs(self):
        '''Returns None, applies incdirs (dict, if any) from self.deps_entry to self.command_design_ref.'''

        entry_incdirs = list()
        # apply command specific incdirs, higher in the incdir list:
        entry_incdirs = dep_str2list(self.entry_eda_command.get('incdirs', list()))
        entry_incdirs += dep_str2list(self.deps_entry.get('incdirs', list()))
        assert type(entry_incdirs) is list, \
            f'{entry_incdirs=} for {self.target_node=} in {self.deps_file=} must be a list()'
        self.apply_incdirs(entry_incdirs)

    def process_top(self):
        '''Returns None, applies top (str, if any) from self.deps_entry to self.command_design_ref.'''

        if self.args['top'] != '':
            return # already set

        # For 'top', we overwrite it if not yet set.
        # the command specific 'top' has higher priority.
        entry_top = self.entry_eda_command.get('top', str()) # if someone set target['sim']['top']
        if entry_top == '':
            entry_top = self.deps_entry.get('top', str()) # if this target has target['top'] set

        if entry_top != '':
            if self.args['top'] == '':
                # overwrite only if unset - we don't want other deps overriding the topmost
                # target's setting for 'top'.
                self.set_arg('top', str(entry_top))

    def process_args(self):
        '''Returns None, applies args (list or str, if any) from self.deps_entry to self.command_design_ref.'''

        # for 'args', process each. command specific args take higher priority that target args.
        # run_argparser_on_list: uses argparse, which takes precedence on the last arg that is set,
        # so put the command specific args last.
        # Note that if an arg is already set, we do NOT update it
        args_list = dep_str2list(self.deps_entry.get('args', list()))
        args_list += dep_str2list(self.entry_eda_command.get('args', list()))

        # for args_list, re-parse these args to apply them to self.args.
        unparsed = list()
        if len(args_list) == 0:
            return

        debug(f'{self.target_node=} in {self.deps_file=}: {args_list=}')
        unparsed = self.apply_args(args_list)

        # TODO(drew): Currently, I can't support changing the 'config' via an arg encountered in
        # DEPS.yml. This is prevented b/c --config-yml appears as a modifed arg no matter what
        # (and we don't let DEPS.yml override modifed args, otherwise a target would override the
        # user command line).


    def get_commands(self, commands=list(), dep=None):
        '''Returns tuple of (shell_commands_list, work_dir_add_srcs_list).

        Does not have side effects on self.command_design_ref.
        '''

        default_ret = list(), list()

        if len(commands) == 0:
            # if we weren't passed commands, then get them from our target (self.deps_entry)
            commands = self.deps_entry.get('commands', list())

        assert type(commands) is list, f'{self.deps_entry=} has {commands=} type is not list'

        if len(commands) == 0: # No commands in this target
            return default_ret

        debug(f"Got {self.deps_entry=} for {self.target_node=} in {self.deps_file=}, has {commands=}")
        shell_commands_list = list() # list of dict()s
        work_dir_add_srcs_list = list() # list of dict()s

        if dep is None:
            # if we weren't passed a dep, then use our target_node (str key for our self.deps_entry)
            dep = self.target_node

        # Run handler for this to convert to shell commands in self.command_design_ref
        shell_commands_list, work_dir_add_srcs_list = deps_commands_handler(
            config=self.command_design_ref.config,
            eda_args=self.command_design_ref.args,
            dep=dep,
            deps_file=self.deps_file,
            target_node=self.target_node,
            target_path=self.target_path,
            commands=commands
        )

        return shell_commands_list, work_dir_add_srcs_list

    def process_commands(self, commands=list(), dep=None):
        '''Returns None, handles commands (shell, etc) in the target that aren' in the 'deps' list.

        Applies these to self.command_design_ref.

        You can optionally call this with a commands list and a single dep, which we support for
        commands lists that exist within the 'deps' entry of a target.
        '''

        shell_commands_list, work_dir_add_srcs_list = self.get_commands(commands=commands, dep=dep)

        # add these commands lists to self.command_design_ref:
        # Process all shell_commands_list:
        # This will track each shell command with its target_node and target_path
        self.command_design_ref.append_shell_commands( cmds=shell_commands_list )
        # Process all work_dir_add_srcs_list:
        # This will track each added filename with its target_node and target_path
        self.command_design_ref.append_work_dir_add_srcs( add_srcs=work_dir_add_srcs_list )


    def process_deps_return_discovered_deps(self) -> list:
        '''Returns list of deps targets to continue processing,

        -- iterates through 'deps' for this target (self.deps_entry['deps'])
        -- applies to self.command_design_ref
        '''

        # Get the list of deps from this entry (entry is a target in our DEPS.yml):
        deps = deps_target_get_deps_list(
            self.deps_entry,
            target_node=self.target_node,
            deps_file=self.deps_file
        )
        return self.get_remaining_and_apply_deps(deps)

    def get_remaining_and_apply_deps(self, deps:list) -> list:

        deps_targets_to_resolve = list()

        # Process deps (list)
        for dep in deps:

            typ = type(dep)
            if typ not in Defaults.supported_dep_keys_by_type:
                self.error(f'{self.target_node=} {dep=} in {self.deps_file=}:' \
                           + f'has unsupported {type(dep)=} {Defaults.supported_dep_keys_by_type=}')

            for supported_type, supported_values in Defaults.supported_dep_keys_by_type.items():
                if '*' in supported_values:
                    continue
                if typ in [dict,list] and any([k not in supported_values for k in dep]):
                    self.error(f'{self.target_node=} {dep=} in {self.deps_file=}:' \
                               + f'has dict-key or list-item not in {Defaults.supported_dep_keys_by_type[typ]=}')

            # In-line commands in the deps list, in case the results need to be in strict file
            # order for other deps
            if type(dep) is dict and 'commands' in dep:

                commands = dep['commands']
                debug(f"Got commands {dep=} for {self.target_node=} in {self.deps_file=}, {commands=}")

                assert type(commands) is list, \
                    f'dep commands must be a list: {dep=} {self.deps_file=} {self.target_node=}'

                # For this, we need to get the returned commands (to keep strict order w/ other deps)
                command_tuple = self.get_commands( commands=commands, dep=dep )
                # TODO(drew): it might be cleaner to return a dict instead of list, b/c those are also ordered
                # and we can pass type information, something like:
                deps_targets_to_resolve.append(command_tuple)


            elif type(dep) is str and any(dep.startswith(x) for x in ['+define+', '+incdir']):
                # Note: we still support +define+ and +incdir in the deps list.
                # check for compile-time Verilog style plusarg, which are supported under targets
                # These are not run-time Verilog style plusargs comsumable from within the .sv:
                debug(f"Got plusarg (define, incdir) {dep=} for {self.target_node=} {self.deps_file=}")
                self.command_design_ref.process_plusarg(plusarg=dep, pwd=self.target_path)

            else:
                # If we made it this far, dep better be a str type.
                assert type(dep) is str, f'{dep=} {type(dep)=} must be str'
                dep_path = os.path.join(self.target_path, dep)
                debug(f"Got dep {dep_path=} for {self.target_node=} in {self.deps_file=}")

                if dep_path in self.command_design_ref.targets_dict or \
                   dep_path in deps_targets_to_resolve:
                    debug(" - already processed, skipping")
                elif os.path.exists(dep_path):
                    debug(" - raw file, adding to return list...")
                    deps_targets_to_resolve.append(dep_path) # append to list, keeping file order.
                else:
                    debug(f" - a target (not a file) needing to be resolved, adding to return list...")
                    deps_targets_to_resolve.append(dep_path) # append to list, keeping file order.

        # We return the list of deps or files that still need to be resolved (['full_path/some_target', ...])
        # items in this list are either:
        #  -- string (dep or file)
        #  -- tuple (unprocessed commands, in form: (shell_commands_list, work_dir_add_srcs_list))
        # TODO(drew): it might be cleaner to return a dict instead of list, b/c those are also ordered
        # and we can pass type information, something like:
        #  { dep1: 'file',
        #    dep2: 'target',
        #    dep3: 'command_tuple',
        #  }
        return deps_targets_to_resolve




def parse_deps_shell_str(line : str, target_path : str, target_node : str, enable : bool = True):
    '''Returns None or a dict of a possible shell command from line (str)

     Examples of 'line' str:
         shell@echo "hello world" > hello.txt
         shell@ generate_something.sh
         shell@ generate_this.py --input=some_data.json
         shell@ cp ./some_file.txt some_file_COPY.txt
         shell@ vivado -mode tcl -script ./some.tcl -tclargs foo_ip 1.2 foo_part foo_our_name {property value}

    Returns None if no parsing was performed, or if enable is False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''
    if not enable:
        return None

    m = re.match(r'^\s*shell\@(.*)\s*$', line)
    if not m:
        return None

    exec_str = m.group(1)
    exec_list = exec_str.split()

    # Look for path substitutions, b/c we later "work" in self.args['work-dir'], but
    # files should be relative to our target_path.
    exec_list = path_substitutions_relative_to_work_dir(exec_list=exec_list, info_str='shell@', target_path=target_path)

    d = {'target_path': os.path.abspath(target_path),
         'target_node': target_node,
         'exec_list': exec_list,
         }
    return d


def parse_deps_work_dir_add_srcs(line : str, target_path : str, target_node : str, enable : bool = True):
    '''Returns None or a dict describing source files to add from the work-dir path

     Examples of 'line' str:
         work_dir_add_srcs@ my_csrs.sv
         work_dir_add_srcs@ some_generated_file.sv some_dir/some_other.v ./gen-vhd-dir/even_more.vhd

    Returns None if no parsing was performed, or if enable is False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''
    if not enable:
        return None

    m = re.match(r'^\s*work_dir_add_srcs\@(.*)\s*$', line)
    if not m:
        return None

    files_str = m.group(1)
    file_list = files_str.split()

    d = {'target_path': os.path.abspath(target_path),
         'target_node': target_node,
         'file_list': file_list,
         }
    return d


def parse_deps_peakrdl(line : str, target_path : str, target_node : str, enable : bool = True,
                       tool : str = ''):
    '''Returns None or a dict describing a PeakRDL CSR register generator dependency

     Examples of 'line' str:
         peakrdl@ --cpuif axi4-lite-flat --top oc_eth_10g_1port_csrs ./oc_eth_10g_csrs.rdl

    Returns None if no parsing was performed, or if enable=False

    target_path (str) -- from dependency parsing (relative path of the DEPS file)
    target_node (str) -- from dependency parsing, the target containing this 'line' str.
    '''

    m = re.match(r'^\s*peakrdl\@(.*)\s*$', line)
    if not m:
        return None

    if not enable:
        warning(f'peakrdl: encountered peakrdl command in {target_path=} {target_node=},' \
                + ' however it is not enabled in edy.py - eda.config[dep_command_enables]')
        return None

    if not shutil.which('peakrdl') or \
       'peakrdl' not in globals().keys():

        error('peakrdl: is not present in shell path, or the python package is not avaiable,' \
              + f' yet we encountered a peakrdl command in {target_path=} {target_node=}')
        return None


    args_str = m.group(1)
    args_list = args_str.split()

    # Fish out the .rdl name
    # If there is --top=value or --top value, then fish out that value (that will be the
    # value.sv and value_pkg.sv generated names.

    sv_files = list()
    top = ''
    for iter,str_value in enumerate(args_list):
        if '--top=' in str_value:
            _, top = str_value.split('=')
        elif '--top' in str_value:
            if iter + 1 < len(args_list):
                top = args_list[iter + 1]

    for str_item in args_list:
        if str_item[-4:] == '.rdl':
            _, rdl_fileonly = os.path.split(str_item) # strip all path info
            rdl_filebase, rdl_ext = os.path.splitext(rdl_fileonly) # strip .rdl
            if top == '':
                top = rdl_filebase

    assert top != '', f'peakrdl@ DEP, could not determine value for {top=}: {line=}, {target_path=}, {target_node=}'

    sv_files += [ f'peakrdl/{top}_pkg.sv', f'peakrdl/{top}.sv' ]


    shell_commands = [
        [ 'peakrdl', 'regblock', '-o', 'peakrdl/'] + args_list,
        # Edit file to apply some verilator waivers, etc, from peakrdl_cleanup.py:
        [ 'python3', peakrdl_cleanup_py, f'peakrdl/{top}.sv', f'peakrdl/{top}.sv' ],
    ]

    ret_dict = {
        'shell_commands_list': list(), # Entry needs target_path, target_node, exec_list
        'work_dir_add_srcs': dict(),   # Single dict needs target_path, target_node, file_list
    }

    # Make these look like a dep_shell_command:
    for one_cmd_as_list in shell_commands:
        ret_dict['shell_commands_list'].append(
            parse_deps_shell_str(line = ' shell@ ' + ' '.join(one_cmd_as_list),
                                 target_path = target_path,
                                 target_node = target_node
                                 )
        )

    # Make the work_dir_add_srcs dict:
    ret_dict['work_dir_add_srcs'] = parse_deps_work_dir_add_srcs(line = ' work_dir_add_srcs@ ' + ' '.join(sv_files),
                                                                 target_path = target_path,
                                                                 target_node = target_node
                                                                 )

    return ret_dict



def deps_commands_handler(config: dict, eda_args: dict,
                          dep : str, deps_file : str, target_node : str, target_path : str,
                          commands : list):
    ''' Returns a tuple of (shell_commands_list, work_dir_add_srcs_list), from processing
        a DEPS.yml entry for something like:

        target_foo:
          deps:
            - some_file
            - commands: # (list of dicts) These are directly in a 'deps' list.
                - shell: ...
                - peakrdl: ...
                - work-dir-add-sources: ...
                - shell: ...

        target_foo:
          commands: # (list of dicts) These are in a target, but not ordered with other deps
             - shell: ...
             - peakrdl: ...
             - work-dir-add-sources: ...
             - shell: ...

        We'd like to handle the list in a 'commands' entry, supporting it in a few places in a DEPS.yml, so this
        this a generic way to do that. Currently these are broken down into Shell commands and Files
        that will be later added to our sources (b/c we haven't run the Shell commands yet, and the Files
        aren't present yet but we'd like them in our eda.py filelist in order.

    '''

    shell_commands_list = list()
    work_dir_add_srcs_list = list()

    for command in commands:
        assert type(command) is dict, \
            f'{type(command)=} must be dict, for {deps_file=} {target_node=} {target_path=} with {commands=}'

        for key in command.keys():
            if key not in Defaults.supported_command_keys:
                error(f'deps_helpers.process_commands - command {key=} not in {Defaults.supported_command_keys=}')

        var_subst_dict = dict() # this is per-command.
        if config['dep_command_enables'].get('var_subst_os_env', False) and \
           command.get('var-subst-os-env', False):
            var_subst_dict.update(os.env)
        if config['dep_command_enables'].get('var_subst_args', False) and \
           command.get('var-subst-args', False):
            var_subst_dict = eda_args

        tee_fpath = command.get('tee', None)

        for key,item in command.items():

            # skip the var-subst-* keys, since these types are bools
            if key.startswith('var-subst'):
                continue

            if key.startswith('tee'):
                continue

            # Optional variable substituion in commands
            if type(item) is str:
                item = line_with_var_subst(item, replace_vars_dict=var_subst_dict,
                                           target_node=target_node, target_path=deps_file)

            if key == 'shell':
                # For now, piggyback on parse_deps_shell_str:
                ret_dict = parse_deps_shell_str(
                    line = 'shell@ ' + item,
                    target_path = target_path,
                    target_node = target_node,
                    enable=config['dep_command_enables']['shell'],
                )
                # To support 'tee: <some-file>' need to append it to last
                # list item in ret_dict['exec_list'], and make it a util.ShellCommandList.
                if tee_fpath:
                    ret_dict['exec_list'] = ShellCommandList(ret_dict['exec_list'], tee_fpath=tee_fpath)
                assert ret_dict, f'shell command failed in {dep=} {target_node=} in {deps_file=}'
                shell_commands_list.append(ret_dict) # process this later, append to our to-be-returned tuple

            elif key in ['work-dir-add-srcs', 'work-dir-add-sources']:
                # For now, piggyback on parse_deps_work_dir_add_srcs:
                ret_dict = parse_deps_work_dir_add_srcs(
                    line = 'work_dir_add_srcs@ ' + item,
                    target_path = target_path,
                    target_node = target_node,
                    enable=config['dep_command_enables']['work_dir_add_srcs'],
                )
                assert ret_dict, f'work-dir-add-srcs command failed in {dep=} {target_node=} in {deps_file=}'

                work_dir_add_srcs_list.append(ret_dict) # process this later, append to our to-be-returned tuple

            elif key == 'peakrdl':
                # for now, piggyback on parse_deps_peakrdl:
                ret_dict = parse_deps_peakrdl(
                    line = 'peakrdl@ ' + item,
                    target_path = target_path,
                    target_node = target_node,
                    enable=config['dep_command_enables']['peakrdl'],
                    tool=eda_args.get('tool', '')
                )
                assert ret_dict, f'peakrdl command failed in {dep=} {target_node=} in {deps_file=}'

                # add all the shell commands:
                shell_commands_list += ret_dict['shell_commands_list'] # several entries.
                # all the work_dir_add_srcs:
                work_dir_add_srcs_list += [ ret_dict['work_dir_add_srcs'] ] # single entry append


            else:
                assert False, f'unknown {key=} in {command=}, {item=} {dep=} {target_node=} in {deps_file=}'

    return (shell_commands_list, work_dir_add_srcs_list)
