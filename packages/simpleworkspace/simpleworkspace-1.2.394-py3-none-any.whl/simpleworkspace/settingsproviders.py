from abc import ABC as _ABC, abstractmethod as _abstractmethod
import os as _os
import json as _json
from typing import Generic as _Generic, TypeVar as _TypeVar, Any as _Any, Type as _Type, IO as _IO
from io import TextIOBase as _TextIOBase, BufferedIOBase as _BufferedIOBase, TextIOWrapper as _TextIOWrapper

_T = _TypeVar("_T")

class SettingsTemplate():
    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self): #iters keys
        return iter(self.__dict__)
    
    def __len__(self): #count key value pairs
        return len(self.__dict__)


class _SettingsManager(_ABC, _Generic[_T]):
    '''
    Abstract Settingsmanager that supports dynamic and strongly typed settings
        * Uses dynamic settings management by default when no templates are provided
        * For strongly typed settings with defaultable settings, supply a derived SettingsTemplate as the generic Type and constructor arg

    Example Usage, Dynamic settings:
    >>> manager = SettingsManager_JSON('./tmp.json')
        manager.LoadSettings()
        if("key1" in manager.Settings):
            val1 = manager.Settings["key1"]
        manager.Settings["key1"] = 10
        manager.SaveSettings()

    Example Usage, Typed settings:
    >>> class MyTemplate(SettingsTemplate):
            def __init__(self):
                self.val1:str = "hej" #both typehint and default value
                self.val2:str = None
        #template provides intellisense and default values
        manager = SettingsManager_JSON('./tmp.json', MyTemplate)
        manager.LoadSettings()
        if(manager.Settings.val1 is not None):
            val1 = manager.Settings.val1
        manager.Settings.val1 = 10
        manager.SaveSettings()
    '''
    def __init__(self, streamOrFilepath:str|_IO, settingsTemplate: _Type[_T] = SettingsTemplate):
        self.dataSource = streamOrFilepath
        '''Underlying datasource for this setting manager, can be a filepath string or a stream object'''
        if(not isinstance(settingsTemplate, type)):
            raise TypeError(f"SettingsTemplate needs to be a class type, got {type(settingsTemplate)}")
        
        self._settings: _T = settingsTemplate()

    @property
    def Settings(self):
        return self._settings
    
    @Settings.setter
    def Settings(self, value:object|dict):
        if(isinstance(value, dict)): #dict has no __dict__ property therefore special scenario
            self.Settings.__dict__ = value
        else:
            self.Settings.__dict__ = value.__dict__

    @_abstractmethod
    def _ParseSettingsStream(self, streamOrFilepath:str|_IO) -> dict[str, _Any]:
        '''responsible for parsing setting file and returning a settings object'''

    @_abstractmethod
    def _ExportSettingsStream(self, settingsObject: dict[str, _Any], streamOrFilepath: str|_IO):
        '''responsible for saving the settingsObject to file location in self._settingsPath'''
  
    def ClearSettings(self):
        self.Settings = type(self.Settings)()

    def LoadSettings(self):
        '''Loads the setting file from specified location to the memory at self.settings'''
        self.ClearSettings()
        #filepath not existing, nothing to load
        if isinstance(self.dataSource, str) and not _os.path.exists(self.dataSource):
            return

        settingsObject = self._ParseSettingsStream(self.dataSource)
        #instead of replacing all the settings, we set it to default state, and copy over keys
        #incase default settings are specified/overriden, even if only one of the default setting existed in the file
        #we will keep other default settings as specified and only change value of new settings parsed
        self.Settings.__dict__.update(settingsObject)
        return

    def SaveSettings(self):
        self._ExportSettingsStream(self.Settings.__dict__, self.dataSource)


class SettingsManager_JSON(_SettingsManager[_T]):
    def _ParseSettingsStream(self, streamOrFilepath: str | _IO) -> dict:
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'r')
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath) #convert from binary to text stream since csv only supports text
            return self._ParseDefinitiveStream(stream)
        finally:
            if(fp):
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream
       
    def _ParseDefinitiveStream(self, stream:_TextIOBase) -> dict:
        stream.seek(0)
        settings = _json.load(stream)
        stream.seek(0)
        return settings

    def _ExportSettingsStream(self, settingsObject: dict, streamOrFilepath: str | _IO):
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'w', newline='')
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath, newline='') #convert from binary to text stream since csv only supports text
            self._ExportDefinitiveStream(settingsObject, stream)
        finally:
            if(fp):
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream
        return

    def _ExportDefinitiveStream(self, settingsObject:dict, stream:_TextIOBase):
        stream.truncate(0)
        stream.seek(0)
        _json.dump(settingsObject, stream)
        stream.flush()
        stream.seek(0)

