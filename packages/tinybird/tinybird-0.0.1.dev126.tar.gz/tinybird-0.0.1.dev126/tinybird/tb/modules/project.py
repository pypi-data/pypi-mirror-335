import glob
import re
from pathlib import Path
from typing import Dict, List, Optional

from tinybird.tb.modules.datafile.common import Datafile
from tinybird.tb.modules.datafile.parse_datasource import parse_datasource
from tinybird.tb.modules.datafile.parse_pipe import parse_pipe


class Project:
    extensions = ("datasource", "pipe", "connection")

    def __init__(self, folder: str):
        self.folder = folder

    @property
    def path(self) -> Path:
        return Path(self.folder)

    @property
    def vendor_path(self) -> str:
        return f"{self.path}/vendor"

    def get_project_files(self) -> List[str]:
        project_files: List[str] = []
        for extension in self.extensions:
            for project_file in glob.glob(f"{self.path}/**/*.{extension}", recursive=True):
                if self.vendor_path in project_file:
                    continue
                project_files.append(project_file)
        return project_files

    def get_resource_path(self, resource_name: str, resource_type: str) -> Optional[str]:
        full_path = next((p for p in self.get_project_files() if p.endswith(resource_name + f".{resource_type}")), "")
        if not full_path:
            return None
        return Path(full_path).relative_to(self.path).as_posix()

    def get_vendor_files(self) -> List[str]:
        vendor_files: List[str] = []
        for project_file in glob.glob(f"{self.vendor_path}/**/*.datasource", recursive=False):
            vendor_files.append(project_file)
        return vendor_files

    @property
    def datasources(self) -> List[str]:
        return sorted([Path(f).stem for f in glob.glob(f"{self.path}/**/*.datasource", recursive=False)])

    @property
    def pipes(self) -> List[str]:
        return sorted([Path(f).stem for f in glob.glob(f"{self.path}/**/*.pipe", recursive=False)])

    @property
    def connections(self) -> List[str]:
        return sorted([Path(f).stem for f in glob.glob(f"{self.path}/**/*.connection", recursive=False)])

    def get_pipe_datafile(self, filename: str) -> Optional[Datafile]:
        try:
            return parse_pipe(filename).datafile
        except Exception:
            return None

    def get_datasource_datafile(self, filename: str) -> Optional[Datafile]:
        try:
            return parse_datasource(filename).datafile
        except Exception:
            return None

    def get_datafile(self, filename: str) -> Optional[Datafile]:
        if filename.endswith(".pipe"):
            return self.get_pipe_datafile(filename)
        elif filename.endswith(".datasource"):
            return self.get_datasource_datafile(filename)
        return None

    def get_project_datafiles(self) -> Dict[str, Datafile]:
        project_filenames = self.get_project_files()
        datafiles: Dict[str, Datafile] = {}
        for filename in project_filenames:
            if datafile := self.get_datafile(filename):
                datafiles[filename] = datafile
        return datafiles

    @staticmethod
    def is_endpoint(content: str) -> bool:
        return re.search(r"TYPE endpoint", content, re.IGNORECASE) is not None
