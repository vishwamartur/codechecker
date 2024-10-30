# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

import logging
from typing import List

from codechecker_report_converter.report import (Report,
                                                 get_or_create_file,
                                                 File)

from typing import Dict
import os
import json
from ..analyzer_result import AnalyzerResultBase

LOG = logging.getLogger('report-converter')


class AnalyzerResult(AnalyzerResultBase):
    """ Transform analyzer result of the PVS-Studio analyzer. """

    TOOL_NAME = 'pvs-studio'
    NAME = 'PVS-Studio'
    URL = 'https://pvs-studio.com/en/'

    __severities = ["UNSPECIFIED", "HIGH", "MEDIUM", "LOW"]

    def get_reports(self, file_path: str) -> List[Report]:
        """ Get reports from the PVS-Studio analyzer result. """

        reports: List[Report] = []

        if not os.path.exists(file_path):
            LOG.info("Report file does not exist: %s", file_path)
            return reports

        try:
            with open(file_path,
                      "r",
                      encoding="UTF-8",
                      errors="ignore") as report_file:
                bugs = json.load(report_file)['warnings']
        except (IOError, json.decoder.JSONDecodeError):
            LOG.warning("Failed to parse the given analyzer result '%s'. Please "
                        "give a valid json file generated by PVS-Studio.",
                        file_path)
            return reports

        file_cache: Dict[str, File] = {}
        for bug in bugs:
            bug_positions = bug['positions']

            for position in bug_positions:
                if not os.path.exists(position['file']):
                    LOG.warning(
                        "Source file does not exist: %s",
                        position['file']
                    )
                    continue

                reports.append(Report(
                    get_or_create_file(
                        os.path.abspath(position['file']),
                        file_cache
                    ),
                    position['line'],
                    position['column'] if position.get('column') else 0,
                    bug['message'],
                    bug['code'],
                    severity=self.get_diagnostic_severity(bug.get('level'))
                ))

        return reports

    def get_diagnostic_severity(self, level: int) -> str:
        return self.__severities[level]
