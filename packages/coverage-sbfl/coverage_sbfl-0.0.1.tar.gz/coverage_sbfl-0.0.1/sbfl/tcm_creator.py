# PYTHON_ARGCOMPLETE_OK
from tempfile import NamedTemporaryFile as mktemp
import sys
import json
import subprocess
import re
import os
from os.path import dirname
from os import path as osp
from enum import Enum

from typing import Dict, List, Optional, Iterable

import argparse
import argcomplete

from coverage import Coverage
from coverage.report_core import get_analysis_to_report
from coverage.types import TMorf

from sbfl import method_defs


def read_coverage_json(json_cov_file, method=False, basedir=None):
    """
    Extract coverage from coverage.py's json file
    """
    js = json.load(open(json_cov_file))
    tests = set()
    locs: List[str] = []
    coverage: Dict[str, List[int]] = {}
    defs_dict: Dict[str, Optional[method_defs.Container]] = {}
    test_re = re.compile("^(.*).py::(.*?)(\\[.*?\\])?(\\|\\w+)?$")
    rm_test_prefix_re = re.compile("(?<=\\b)tests?\\.(?!([A-Z]|[^.] ))")
    for file, content in js['files'].items():
        if (method):  # get the methods from the file
            if (file not in defs_dict):
                try:
                    defs_dict[file] = method_defs.get_defs(osp.join(basedir, file))
                except FileNotFoundError:
                    defs_dict.setdefault(file, None)
                    print("WARNING: could not find file",
                          osp.join(basedir, file), "for method level")
            cur_defs = defs_dict[file]
        for line, context in content['contexts'].items():
            if (not method):
                loc = str(file) + ":" + str(line)
            elif (cur_defs is None):
                loc = str(file) + ":<module>:" + str(line)
            else:
                def_list = cur_defs.get_def_list(int(line))
                loc = '.'.join([str(file)] + def_list[:-1]) + ":" + \
                    def_list[-1] + ":" + str(line)
            if (loc in locs):
                j = locs.index(loc)
            else:
                j = len(locs)
                locs.append(loc)
            for test in context:
                # Format test name
                test = test.replace("\n", "\\n")
                matchr = re.match(test_re, test)
                if (matchr is not None):
                    test = matchr.group(1).replace("/", ".") + "." + \
                           matchr.group(2).replace("::()", "").replace("::", ".") + \
                           str(matchr.group(3) or '')
                test = re.sub(rm_test_prefix_re, "", test).replace(" ", "")
                # Check for default context
                if (test == ""):
                    continue
                # Add test if unique
                tests.add(test)
                coverage.setdefault(test, []).append(j)
    return tests, locs, coverage


def read_coverage(cov_file, method=False, basedir=None,
                  morfs: Iterable[TMorf] = None):
    """
    Extract coverage from coverage.py's json file
    """
    cov = Coverage(data_file=cov_file)
    cov.load()
    cov_data = cov.get_data()
    tests = set()
    locs: List[str] = []
    coverage: Dict[str, List[int]] = {}
    defs_dict: Dict[str, Optional[method_defs.Container]] = {}
    test_re = re.compile("^(.*).py::(.*?)(\\[.*?\\])?(\\|\\w+)?$")
    rm_test_prefix_re = re.compile("(?<=\\b)tests?\\.(?!([A-Z]|[^.] ))")
    for file_reporter, analysis in get_analysis_to_report(cov, morfs):
        file = file_reporter.relative_filename()
        if (method):  # get the methods from the file
            if (file not in defs_dict):
                try:
                    defs_dict[file] = method_defs.get_defs(osp.join(basedir,
                                                                    file))
                except FileNotFoundError:
                    defs_dict.setdefault(file, None)
                    print("WARNING: could not find file",
                          osp.join(basedir, file), "for method level")
            cur_defs = defs_dict[file]
        for line, context in cov_data.contexts_by_lineno(analysis.filename).items():
            if (not method):
                loc = str(file) + ":" + str(line)
            elif (cur_defs is None):
                loc = str(file) + ":<module>:" + str(line)
            else:
                def_list = cur_defs.get_def_list(int(line))
                loc = '.'.join([str(file)] + def_list[:-1]) + ":" + \
                    def_list[-1] + ":" + str(line)
            if (loc in locs):
                j = locs.index(loc)
            else:
                j = len(locs)
                locs.append(loc)
            for test in context:
                # Format test name
                test = test.replace("\n", "\\n")
                matchr = re.match(test_re, test)
                if (matchr is not None):
                    test = matchr.group(1).replace("/", ".") + "." + \
                           matchr.group(2).replace("::()", "").replace("::", ".") + \
                           str(matchr.group(3) or '')
                test = re.sub(rm_test_prefix_re, "", test).replace(" ", "")
                # Check for default context
                if (test == ""):
                    continue
                # Add test if unique
                tests.add(test)
                coverage.setdefault(test, []).append(j)
    return tests, locs, coverage


