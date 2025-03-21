import re
from pathlib import Path

from dblocks_core.config.config import logger
from dblocks_core.model import config_model, plugin_model
from rich.console import Console
from rich.prompt import Prompt

from dblocks_core import exc

_VALID_SCENARIOS = ["drop", "create", "cleanup", "drop-only"]

# regular expressions building blocks
_WS = r"\s+"
_MAYBE_WS = r"\s*"
_CREATE = "create"
_SET = "set +|multiset +"
_TABLE = "table"
_IDENTIFIER = "[a-z0-9_.]+"
_AS = "as"
_PATTERN = (
    _CREATE
    + _WS
    + "("
    + _SET
    + ")?"
    + _MAYBE_WS
    + _TABLE
    + _WS
    + "(?P<IDENT>"
    + _IDENTIFIER
    + ")"
)
_PATTERN2 = (
    _CREATE
    + _WS
    + _TABLE
    + _WS
    + "(?P<IDENT>"
    + _IDENTIFIER
    + ")"
    + _AS
    + _WS
    + _IDENTIFIER
)

# regular expressions used to find what is needed
_re_create = re.compile(_PATTERN, re.I)
_re_create2 = re.compile(_PATTERN2, re.I)
_re_condition = re.compile(r"\/\*--conditional_create--\*\/", re.I)


# the template inected into SQL files
_TEMPLATE_CREATE = """-----------------------------------------------------------------------
/*--conditional_create--*/
select count(*) from dbc.tablesV 
where tablename='<table>' and databasename=( select database )
having count(*) > 0;

.IF ERRORCODE <> 0 THEN .QUIT 10;
.IF ACTIVITYCOUNT = 0 THEN .GOTO TABLE_DOES_NOT_EXIST;
.REMARK 'tabulka EXISTUJE'
.GOTO KONEC

.LABEL TABLE_DOES_NOT_EXIST
-----------------------------------------------------------------------
"""

_TEMPLATE_DROP = """-----------------------------------------------------------------------
/*--conditional_create--*/
select count(*) from dbc.tablesV 
where tablename='<table>' and databasename=( select database )
having count(*) > 0;

.IF ERRORCODE <> 0 THEN .QUIT 10;
.IF ACTIVITYCOUNT = 0 THEN .GOTO TABLE_DOES_NOT_EXIST;
.REMARK 'tabulka EXISTUJE'
drop table <table>;

.LABEL TABLE_DOES_NOT_EXIST
-----------------------------------------------------------------------
"""


def _load_script(file: Path, input_encoding: str):
    """loads the script, and filters out the header and footer of the conditional create.

    Args:
        file (Path): path to the file
        input_encoding (str): encoding used to load the file

    Returns:
        _type_: _description_
    """
    outLines = []
    with open(file, "r", encoding=input_encoding) as f:
        script = f.read()

        # pokud neobsahuje ".LABEL TABLE_DOES_NOT_EXIST", není tam co řešit
        if ".LABEL TABLE_DOES_NOT_EXIST" not in script:
            return script

        # jinak ale musíme filtrovat
        lines = script.splitlines()
        skipThis = True
        readNext = False

        for line in lines:
            if line == ".LABEL TABLE_DOES_NOT_EXIST":
                readNext = True
                continue
            if readNext:
                skipThis = False
                readNext = False
                continue

            if line == ".LABEL KONEC":
                break

            if skipThis:
                continue

            outLines.append(line)

    return "\n".join(outLines)


def _is_create_script(insides: str, file: str):
    if m := _re_create.search(insides):
        parts = m.group("IDENT").split(".")
        if len(parts) == 1:
            return True, parts[0]
        return True, parts[1]
    elif m := _re_create2.search(insides):
        parts = m.group("IDENT").split(".")
        if len(parts) == 1:
            return True, parts[0]
        return True, parts[1]
    else:
        raise exc.DOperationsError(f"did not find name of the table: {file}")


def _change_to_conditional(
    file: Path,
    output_encoding: str,
    input_encoding: str,
    create_or_drop="create",
):
    try:
        old_script = _load_script(file, input_encoding)
    except UnicodeDecodeError as e:
        raise exc.DOperationsError(f"encoding error: {file.as_posix()}")

    is_create, creates_table = _is_create_script(old_script, file)

    if not is_create:
        return False

    new_script = ""

    if create_or_drop == "cleanup":
        new_script = old_script

    else:
        TEMPLATE = _TEMPLATE_CREATE if create_or_drop == "create" else _TEMPLATE_DROP
        inject = TEMPLATE.replace("<table>", creates_table)
        if create_or_drop == "drop-only":
            old_script = "--only drop the table, do not create\n\n"
        new_script = inject + old_script + "\n" + ".LABEL KONEC"

    # save
    if new_script != old_script:
        logger.info(f"writing: {file.as_posix()}")
        try:
            with open(file, "w", encoding=output_encoding) as f:
                f.write(new_script)
        except Exception as e:
            logger.error(f"check this file, it may have been lost: {file.as_posix()}")


class CC(plugin_model.PluginWalker):
    def __init__(self):
        self.files = []

    def before(
        self,
        path: Path,
        environment: str | None,
        cfg: config_model.Config,
        **kwargs,
    ):
        """This function is executed before the walk starts."""
        pass

    def walker(
        self,
        path: Path,
        environment: str | None,
        cfg: config_model.Config,
        **kwargs,
    ):
        """This function is executed for each file we walk through."""
        ext = path.suffix.lower()
        if ext in (".bteq", ".sql"):
            self.files.append(path)

    def after(
        self,
        path: Path,
        environment: str | None,
        cfg: config_model.Config,
        **kwags,
    ):
        self._conditional_create()

    def _conditional_create(
        self,
        scenario="create",
        input_encoding: str = "utf-8",
        output_encoding: str = "utf-8",
        max_files: int = 20,
    ):
        """
        Scans a folder for files with .sql or .bteq extension, and tries to insert conditional create header and footer in them.
        Raises a ContentError when the number of files is > max_files.

        Args:
            folder (str): input folder
            scenario (str, optional): ["drop", "create", "cleanup", "drop-only"], defaults to "create".
            input_encoding (str, optional): defaults to "utf-8".
            output_encoding (str, optional): defaults to "utf-8".
            max_files (int, optional): defaults to 20.

        Raises:
            ContentError: raised when number of files is too great, or when one of the files can not be patched.
        """
        files = self.files
        if len(files) > max_files:
            console = Console()
            console.print(f"Expected to get at max {max_files}, got {len(files)}")
            answer = Prompt.ask("continue? [Y/n]")
            if answer != "Y":
                console.print("Canceled.", style="bold red")
                return

        for f in files:
            _change_to_conditional(f, output_encoding, input_encoding, scenario)


PLUGINS = [
    CC(),
]
