from ydata.profiling import ProfileReport
from ydata_profiling.config import Settings as Settings

def compare(reports: list[ProfileReport], config: Settings | None = None) -> ProfileReport: ...