def read_errs(err_file):
    """
    Extract pass/fail info from test framework's output
    """
    if (err_file is None):
        return None
    if (subprocess.getoutput('head -n1 {} | grep unittest'.format(err_file))):
        all_failed = subprocess.getoutput('grep "^\\(ERROR\\|FAIL\\):" '
                                          '{}'.format(err_file))
        pat = "^(?:ERROR|FAIL): (\\S+) \\((.*)\\)"
        failed = all_failed.splitlines()
        for i in range(len(failed)):
            match = re.match(pat, failed[i])
            if (match is not None):
                failed[i] = match.group(2) + "." + match.group(1)
    else:
        all_failed = subprocess.getoutput('grep "^\\(FAIL\\|FAILED\\|ERROR\\)'
                                          '\\s\\+[^(]" {}'.format(err_file))
        failed = []
        raw_failed = all_failed.splitlines()
        for raw_failure in raw_failed:
            matchr = re.match("^(FAIL|FAILED|ERROR)\\s+(.*).py::(.*?)(\\[.*?\\])?( - |$)",
                              raw_failure)
            if (matchr is not None):
                failure = re.sub("tests?\\.(?!([A-Z]|[^.] ))", "",
                                 matchr.group(2).replace("/", ".")) + "." + \
                        matchr.group(3).replace("::()", "").replace("::", ".") + \
                        str(matchr.group(4) or '')
                failed.append(failure)
    return failed


def get_status(test, failed):
    if (failed is None):
        return "PASSED"
    return "FAILED" if any(fail.endswith(test) or test.endswith(fail)
                           for fail in failed) else "PASSED"


def print_tcm(tests, locs, coverage, failed, tcm_file):
    """
    Output the collected coverage in TCM format to the output file (tcm_file)
    given
    """
    with open(tcm_file, 'w') as tcm:
        print("#tests", file=tcm)
        for test in sorted(tests):
            status = get_status(test, failed)
            print(test, status, file=tcm)
        print(file=tcm)
        print("#uuts", *locs, sep="\n", file=tcm)
        print(file=tcm)
        print("#matrix", file=tcm)
        for test in sorted(coverage):
            for i, loc in enumerate(coverage[test]):
                end = " " if i != len(coverage[test])-1 else ""
                print(loc, 1, end=end, file=tcm)
            print(file=tcm)


