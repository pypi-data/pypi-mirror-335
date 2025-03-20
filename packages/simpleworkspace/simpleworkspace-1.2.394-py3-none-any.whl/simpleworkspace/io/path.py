import os as _os
import string as _string
import shutil as _shutil
from typing import Callable as _Callable


class PathInfo:
    from functools import cached_property as _cached_property

    def __init__(self, path: str, normalizePath=True) -> None:
        """
        :param normalizePath: all backslashes are replaced with forward ones for compability when enabled
        """
        self._normalizePathEnabled = normalizePath
        self.Path = self._NormalizePath(path)
        """the input path, example case: a/b/test.exe -> a/b/test.exe"""

    def CreateDirectory(self):
        """
        Create all non existing directiores in specified path, ignores if directory already exists
        :raises Exception: if path exists and is not a directory
        """
        from simpleworkspace.io import directory

        if not (self.Exists):
            directory.Create(self.Path)
            return
        if not (self.IsDirectory):
            raise Exception(f'Path "{self.Absolute.Path}" already exists and is NOT a directory')
        return  # path is already directory

    def ListDirectory(self):
        """Lists direct child entries of directory"""
        from pathlib import Path

        for entry in Path(self.Path).iterdir():
            # pathlib on str will return a same design as PathInfo.Path
            yield PathInfo(str(entry), normalizePath=self._normalizePathEnabled)

    def CreateFile(self, data: bytes | str = None):
        """
        Creates or overwrites file if exists
        :raises Exception: if path exists and is not a file
        """
        from simpleworkspace.io import file

        if (not self.Exists) or (self.IsFile):
            file.Create(self.Path, data)
            return

        raise Exception(f'Path "{self.Absolute.Path}" already exists and is NOT a file')

    def ReadFile(self, type=str):
        from simpleworkspace.io import file

        if self.IsFile:
            return file.Read(self.Path, type=type)

        raise Exception(f'Path "{self.Absolute.Path}" is not a file')

    def Remove(self):
        """removes existing file or empty directory"""
        if not self.Exists:
            return
        if self.IsDirectory:
            _os.rmdir(self.Path)
        else:
            _os.remove(self.Path)

    def Rename(self, newName: str):
        currentPath = self.Absolute.Path
        newPath = (self.Absolute.Parent / newName).Path
        if currentPath == newPath:
            return
        _os.rename(currentPath, newPath)
        # invalidate cache...
        self.Path = newPath
        self._InvalidateCache()

    @property
    def IsDirectory(self) -> bool:
        return _os.path.isdir(self.Path)

    @property
    def IsFile(self) -> bool:
        return _os.path.isfile(self.Path)

    @property
    def IsSymlink(self) -> bool:
        return _os.path.islink(self.Path)

    @property
    def Exists(self) -> bool:
        return _os.path.exists(self.Path)

    def Join(self, *otherPaths: "str|PathInfo"):
        otherPaths = [str(x) if type(x) is PathInfo else x for x in otherPaths]  # convert pathinfo objects to str aswell
        return PathInfo(_os.path.join(self.Path, *otherPaths), normalizePath=self._normalizePathEnabled)

    @property
    def Stats(self):
        return _os.stat(self.Path)  # follows symlink by default

    @_cached_property
    def Absolute(self) -> "PathInfo":
        """converts the input path to an absolute path, example case: a/b/test.exe -> c:/a/b/test.exe"""
        return PathInfo(_os.path.realpath(self.Path), normalizePath=self._normalizePathEnabled)

    @property
    def Tail(self) -> str:
        """Retrieves everything before filename, example case: a/b/test.exe -> a/b"""

        tail, head = self._HeadTail
        return tail

    @property
    def Head(self) -> str:
        """Retrieves everything after last slash which would be the filename or directory, example case: a/b/test.exe -> test.exe"""

        tail, head = self._HeadTail
        return head

    @property
    def Filename(self) -> str:
        """retrieves filename, example case: a/b/test.exe -> test.exe"""

        return self.Head

    @property
    def FilenameWithoutExtension(self):
        """retrieves filename without extension, example case: a/b/test.exe -> test"""

        filename = self._FilenameSplit[0]
        return filename

    @property
    def Extension(self):
        """
        Retrieves fileextension without the dot, example case: a/b/test.exe -> exe\n
        Returns empty string if there is no extension
        """

        if len(self._FilenameSplit) == 2:
            return self._FilenameSplit[1]
        return ""

    @property
    def Parent(self):
        return PathInfo(self.Tail, normalizePath=self._normalizePathEnabled)

    def RelativeTo(self, startPath: "str|PathInfo"):
        """
        Return a relative version of a path with starting point of startPath

        Example:

        >>> PathInfo("/root/assets/img.png").RelativeTo("/root")
        PathInfo("assets/img.png")
        """
        if isinstance(startPath, type(self)):
            startPath = startPath.Path
        return PathInfo(_os.path.relpath(self.Path, startPath), normalizePath=self._normalizePathEnabled)

    @_cached_property
    def _HeadTail(self) -> tuple[str, str]:
        return _os.path.split(self.Path)

    @_cached_property
    def _FilenameSplit(self) -> str:
        return self.Head.rsplit(".", 1)

    def __str__(self):
        return self.Path

    def _NormalizePath(self, path: str):
        return path.replace("\\", "/") if self._normalizePathEnabled else path

    def __truediv__(self, otherPath: "str|PathInfo"):
        return self.Join(otherPath)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        # could also have been swapped for abspath to make different path syntax match aswell...
        return self.Path == other.Path

    def _InvalidateCache(self):
        cachedProps = ["Absolute", "_HeadTail", "_FilenameSplit"]
        for attr in cachedProps:
            if hasattr(self, attr):
                delattr(self, attr)

    def CopyTo(self, destination: "str|PathInfo", filter: _Callable[["PathInfo", "PathInfo"], bool] = None, filter_PreserveNewest=False):
        """
        Copies the source file or directory to the destination path.
        This method handles both file and directory copying. If the source is a directory,
        it will create the destination directory if it does not exist and recursively copy
        all subdirectories and files. If the source is a file, it will be copied directly
        to the destination. The filter function, if provided, allows for conditional copying
        based on custom logic.

        Params:
            - destination: The destination path where the source file or directory will be copied.
            - filter: A filter function that takes the source and destination PathInfo objects and returns a boolean indicating whether to copy the file or directory.
            - filter_PreserveNewest: skip copying file if source is not newer than destination
        """

        def _filterPreserveNewest(src:PathInfo, dst:PathInfo):
            if dst.IsFile and (dst.Stats.st_mtime >= src.Stats.st_mtime):
                return False
            return True

        if isinstance(destination, str):
            destination = PathInfo(destination).Absolute
        if not self.Exists:
            raise FileNotFoundError(f'source path "{self.Absolute.Path}" does not exist')
        if self.IsDirectory:
            if not destination.IsDirectory:
                destination.CreateDirectory()
            for root, dirs, files in _os.walk(self.Absolute.Path):
                for dir_name in dirs:
                    dir_path = _os.path.join(root, dir_name)
                    rel_path = _os.path.relpath(dir_path, self.Path)
                    dest_path = _os.path.join(destination.Path, rel_path)
                    if (filter is not None) and filter(PathInfo(dir_path), PathInfo(dest_path)) == False:
                        continue
                    if(filter_PreserveNewest is not None) and _filterPreserveNewest(PathInfo(dir_path), PathInfo(dest_path)) == False:
                        continue
                    _os.makedirs(dest_path, exist_ok=True)
                for file_name in files:
                    file_path = _os.path.join(root, file_name)
                    rel_path = _os.path.relpath(file_path, self.Path)
                    dest_path = _os.path.join(destination.Path, rel_path)
                    if (filter is not None) and filter(PathInfo(file_path), PathInfo(dest_path)) == False:
                        continue
                    if(filter_PreserveNewest is not None) and _filterPreserveNewest(PathInfo(file_path), PathInfo(dest_path)) == False:
                        continue
                    _shutil.copy2(file_path, dest_path)
        else:
            if (filter is None) or filter(self.Absolute, destination):
                _shutil.copy2(self.Path, destination.Path)


