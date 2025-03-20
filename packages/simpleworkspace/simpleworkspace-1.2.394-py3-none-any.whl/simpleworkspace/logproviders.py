import logging as _logging
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import sys as _sys
import os as _os
import time as _time

### Only non standard flow of these loggers are that instead of setting extra param as individual class properties, we collect them under record.extra instead ###

class LogUtility:
    @staticmethod
    def AddContextToLogger(logger: _logging.Logger, **kwargs):
        def filter(record: _logging.LogRecord):
            if not(hasattr(record, 'extra')):
                record.extra = {}
            record.extra.update(kwargs)
            return record
        logger.addFilter(filter)
    

    @staticmethod
    def RegisterUnhandledExceptionHandler(logger: _logging.Logger):
        def UncaughtExeceptionHandler(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt): #avoid registering console aborts such as ctrl+c etc
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            _logging.shutdown()
            _sys.__excepthook__(exc_type, exc_value, exc_traceback)

        _sys.excepthook = UncaughtExeceptionHandler

class FormatOptions:
    def __init__(self,
                 includeTime:bool=None, includeLevel:bool=None, includeModuleInfo:bool=None,
                 includeProcessID:bool=None, includeThreadID:bool=None, json_prettyPrint:bool=False):
        self.includeTime = includeTime
        self.includeLevel = includeLevel
        self.includeModuleInfo = includeModuleInfo
        self.includeProcessID = includeProcessID
        self.includeThreadID = includeThreadID
        self.json_prettyPrint = json_prettyPrint

    
    def InheritDefaultOptions(self, options:'FormatOptions'):
        if(self.includeTime is None):
            self.includeTime = options.includeTime
        if(self.includeLevel is None):
            self.includeLevel = options.includeLevel
        if(self.includeModuleInfo is None):
            self.includeModuleInfo = options.includeModuleInfo
        if(self.includeProcessID is None):
            self.includeProcessID = options.includeProcessID
        if(self.includeThreadID is None):
            self.includeThreadID = options.includeThreadID

    def __hash__(self):
        return hash((self.includeTime, self.includeLevel, self.includeModuleInfo, self.includeProcessID, self.includeThreadID, self.json_prettyPrint))

