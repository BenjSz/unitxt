import os
import re
from pathlib import Path
import requests
import json
from .artifact import Artifact, Artifactory


COLLECTION_SEPARATOR = '.'
PATHS_SEP = ':'


class Catalog(Artifactory):
    name: str = None
    location: str = None


try:
    import unitxt

    default_catalog_path = os.path.dirname(unitxt.__file__) + "/catalog"
except ImportError:
    default_catalog_path = os.path.dirname(__file__) + "/catalog"


class LocalCatalog(Catalog):
    name: str = "local"
    location: str = default_catalog_path

    def path(self, artifact_identifier: str):
        return os.path.join(self.location, *(artifact_identifier + ".json").split(COLLECTION_SEPARATOR))

    def load(self, artifact_identifier: str):
        assert artifact_identifier in self, "Artifact with name {} does not exist".format(artifact_identifier)
        path = self.path(artifact_identifier)
        artifact_instance = Artifact.load(path)
        return artifact_instance

    def __getitem__(self, name) -> Artifact:
        return self.load(name)

    def __contains__(self, artifact_identifier: str):
        if not os.path.exists(self.location):
            return False
        path = self.path(artifact_identifier)
        if path is None:
            return False
        return os.path.exists(path) and os.path.isfile(path)



    def save_artifact(self, artifact: Artifact, artifact_identifier: str, overwrite: bool = False):
        assert isinstance(artifact, Artifact), f"Input artifact must be an instance of Artifact, got {type(artifact)}"
        if not overwrite:
            assert (
                artifact_identifier not in self
            ), f"Artifact with name {artifact_identifier} already exists in catalog {self.name}"
        path = self.path(artifact_identifier)
        os.makedirs(Path(path).parent.absolute(), exist_ok=True)
        artifact.save(path)


class GithubCatalog(LocalCatalog):
    name = "community"
    repo = "unitxt"
    repo_dir = "src/unitxt/catalog"
    user = "IBM"
    branch = "master"
    
    def prepare(self):
        self.location = f"https://raw.githubusercontent.com/{self.user}/{self.repo}/{self.branch}/{self.repo_dir}"
    
    def load(self, artifact_identifier: str):
        url = self.path(artifact_identifier)
        response = requests.get(url)
        data = response.json()
        return Artifact.from_dict(data)
    
    def __contains__(self, artifact_identifier: str):
        url = self.path(artifact_identifier)
        response = requests.head(url)
        return response.status_code == 200
        
        


def verify_legal_catalog_name(name):
    assert re.match('^[\w' + COLLECTION_SEPARATOR + ']+$', name),\
        'Catalog name should be alphanumeric, ":" should specify dirs (instead of "/").'


def add_to_catalog(artifact: Artifact, name: str, catalog: Catalog = None, overwrite: bool = False,
                   catalog_path: str = None):
    if catalog is None:
        if catalog_path is None:
            catalog_path = default_catalog_path
        catalog = LocalCatalog(location=catalog_path)
    verify_legal_catalog_name(name)
    catalog.save_artifact(artifact, name, overwrite=overwrite) # remove collection (its actually the dir).
    # verify name


