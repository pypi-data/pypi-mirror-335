from abc import abstractmethod, ABC
from pathlib import Path


class Dir(ABC):
    def __init__(self, path):
        self._path = path

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @property
    def path(self):
        return self._path


class CurrentSourceDir(Dir):
    def __init__(self):
        super().__init__(None)

    def __hash__(self):
        return hash(None)

    def __eq__(self, other):
        if not isinstance(other, CurrentSourceDir):
            return False
        return True


class SourceDir(Dir):
    def __init__(self, path: Path):
        super().__init__(Path(path))

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other: Dir):
        return self.path == other.path


class RootRelativeSourceDir(SourceDir):
    def __init__(self):
        from iprm.core.session import Session
        super().__init__(Path(Session.root_relative_source_dir()))
