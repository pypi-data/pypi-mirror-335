from nemo_library.features.nemo_persistence_api import deleteProjects
from nemo_library.features.nemo_persistence_api import getProjects
from nemo_library.utils.config import Config

__all__ = ["MigManDeleteProjects"]


def MigManDeleteProjects(config: Config) -> None:
    projects = getProjects(config)
    to_delete = [
        project.id
        for project in projects
        if not project.displayName in ["Business Processes", "Master Data"]
    ]
    deleteProjects(config, to_delete)
