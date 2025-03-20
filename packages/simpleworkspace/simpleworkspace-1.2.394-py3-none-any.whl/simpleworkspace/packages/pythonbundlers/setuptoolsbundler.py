import sys as _sys
import os as _os
import simpleworkspace.loader as _sw
from simpleworkspace.utility.time import StopWatch as _StopWatch
from simpleworkspace.io.parsers import toml as _toml
from simpleworkspace.utility.module import RequireModules
import io as _io
import sys as _sys
from simpleworkspace.utility import strings as _strings
from simpleworkspace.utility.cli.console import LevelPrint

class _indentedStdout(_io.TextIOWrapper):
    def __init__(self, indentLevel:int):
        self._indentLevel = indentLevel
        super().__init__(_sys.stdout.buffer, encoding=_sys.stdout.encoding, line_buffering=_sys.stdout.line_buffering)

    def write(self, message):
        super().write(_strings.IndentText(message, self._indentLevel, '   ').rstrip(' '))
    
    def close(self) -> None:
        self.detach() #avoid closing the original stdout, only the wrapper should be closed
        super().close()

class SetupToolsBundler:
    def __init__(self):
        from simpleworkspace.utility.module import ModuleInfo

        mainModule = ModuleInfo.Factory_MainModule()
        self.entryPath = mainModule.pathInfo.Parent.Absolute.Path
        self.pyproject = _toml.load(f"{self.entryPath}/pyproject.toml")
        self.packageName = self.pyproject['project']['name']
        _sys.path.insert(0, f"{self.entryPath}/src") #ensure imports to the package is done through the dev version
        self._stopwatch = _StopWatch()
        self._Register_CLI()

    def _Register_CLI(self):
        from simpleworkspace.utility.cli.parser import CLIParser, Arguments
        class CLITemplate(CLIParser):
            Build = Arguments.Argument('--build')
        self.cli = CLITemplate.Parse(ignoreUnkownArguments=True, add_help=False)

    def Command(self, args:list[str], title=None):
        import subprocess
        if(title is None):
            title = f'{args}'
        LevelPrint(0, f"> Executing command {title}...", flush=True)
        with _StopWatch() as sw1:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout: #keep in mind that stderr also writes to same stream
                LevelPrint(1, line, end='', flush=True)
            process.wait()
            if(process.returncode != 0): #something went bad
                raise RuntimeError(f"command failed...")
        LevelPrint(0, f' - Command finished in {round(sw1.ElapsedSeconds,2)} seconds...', flush=True)

    def Pipe_Init(self):
        self._stopwatch.Start()
        initMessage = f'> Bundling {self.packageName}'
        if(self.cli.Build):
            initMessage += ', Build=' + self.cli.Build
        LevelPrint(0, initMessage, flush=True)

    def Pipe_CleanUp(self):
        if not (_os.path.isfile(f'{self.entryPath}/pyproject.toml')):
            raise LookupError("Could not find a pyproject.toml file in entry directory, aborting cleanup as safety precaution")
        LevelPrint(0, "> Performing CleanUp...", flush=True)
        for pathToRemove in [
            f'{self.entryPath}/dist/',
            f'{self.entryPath}/build/',
            f'{self.entryPath}/src/{self.packageName}.egg-info/'
        ]:
            if(_os.path.isdir(pathToRemove)):
                _sw.io.directory.RemoveTree(pathToRemove)
                LevelPrint(1, f'- Removed {pathToRemove}', flush=True)
        return


    def Pipe_RunTests(self, testPath='tests/'):
        import unittest 
        LevelPrint(0, "> Running unittests...", flush=True)
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(_os.path.join(self.entryPath, testPath))
        test_runner = unittest.TextTestRunner(stream=_indentedStdout(indentLevel=1), verbosity=2)
        result = test_runner.run(test_suite)
        if not(result.wasSuccessful()): #something went bad
            raise Exception("Unittests failed!")

    def Pipe_IncrementPackageVersion(self):
        def BumpMinorVersion(versionString):
            versionInfo = versionString.split(".")
            versionInfo[2] = str(int(versionInfo[2]) + 1)
            newVersion = ".".join(versionInfo)
            return newVersion
        
        ### increment module version ###
        currentVersion = self.pyproject["project"]["version"]
        newVersion = BumpMinorVersion(currentVersion)
        self.pyproject["project"]["version"] = newVersion
        _sw.io.file.Create(f"{self.entryPath}/pyproject.toml", _toml.dumps(self.pyproject))
        LevelPrint(1, f"> Incremented package version from {currentVersion} -> {newVersion}...", flush=True)

    def Pipe_Install(self, developmentMode=False):
        ### install on computer as editable/dev mode ###
        if(developmentMode):
            self.Command([_sys.executable, "-m", "pip", "install", "--editable", self.entryPath])
        else:
            self.Command([_sys.executable, "-m", "pip", "install", self.entryPath])

    def Pipe_Publish(self, username:str, token:str):
        def Pipe_BuildDistribution():
            ### build distribution ###
            RequireModules('build')
            self.Command([_sys.executable, '-m', 'build', self.entryPath])
        
        Pipe_BuildDistribution()
        ### upload to pypi ###
        RequireModules('twine')
        self.Command(
            [_sys.executable, "-m",
                "twine", "upload",
                "-u", username, 
                "-p", token,
                f"{self.entryPath}/dist/*"
            ], 
            title='Upload To PyPi')

    def Pipe_Finish(self):
        LevelPrint(0, f"> Installer finished! Elapsed: {round(self._stopwatch.ElapsedSeconds,1)} seconds", flush=True)


