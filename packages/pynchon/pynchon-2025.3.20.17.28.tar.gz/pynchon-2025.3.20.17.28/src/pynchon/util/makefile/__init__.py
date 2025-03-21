"""pynchon.util.makefile"""

import os
import re
from fnmatch import fnmatch

from pynchon import abcs, cli
from pynchon.util.os import invoke

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)
_recipe_pattern = "#  recipe to execute (from '"
_variables_pattern = "# Variables"
_ht_stats_pattern = "# files hash-table stats:"


@cli.click.argument("makefile")
def database(makefile: str = "", make="make") -> typing.List[str]:
    """
    Get database for Makefile
    (This output comes from 'make --print-data-base')
    """
    LOGGER.critical(f"building database for {makefile}")
    assert makefile
    tmp = abcs.Path(makefile)
    if not all(
        [
            tmp.exists,
            tmp.is_file,
        ]
    ):
        raise ValueError(f"{makefile} does not exist")
    else:
        LOGGER.warning(f"parsing makefile @ {makefile}")
    cmd = f"{make} --print-data-base -pqRrs -f {makefile} > .tmp.mk.db"
    resp = invoke(cmd, system=True, command_logger=LOGGER.debug)
    out = open(".tmp.mk.db").read().split("\n")
    os.remove(".tmp.mk.db")
    return out


def _get_prov_line(body):
    pline = [x for x in body if _recipe_pattern in x]
    pline = pline[0] if pline else None
    return pline


def _get_file(body=None, makefile=None):
    pline = _get_prov_line(body)
    if pline:
        return pline.split(_recipe_pattern)[-1].split("'")[0]
    else:
        return str(makefile)


