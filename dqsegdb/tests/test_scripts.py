# -*- coding: utf-8 -*-

"""Tests for the DQSEGDB scripts
"""

import subprocess
import sys
from pathlib import Path

import pytest

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

# -- utilities --------------

if pytest.__version__ < "3.0.0":
    yield_fixture = pytest.yield_fixture
else:
    yield_fixture = pytest.fixture

# homebrew tmp_path fixture for old pytest
if pytest.__version__ < "3.9.1":
    @yield_fixture
    def tmp_path():
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)


def find_script_path(name):
    """Find the path of the script with the given ``name``

    This is a naive function that tries a few different places
    to discover where the script might be.

    Examples
    --------
    From the git repo:

    >>> find_script_path("ligolw_segment_query_dqsegdb")
    PosixPath('/home/user/git/dqsegdb/bin/ligolw_segment_query_dqsegdb')

    From an environment:

    >>> find_script_path("ligolw_segment_query_dqsegdb")
    PosixPath('/opt/bin/ligolw_segment_query_dqsegdb')
    """
    import dqsegdb
    dqsegdb_path = Path(dqsegdb.__file__)
    pyxy = f"{sys.version_info.major}.{sys.version_info.minor}"
    for path in (
        # standard environment layout
        # (work back through lib/pythonX.Y/site-packages/dqsegdb/)
        dqsegdb_path.parent.parent.parent.parent.parent / "bin",
        # git repo layout
        dqsegdb_path.parent.parent / "bin",
        # setup.py build layout
        dqsegdb_path.parent.parent / f"scripts-{pyxy}",
        dqsegdb_path.parent.parent.parent / f"scripts-{pyxy}",
    ):
        guess = path / name
        if guess.is_file():
            return guess
    raise RuntimeError(
        f"cannot find '{name}' in a predictable location",
    )


def run_script(script, *args, check=True, **kwargs):
    """Run a script with the given arguments

    Parameters
    ----------
    script : `str`, `pathlib.Path`
        the path of the script to run

    *args
        the arguments to pass to the script

    check : `bool`, optional
        if `True`, raise a `subprocess.CalledProcessError` is the
        script fails

    **kwargs
        keyword arguments to pass to `subprocess.run`

    Returns
    -------
    proc : `subprocess.CompletedProcess`
    """
    return subprocess.run(
        [
            sys.executable,
            str(script),
            *args,
        ],
        check=check,
        **kwargs,
    )


def load_segment_tables(path):
    """Load the three segment tables from the given XML file path

    Returns
    -------
    segdeftable : `glue.ligolw.lsctables.SegmentDefTable`
    segsumtable : `glue.ligolw.lsctables.SegmentSumTable`
    segtable : `glue.ligolw.lsctables.SegmentTable`
    """
    from glue.ligolw import lsctables
    from glue.ligolw.ligolw import LIGOLWContentHandler
    from glue.ligolw.utils import load_filename

    @lsctables.use_in
    class ContentHandler(LIGOLWContentHandler):
        pass

    xmldoc = load_filename(path, contenthandler=ContentHandler)
    return (
        lsctables.SegmentDefTable.get_table(xmldoc),
        lsctables.SegmentSumTable.get_table(xmldoc),
        lsctables.SegmentTable.get_table(xmldoc),
    )


# -- tests ------------------

def test_ligolw_segment_insert_dqsegdb_output(tmp_path):
    """Test that ligolw_segment_insert_dqsegdb correctly formats a file

    This isn't a very thorough test, but it's better than nothing.
    """
    # write known and active segments to a file
    known = [
        (0, 10),
        (20, 30),
    ]
    active = [
        (0, 2),
        (3, 5),
        (25, 30),
    ]
    for name, seglist in (
        ("known.txt", known),
        ("active.txt", active),
    ):
        with open(tmp_path / name, "w") as file:
            for seg in seglist:
                print(f"{seg[0]} {seg[1]}", file=file)

    # run ligolw_segment_insert_dqsegdb
    run_script(
        find_script_path("ligolw_segment_insert_dqsegdb"),
        "--insert",
        "--ifos=X1",
        "--name=TEST",
        "--version=0",
        "--segment-url=http://example.com",
        f"--summary-file={tmp_path}/known.txt",
        f"--segment-file={tmp_path}/active.txt",
        f"--output={tmp_path}/result.xml.gz",
        "--explain='test'",
        "--comment='test'",
    )

    # validate the output
    segdef, segsum, seg = load_segment_tables(tmp_path / "result.xml.gz")
    assert len(segdef) == 1
    assert [(s.start_time, s.end_time) for s in segsum] == known
    assert [(s.start_time, s.end_time) for s in seg] == active