class _Formatters:
    class Plain(_logging.Formatter):
        def __init__(self, formatOptions:FormatOptions, useUTCTime=False, *args, **kwargs):
            '''Styling: "{Time} {Level} [PID={ProcessID},TID={ThreadID},TRC={moduleName}:{lineNo}]: <Message>"'''

            self.formatOptions = formatOptions
            super().__init__(fmt=self._ResolveFormatString(formatOptions), datefmt="%Y-%m-%dT%H:%M:%S.%f%z", *args, **kwargs)
            if (_time.timezone == 0) or (useUTCTime):
                self._timezoneStr = 'Z'
                self.converter = _time.gmtime
            else:
                self._timezoneStr = _time.strftime('%z') #uses '+HHMM'


        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                # support %z and %f in datefmt (struct_time doesn't carry ms or tz)
                datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
                datefmt = datefmt.replace('%z', self._timezoneStr)
                s = _time.strftime(datefmt, ct)
            else:
                s = _time.strftime(self.default_time_format, ct)
                if self.default_msec_format:
                    s = self.default_msec_format % (s, record.msecs)
            return s

        def formatMessage(self, record: _logging.LogRecord) -> str:
            msg = super().formatMessage(record)
            if(record.extra):
                import json
                try:
                    contextStr = json.dumps(
                        record.extra,
                        default=_Formatters.JSON._json_serializable,
                        indent='\t' if self.formatOptions.json_prettyPrint else None,
                    )    
                # "ValueError: Circular reference detected" is raised when there is a reference to object inside the object itself.
                except (TypeError, ValueError, OverflowError) as ex:
                    contextStr = f'{{"_jsonWriteError":"{ex}"}}'
                msg += " " + contextStr
            return msg

        def _ResolveFormatString(self, formatOptions:FormatOptions):
            fmt = []
            if(formatOptions.includeTime):
                fmt.append('%(asctime)s')
            if(formatOptions.includeLevel):
                fmt.append('%(levelname)s')
            
            subFmt = []
            if(formatOptions.includeProcessID):
                subFmt.append('PID=%(process)d')
            if(formatOptions.includeThreadID):
                subFmt.append('TID=%(thread)d')
            if(formatOptions.includeModuleInfo):
                subFmt.append('TRC=%(module)s:%(lineno)s')
            if(len(subFmt) > 0):
                subfmt = ','.join(subFmt)
                fmt.append(f'[{subfmt}]')
            
            fmt = ' '.join(fmt) 
            if(fmt):
                fmt += ": "
            fmt += "%(message)s"
            return fmt

    class JSON(_logging.Formatter):
        def __init__(self, formatOptions:FormatOptions, useUTCTime=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.formatOptions = formatOptions
            
            if (_time.timezone == 0) or (useUTCTime):
                self._timezoneStr = 'Z'
                self.converter = _time.gmtime #needed when forcing utc on a non utc system
            else:
                self._timezoneStr = _time.strftime('%z') #uses '+HHMM'

        def _json_serializable(obj):
            try:
                return obj.__dict__
            except AttributeError:
                return str(obj)
    
        def formatTime(self, record, datefmt="%Y-%m-%dT%H:%M:%S.%f%z"):
            #normally this supports changing datefmt, but we hardcode the iso8601 instead

            ct = self.converter(record.created)
            datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
            datefmt = datefmt.replace('%z', self._timezoneStr)
            s = _time.strftime(datefmt, ct)
            return s
        
        def format(self, record: _logging.LogRecord) -> str:
            import json

            msg = {
                **({'timestamp': self.formatTime(record)} if self.formatOptions.includeTime else {}),
                **({'level': record.levelname} if self.formatOptions.includeLevel else {}),
                'message': record.getMessage(),
                **({'module': {'name': record.module, 'lineNo': record.lineno}} if self.formatOptions.includeModuleInfo else {}),
                **({'executionContext': {
                    **({'threadId': record.thread} if self.formatOptions.includeThreadID else {}),
                    **({'processId': record.process} if self.formatOptions.includeProcessID else {}),
                }} if (self.formatOptions.includeProcessID or self.formatOptions.includeThreadID) else {}),
                **({'context': record.extra} if record.extra else {}),
            }

            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                msg['Exception'] = self.formatException(record.exc_info)
                if record.stack_info:
                    msg["Exception"] += '\n' + self.formatStack(record.stack_info)


            try:
                return json.dumps(
                    msg,
                    default=self._json_serializable,
                    indent='\t' if self.formatOptions.json_prettyPrint else None,
                )    
            # "ValueError: Circular reference detected" is raised when there is a reference to object inside the object itself.
            except (TypeError, ValueError, OverflowError) as ex:
                return f'{{"_jsonWriteError":"{ex}"}}'

class _BaseLogger(_logging.Logger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create specialized LogRecords.
        """
        rv = _logging._logRecordFactory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        rv.extra = extra if extra else {}
        return rv

_baselogger = _BaseLogger("__SW_BASELOGGER__")
_LogManager = _logging.Manager(_baselogger)
_LogManager.setLoggerClass(_BaseLogger)
    
class FileLogger:
    _logNamePrefix = "__FILELOGGER_"
    _GetLogger_DefaultFormatOptions = FormatOptions(
        includeTime=True, includeLevel=True, includeModuleInfo=True,
        includeProcessID=True, includeThreadID=False)
    @classmethod
    def GetLogger(cls, 
                  filepath, minimumLogLevel=_logging.DEBUG, 
                  useUTCTime=True, registerGlobalUnhandledExceptions=False,
                  formatOptions=_GetLogger_DefaultFormatOptions):
        formatOptions.InheritDefaultOptions(cls._GetLogger_DefaultFormatOptions)

        logger = _LogManager.getLogger(f"{cls._logNamePrefix}{hash((filepath,minimumLogLevel,useUTCTime,formatOptions))}")
        if(registerGlobalUnhandledExceptions):
            LogUtility.RegisterUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        cls._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        logger.addHandler(cls.CreateHandler(
            filepath=filepath, useUTCTime=useUTCTime, 
            formatOptions=formatOptions))
        return logger
    
    @classmethod
    def CreateHandler(cls, filepath:str, useUTCTime=False, formatOptions=_GetLogger_DefaultFormatOptions):
        formatOptions.InheritDefaultOptions(cls._GetLogger_DefaultFormatOptions)

        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_Formatters.Plain(formatOptions=formatOptions, useUTCTime=useUTCTime))
        return handler
    
    @staticmethod
    def _CreateParentFolders(filepath:str):
        filepath = _os.path.realpath(filepath)
        directoryPath = _os.path.dirname(filepath)
        if(directoryPath in ("", "/")):
            return
        _os.makedirs(directoryPath, exist_ok=True)

class FileLogger_JSON(FileLogger):
    _logNamePrefix = "__JSONFILELOGGER_"
    @classmethod
    def CreateHandler(cls, filepath:str, useUTCTime=False, formatOptions=FileLogger._GetLogger_DefaultFormatOptions):
        formatOptions.InheritDefaultOptions(cls._GetLogger_DefaultFormatOptions)
        
        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_Formatters.JSON(formatOptions=formatOptions, useUTCTime=useUTCTime))
        return handler
    
class RotatingFileLogger:
    _logNamePrefix = "__ROTATINGFILELOGGER_"
    
    @classmethod
    def GetLogger(cls, 
                  filepath, minimumLogLevel=_logging.DEBUG, 
                  maxBytes=_ByteEnum.MegaByte.value * 30, maxRotations=10, 
                  useUTCTime=True, registerGlobalUnhandledExceptions=False,
                  formatOptions=FileLogger._GetLogger_DefaultFormatOptions):
        formatOptions.InheritDefaultOptions(FileLogger._GetLogger_DefaultFormatOptions)

        logger = _LogManager.getLogger(f"{cls._logNamePrefix}{hash((filepath,minimumLogLevel,maxBytes,maxRotations,useUTCTime,formatOptions))}")
        if(registerGlobalUnhandledExceptions):
            LogUtility.RegisterUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        

        FileLogger._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        logger.addHandler(cls.CreateHandler(
            filepath=filepath, useUTCTime=useUTCTime,
            maxBytes=maxBytes, maxRotations=maxRotations,
            formatOptions=formatOptions))
    

        return logger

    @classmethod
    def _rotator(cls, source, dest):
        import gzip 
        with open(source, "rb") as sf:
            gzip_fp = gzip.open(dest, "wb")
            gzip_fp.writelines(sf)
            gzip_fp.close()
        _os.remove(source)

    @classmethod
    def CreateHandler(cls, 
                    filepath:str, useUTCTime=True,
                    maxBytes=_ByteEnum.MegaByte.value * 100, maxRotations=10, 
                    formatOptions=FileLogger._GetLogger_DefaultFormatOptions):
            from logging.handlers import RotatingFileHandler

            formatOptions.InheritDefaultOptions(FileLogger._GetLogger_DefaultFormatOptions)
            handler = RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations, encoding='utf-8')
            handler.rotator = cls._rotator
            handler.namer = lambda name: name + ".gz"
            handler.setFormatter(_Formatters.Plain(formatOptions=formatOptions, useUTCTime=useUTCTime))
            return handler

class RotatingFileLogger_JSON(RotatingFileLogger):
    _logNamePrefix = "__ROTATINGJSONFILELOGGER_"

    @classmethod
    def CreateHandler(cls, 
                    filepath:str, useUTCTime=True,
                    maxBytes=_ByteEnum.MegaByte.value * 100, maxRotations=10, 
                    formatOptions=FileLogger._GetLogger_DefaultFormatOptions):
            from logging.handlers import RotatingFileHandler

            formatOptions.InheritDefaultOptions(FileLogger._GetLogger_DefaultFormatOptions)
            handler = RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations, encoding='utf-8')
            handler.rotator = cls._rotator
            handler.namer = lambda name: name + ".gz"
            handler.setFormatter(_Formatters.JSON(formatOptions=formatOptions, useUTCTime=useUTCTime))
            return handler



class StreamLogger:
    _GetLogger_DefaultFormatOptions = FormatOptions(
        includeTime=True, includeLevel=True, includeModuleInfo=False,
        includeProcessID=False, includeThreadID=False)
    
    @classmethod
    def GetLogger(cls, 
                  minimumLogLevel=_logging.DEBUG, useUTCTime=False, 
                  registerGlobalUnhandledExceptions=False,  stream=_sys.stdout,
                  formatOptions=_GetLogger_DefaultFormatOptions):
        formatOptions.InheritDefaultOptions(cls._GetLogger_DefaultFormatOptions)
        stdoutLogger = _LogManager.getLogger(f"__STDOUTLOGGER__{hash((minimumLogLevel,useUTCTime,formatOptions,stream))}")
        if(registerGlobalUnhandledExceptions):
            LogUtility.RegisterUnhandledExceptionHandler(stdoutLogger)
        if(stdoutLogger.hasHandlers()):
            return stdoutLogger
        stdoutLogger.setLevel(minimumLogLevel)
        stdoutLogger.addHandler(cls.CreateHandler(stream=stream, useUTCTime=useUTCTime, formatOptions=formatOptions))
        return stdoutLogger
    
    @staticmethod
    def CreateHandler(stream=_sys.stdout, useUTCTime=False, formatOptions=_GetLogger_DefaultFormatOptions):
        """
        A handler that can be supplied into a logger
        >>> logger.addHandler(StreamLogger.CreateHandler())
        """
        handler = _logging.StreamHandler(stream)
        handler.setFormatter(_Formatters.Plain(formatOptions=formatOptions, useUTCTime=useUTCTime))
        return handler

class DummyLogger:
    @classmethod
    def GetLogger(cls):
        dummyLogger = _LogManager.getLogger("@@BLACKHOLE@@")
        if(dummyLogger.hasHandlers()):
            return dummyLogger
        dummyLogger.addHandler(_logging.NullHandler())
        dummyLogger.propagate = False
        return dummyLogger