class PathResolver:
    class User:
        @classmethod
        def AppData(cls, appName=None, companyName=None, roaming=False):
            """
            Retrieves crossplatform user specific Appdata folder.
            * no arguments        -> %appdata%/
            * appName only        -> %appdata%/appname
            * appname and company -> %appdata%/companyName/appname/

            Typical user data directories are:
            * Mac OS X:              ~/Library/Application Support/<AppAuthor>/<AppName>
            * Unix:                  ~/.local/share/<AppAuthor>/<AppName>    # or in $XDG_DATA_HOME, if defined
            * Windows (not roaming): C:/Users/<username>/AppData/Local/<AppAuthor>/<AppName>
            * Windows (roaming):     C:/Users/<username>/AppData/Roaming/<AppAuthor>/<AppName>

            Params:
                - roaming: can be set True to use the Windows roaming appdata directory. \
                           That means that for users on a Windows network setup for roaming profiles, \
                           this user data will be sync'd on login.
            """
            from simpleworkspace.types.os import OperatingSystemEnum

            currentOS = OperatingSystemEnum.GetCurrentOS()
            if currentOS == OperatingSystemEnum.Windows:
                envKey = "APPDATA" if roaming else "LOCALAPPDATA"
                pathBuilder = _os.getenv(envKey)
            elif currentOS == OperatingSystemEnum.MacOS:
                pathBuilder = _os.path.expanduser("~/Library/Application Support/")
            else:
                pathBuilder = _os.getenv("XDG_DATA_HOME", _os.path.expanduser("~/.local/share"))

            if companyName is not None:
                pathBuilder = _os.path.join(pathBuilder, companyName)
            if appName is not None:
                pathBuilder = _os.path.join(pathBuilder, appName)
            return pathBuilder

        @classmethod
        def Home(cls):
            return _os.path.expanduser("~")

    class Shared:
        @classmethod
        def AppData(cls, appName=None, companyName=None, multipath=False) -> str | list[str]:
            """
            Retrieves crossplatform user-shared Appdata folder.
            * no arguments        -> %appdata%/
            * appName only        -> %appdata%/appname
            * appname and company -> %appdata%/companyName/appname/

            Typical user data directories are:
            * Mac OS X : /Library/Application Support/<AppAuthor>/<AppName>
            * Unix     : /usr/local/share/<AppAuthor>/<AppName>
            * Windows  : C:/ProgramData/<AppAuthor>/<AppName>

            :param multipath: is an optional parameter only applicable to *nix which indicates that the entire list of data dirs should be returned. \
                By default, the first item from XDG_DATA_DIRS is returned, or '/usr/local/share/<AppAuthor>/<AppName>' if XDG_DATA_DIRS is not set

            """
            from simpleworkspace.types.os import OperatingSystemEnum

            currentOS = OperatingSystemEnum.GetCurrentOS()
            if currentOS == OperatingSystemEnum.Windows:
                paths = [_os.getenv("ALLUSERSPROFILE")]
            elif currentOS == OperatingSystemEnum.MacOS:
                paths = ["/Library/Application Support"]
            else:
                paths = _os.getenv("XDG_DATA_DIRS")
                if paths is not None:
                    paths = [_os.path.expanduser(x.rstrip(_os.sep)) for x in paths.split(_os.pathsep)]
                else:
                    paths = ["/usr/local/share", "/usr/share"]

            for i in range(len(paths)):
                pathBuilder = paths[i]
                if companyName is not None:
                    pathBuilder = _os.path.join(pathBuilder, companyName)
                if appName is not None:
                    pathBuilder = _os.path.join(pathBuilder, appName)
                if not multipath:
                    return pathBuilder
                paths[i] = pathBuilder
            return paths


def FindEmptySpot(filepath: str):
    pathInfo = PathInfo(filepath)
    TmpPath = filepath
    i = 1
    while _os.path.exists(TmpPath) == True:
        TmpPath = _os.path.join(pathInfo.Tail, f"{pathInfo.FilenameWithoutExtension}_{i}.{pathInfo.Extension}")
        i += 1
    return TmpPath


def SanitizePath(path: str, allowedCharset=_string.ascii_letters + _string.digits + " .-_/\\"):
    from simpleworkspace.utility import strings

    return strings.Sanitize(path, allowedCharset=allowedCharset)