def annotate_tcm(tcm_file, failed=None, basedir=None):
    """
    Read in the TCM file (tcm_file) given and annotate with the new failed
    information given in failed and/or method names from the project located at
    basedir.
    """
    class Phase(Enum):
        NONE = 0
        TEST = 1
        UUTS = 2
        MATRIX = 3
    tmp_name = None
    cur_file = None
    cur_defs = None
    try:
        with open(tcm_file) as tcm, mktemp(mode='wt', dir=dirname(tcm_file),
                                           delete=False) as tmp:
            tmp_name = tmp.name
            phase = Phase(0)
            for l in tcm:
                line = l.strip()
                if (line == "#tests"):
                    phase = Phase.TEST
                elif (line == "#uuts"):
                    phase = Phase.UUTS
                elif (line == '#matrix'):
                    phase = Phase.MATRIX
                elif (failed is not None and phase == Phase.TEST and
                      (m := re.match("^(.*) (PASSED|FAILED)$", line))):
                    test = m.group(1)
                    status = get_status(test, failed)
                    print(test, status, file=tmp)
                    continue
                elif (basedir is not None and phase == Phase.UUTS and
                      (m := re.match("^([^:]+):(\\d+)(.*)$", line))):
                    file, line_no = m.group(1, 2)
                    if (cur_file is None or file != cur_file):
                        cur_file = file
                        try:
                            cur_defs = method_defs.get_defs(osp.join(basedir,
                                                                     file))
                        except FileNotFoundError:
                            cur_defs = None
                            print("WARNING: could not find file",
                                  osp.join(basedir, file), "for method level")
                    if (cur_defs is None):
                        def_list = ['<module>']
                    else:
                        def_list = cur_defs.get_def_list(int(line_no))
                    print('.'.join([file] + def_list[:-1]) + ":" + def_list[-1]
                          + ":" + line_no + m.group(3), file=tmp)
                    continue
                print(line, file=tmp)
    except OSError as err:
        if (tmp_name and os.path.isfile(tmp_name)):
            os.remove(tmp_name)
        raise err
    else:
        os.replace(tmp_name, tcm_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convert coverage.py coverage files into TCM format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--coverage-file', default='.coverage',
                        help='The coverage.py coverage file to process, '
                        'either in binary or JSON format.',
                        dest='cov_file')
    parser.add_argument('-o', '--output-file', default='coverage.tcm',
                        help='The output file for storing the TCM',
                        dest='tcm_file')
    parser.add_argument('-e', '--test-result-file', dest='err_file',
                        help='The output of the testing framework (pytest or \
                        unittest) showing which tests failed')
    parser.add_argument('-a', '--annotate-failed', action='store_true',
                        dest='failed', help='Re-annotate the TCM file already '
                        'generated with the failure information contained in '
                        'the test result file. NOTE: The output TCM file given'
                        ' MUST already exist for this option')
    parser.add_argument('-m', '--add-method-level', action='store_true',
                        default=True, dest='method', help='Add method level '
                        'information to the TCM. If the TCM file given '
                        'already exists, this option will re-annotate it with '
                        'method level information. This option is the '
                        'default, see -M to disable method level information')
    parser.add_argument('-M', '--no-method-level', action='store_false',
                        default=argparse.SUPPRESS,
                        dest='method', help='Do not add method level '
                        'information to the TCM. This is the inverse of the '
                        '-m option, see that option for description')
    parser.add_argument('-p', '--project-dir', action='store', dest='basedir',
                        default='.', help='Extract method level information '
                        'from the project located at PROJECT_DIR (default: '
                        '%(default)s i.e. current directory)')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    # Append to the existing TCM file
    if (args.failed or (args.method and osp.isfile(args.tcm_file))):
        print(f"TCM file \"{args.tcm_file}\" found, annotating...")
        failed = read_errs(args.err_file) if args.failed else None
        basedir = osp.abspath(args.basedir) if args.method else None
        annotate_tcm(args.tcm_file, failed=failed, basedir=basedir)
    else:  # Generate a new TCM file
        print(f"Creating new TCM file \"{args.tcm_file}\"...")
        if (not osp.isfile(args.cov_file)):
            raise FileNotFoundError(f"Coverage file \"{args.cov_file}\" does "
                  "not exist! Please run coverage.py before using this script")
        if (args.cov_file.endswith(".json")):
            tests, locs, coverage = read_coverage_json(args.cov_file,
                                                       args.method,
                                                       osp.abspath(args.basedir))
        else:
            tests, locs, coverage = read_coverage(args.cov_file, args.method,
                                                  osp.abspath(args.basedir))
        if (not hasattr(args, 'err_file') or args.err_file is None):
            print("WARNING: No error file given. Consider specifying an error "
                  "file with -e <erorr file>", file=sys.stderr)
        failed = read_errs(args.err_file)
        print_tcm(tests, locs, coverage, failed, args.tcm_file)


if __name__ == "__main__":
    main()
