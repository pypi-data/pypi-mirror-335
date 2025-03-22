from typing import List, Optional

#from ydata_profiling.compare_reports import compare as _compare
from ydata_profiling.config import Settings

from ydata.profiling import ProfileReport
from ydata.profiling.oss_compare import compare as _compare

def _disable_outliers(reports: List[ProfileReport]):
    for report in reports:
        report._outlier = False
        report.description_set.outliers = {}


def compare(
    reports: List[ProfileReport],
    config: Optional[Settings] = None,
) -> ProfileReport:
    _disable_outliers(reports)
    profile = _compare(reports, config)
    profile.__class__ = ProfileReport
    profile.config.vars.cat.redact = True
    return profile