@cli.click.option("--target", help="Retrieves help for named target only")
@cli.click.flag("--markdown", help="Enriches docs by guessing at markdown formatting")
@cli.click.flag("--module-docs", help="Only return module docs")
@cli.click.argument("makefile")
def parse(
    makefile: str = None,
    target: str = "",
    bodies: bool = False,
    markdown: bool = False,
    include_private: bool = False,
    module_docs: bool = False,
    parse_target_aliases: bool = True,
    **kwargs,
):
    """
    Parse Makefile to JSON.  Includes targets/prereqs details and documentation.
    """

    def _enricher(text, pattern):
        """ """
        # raise Exception(text)
        pat = re.compile(pattern, re.MULTILINE)

        def rrr(match):
            label = match.group("label")
            indent = match.group("indent")
            content = match.group("content")
            dedented_content = re.sub(r"^[\t\s]{2,4}", "", content, flags=re.MULTILINE)
            code_block = (
                f"{indent}\n\nEXAMPLE:{label}\n\n```bash\n{dedented_content}```\n"
            )
            return code_block

        result = pat.sub(rrr, text)
        return result

    def _test(x):
        """ """
        tests = [
            ":" in x.strip(),
            not x.startswith("#"),
            not x.startswith("\t"),
        ]
        # if include_private:
        #     tests+=[not x.startswith("."),]
        return all(tests)

    def zip_markdown(docs):
        if isinstance(docs, (str,)):
            docs = docs.split("\n")
        rfmt = [""]
        while docs:
            tmp = docs.pop(0)
            if any([tmp.lstrip().startswith(x) for x in "* |".split()]) or any(
                [x in tmp for x in "USAGE: EXAMPLE: ```".split()]
            ):
                rfmt = rfmt + [tmp] + docs
                break
            if tmp.lstrip().startswith("---"):
                rfmt += [tmp]
                continue
            elif tmp:
                rfmt[-1] += f" {tmp}"
            else:
                rfmt += ["", tmp]
        return rfmt

    assert os.path.exists(makefile)
    wd = abcs.Path(".")
    db = database(makefile, **kwargs)
    original = open(makefile).readlines()
    variables_start = db.index(_variables_pattern)
    variables_end = db.index("", variables_start + 2)
    vars = db[variables_start:variables_end]
    db = db[variables_end:]
    implicit_rule_start = db.index("# Implicit Rules")
    file_rule_start = db.index("# Files")
    file_rule_end = db.index(_ht_stats_pattern)
    for i, line in enumerate(db[implicit_rule_start:]):
        if "implicit rules, " in line and line.endswith(" terminal."):
            implicit_rule_end = implicit_rule_start + i
            break
    else:
        LOGGER.critical("cannot find `implicit_rule_end`!")
        implicit_rule_end = implicit_rule_start
    implicit_targets_section = db[implicit_rule_start:implicit_rule_end]
    file_targets_section = db[file_rule_start:file_rule_end]
    file_target_names = list(filter(_test, file_targets_section))
    implicit_target_names = list(filter(_test, implicit_targets_section))
    targets = file_target_names + implicit_target_names
    out = {}
    targets = [t for t in targets if t != f"{makefile}:"]
    for tline in targets:
        if any(
            [
                tline.startswith(" ") or tline.startswith(x)
                for x in "$ @ & \t".split(" ")
            ]
        ):
            continue
        bits = tline.split(":")
        target_name = bits.pop(0)
        childs = ":".join(bits)
        type = "implicit" if tline in implicit_targets_section else "file"
        # NB: line nos are from reformatted output, not original file
        line_start = db.index(tline)
        line_end = db.index("", line_start)
        body = db[line_start:line_end]
        pline = _get_prov_line(body)
        file = _get_file(body=body, makefile=makefile)
        if pline:
            # take advice from make's database.
            # we return this because it's authoritative,
            # but actually sometimes it's wrong.  this returns
            # the first like of the target that's tab-indented,
            # but sometimes make macros like `ifeq` are not indented..
            lineno = pline.split("', line ")[-1].split("):")[0]
        else:
            try:
                lineno = original.index(tline)
            except ValueError:
                LOGGER.critical(f"cant find {tline} in {file}, parametric?")
                # target_name
                lineno = None
        lineno = lineno and (int(lineno) - 1)
        prereqs = [x for x in childs.split() if x.strip()]
        out[target_name] = dict(
            file=file,
            lineno=lineno,
            body=body,
            chain=None,
            type=type,
            docs=[x[len("\t@#") :] for x in body if x.startswith("\t@#")],
            prereqs=prereqs,
        )
        if type == "implicit":
            regex = target_name.replace("%", ".*")
            out[target_name].update(regex=regex)
    for target_name, tmeta in out.items():
        if "regex" in tmeta:
            implementors = []
            for impl in out:
                if impl != target_name and re.compile(tmeta["regex"]).match(impl):
                    implementors.append(impl)
            out[target_name]["implementors"] = implementors

    for target_name, tmeta in out.items():
        real_body = [
            b
            for b in tmeta["body"][1:]
            if not b.startswith("#") and not b.startswith("@#")
        ]
        if not real_body:
            LOGGER.critical(f"missing body for: {target_name}")
            for chain in out:
                if target_name in out[chain].get("implementors", []):
                    tmeta["chain"] = chain
            if len(tmeta["prereqs"]) == 1:
                tmeta["chain"] = tmeta["prereqs"][0]
        else:
            tmeta["chain"] = []
        out[target_name] = tmeta

    for target_name, tmeta in out.items():
        # if this is a simple alias with no docs, pull the docs from the principal
        if not tmeta["docs"] and tmeta["chain"]:
            out[target_name]["docs"] = out[tmeta["chain"]]["docs"]
        # user requested enriching docs with markdown
        if markdown:
            docs = [x.lstrip() for x in out[target_name]["docs"]]
            for i, line in enumerate(docs):
                if line.startswith("EXAMPLE:") or line.startswith("USAGE:"):
                    docs[i] = (
                        line.replace("EXAMPLE:", "*EXAMPLE:*")
                        .replace("USAGE:", "*USAGE:*")
                        .replace("REFS:", "*REFS:*")
                        + "\n```bash"
                    )
                    for j, line2 in enumerate(docs[i:]):
                        if not line2:
                            docs[i + j] = line2 + "```\n"
                            break
            out[target_name]["docs"] = zip_markdown(docs)

    # user requested no target-bodies should be provided
    if not bodies:
        tmp = {}
        for k, v in out.items():
            v.pop("body", [])
            tmp[k] = v
        out = tmp

    # user requested private-targets should not be included
    if not include_private:
        LOGGER.warning("Popping all the private-targets..")
        tmp = {}
        for k, v in out.items():
            if not k.startswith("."):
                tmp[k] = v
        out = tmp
    else:
        LOGGER.warning("Including private-targets..")

    # user requested target aliases should be treated
    if parse_target_aliases:
        tmp = {}
        for aliases_maybe, v in out.items():
            aliases = aliases_maybe.split(" ")
            if len(aliases) > 1:
                primary = aliases.pop(0)
                tmp[primary] = v
                for alias in aliases:
                    tmp[alias] = {
                        **v,
                        **dict(
                            alias=True,
                            primary=primary,
                            docs=[f"(Alias for '{primary}')"],
                        ),
                    }
            else:
                tmp[aliases_maybe] = v
        out = tmp

    # user requested target-search
    if target:
        out = out[target]

    parametric = [k.replace("%", "*") for k in out.keys() if k.endswith("%")]
    dupes = []
    for k in out.keys():
        if k.endswith("%"):
            continue
        for p in parametric:
            if fnmatch(k, p):
                dupes.append(k)
                break
    LOGGER.debug(
        f"apparent targets are actually duplicates of parametric ones: {dupes}"
    )
    for k in dupes:
        out.pop(k)

    # user requested lookup string or module docs
    if module_docs:
        modules = []
        blocks = {}
        for k in out.keys():
            k = k.strip().lstrip()
            k = k.split(".")[0]
            if not k:
                continue
            if k[0] in "_ \t $ self".split():
                continue
            if any([x in k for x in "& /".split(" ")]):
                continue
            if k not in modules:
                modules.append(k)
        LOGGER.debug(f"found modules: {modules}")
        lines = open(makefile).readlines()
        for i, line in enumerate(lines):
            line = line.lstrip()
            if not line.startswith("#") and not line.startswith("@#"):
                continue
            if "BEGIN" in line:
                blockend = len(lines)
                for j, l2 in enumerate(lines[i:]):
                    if not l2.strip():
                        block_end = i + j - 1
                        break
                found = None
                for mod in modules:
                    if mod in line:
                        found = mod
                        break
                if not found:
                    LOGGER.warning(f"could not find module for block: {line}")
                    blocks[line[line.index("BEGIN") :].strip()] = lines[
                        i + 1 : block_end
                    ]
                else:
                    blocks[found] = lines[i:block_end]
        blocks = {
            k: [line[len("## ") :].strip() for line in v] for k, v in blocks.items()
        }
        for k, v in blocks.items():
            blocks[k] = zip_markdown(v[1:])

        if module_docs:
            return blocks
    return out


parser = parse