class SettingsManager_BasicConfig(_SettingsManager[_T|dict[str,str]]):
    '''
    Basic Config files are the simplest form of KeyValuePair config files.
    * each line consists of "key=value" pair.
    * comments can be placed anywhere with '#' both at start of a line or inline after a setting
    * whitespaces are trimmed from start and end of both key and the value. "key=value" is same as " key = value "
    * This parser is intentionally not compatible with INI format (will throw an exception only if a section is detected).
        The reason behind this is that basic config files don't use sections and therefore rely that every setting key is 
        unique. An INI file on the other hand can have same setting key under different sections.
    '''

    _fileLineOrderCounter = 0
    _fileLineOrdering = [] #tracks positions of lines to be able to preserve comments
    
    def _ParseSettingsStream(self, streamOrFilepath: str | _IO) -> dict:
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'r')
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath) #convert from binary to text stream since csv only supports text
            return self._ParseDefinitiveStream(stream)
        finally:
            if(fp):
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream
       
    def _ParseDefinitiveStream(self, stream:_TextIOBase) -> dict:
        stream.seek(0)
        self._ResetFileLineOrder()
        conf = {}
        for lineNo, line in enumerate(stream, start=1):
            line = line.strip()

            if line == '': #only a blank line
                self._AddFileLineOrder(None, None)
                continue
            elif line.startswith('#'): #only a comment line
                self._AddFileLineOrder(line, "comment")
                continue

            keyValueAndComment = line.split('#', 1)
            hasInlineComment = True if len(keyValueAndComment) == 2 else False
            if(hasInlineComment):
                line = keyValueAndComment[0]
            keyValue = line.split('=', 1)
            if(len(keyValue) != 2):
                raise ValueError(f"file contains bad line format [LineNo:{lineNo}]: key/value pair is not separated with '='")

            key = keyValue[0].strip()
            val = keyValue[1].strip()
            conf[key] = val
            if(hasInlineComment): #it had an inline comment
                self._AddFileLineOrder([key, keyValueAndComment[1]], "key,comment")
            else:    #regular key value pair
                self._AddFileLineOrder(key, "key")
        stream.seek(0)
        return conf

    def _ExportSettingsStream(self, settingsObject: dict, streamOrFilepath: str | _IO):
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'w', newline='')
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath, newline='') #convert from binary to text stream since csv only supports text
            self._ExportDefinitiveStream(settingsObject, stream)
        finally:
            if(fp):
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream
        return

    def _ExportDefinitiveStream(self, settingsObject:dict, stream:_TextIOBase):
        stream.truncate(0)
        stream.seek(0)
        allKeys = set(settingsObject.keys())
        for orderLine in self._fileLineOrdering:
            order, data, type = orderLine
            if(type is None):
                stream.write("\n")
            elif(type == "comment"):
                stream.write(data + "\n")
            elif(type == "key") and (data in allKeys): #write out previously existing key
                stream.write(f"{data}={settingsObject[data]}\n")
                allKeys.remove(data)
            elif(type == "key,comment") and (data[0] in allKeys):
                key, comment = data[0], data[1] 
                stream.write(f"{key}={settingsObject[key]} #{comment}\n")
                allKeys.remove(key)
        for newKey in allKeys:
            stream.write(f"{newKey}={settingsObject[newKey]}\n")
        stream.flush()
        stream.seek(0)


    def _AddFileLineOrder(self, data, type):
        self._fileLineOrdering.append((self._fileLineOrderCounter, data, type)) #indexes: 0 = order, 1 = data, 2 = type of data
        self._fileLineOrderCounter += 1
    
    def _ResetFileLineOrder(self):
        self._fileLineOrdering = []
        self._fileLineOrderCounter = 0

