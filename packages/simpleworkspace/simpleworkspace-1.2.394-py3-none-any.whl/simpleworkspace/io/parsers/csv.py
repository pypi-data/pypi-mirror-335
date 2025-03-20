import csv as _csv
from typing import Any, TypeVar as _TypeVar, Generic as _Generic, MutableSequence as _MutableSequence, IO as _IO
from io import TextIOWrapper as _TextIOWrapper, BufferedIOBase as _BufferedIOBase, StringIO as _StringIO
import locale as _locale
_T = _TypeVar('_T')

class CSVParser(_Generic[_T]):
    '''
    Simple csv reader and writer wrapper class. The class can also be used to create new csv files.

    Properties for the user:
    * self.Delimiter: The delimiter to be used when loading or exporting a csv file. It is specified in the constructor but can be freely changed.
    * self.Rows     : A 2D list of csv rows in the format Rows[row][col]. It can be manipulated to alter the exported csv file on Save().
    * self.Headers  : A list of column names that must match the column count on the rest of csv rows.
                      When headers is None or an empty list, the exported csv file will not include a header row.
    '''

    def __init__(self, delimiter:str=',', encoding:str=None):
        self.Delimiter = delimiter
        '''The delimiter character to use'''
        self.Headers:list[str] = []
        '''list of column names aka headers'''
        self.Rows = [] #initializes RowList instance
        self._encoding = _locale.getencoding() if encoding is None else encoding
        return
    

    @property
    def Rows(self) -> '_T|_RowList':
        '''contains the a 2D list of data rows, self.Rows[row][col]'''
        return self._rows

    @Rows.setter
    def Rows(self, new_value):
        if not isinstance(new_value, (list, tuple)):
            raise TypeError("RowList must be of type iterable (list/tuple)")
        self._rows = _RowList(self, new_value)

    def GetValuesByColumnName(self, columnName:str):
        '''
        Retrieves list of values under a specific column/header name. 

        :param columnName: The columnName to get values of, is case insensitive.
        :raises LookupError: If headers are not mapped or loaded, exception will be thrown
        :return: list of string values as an LINQ iterator for matched column name, otherwise None.
        '''
        from simpleworkspace.utility.collections.linq import LINQ

        if not (self.Headers):
            raise LookupError("No headers attached in csv document")
        
        columnName = columnName.lower()
        for index, headerName in enumerate(self.Headers):
            if(headerName.lower() == columnName):
                return LINQ(self.Rows).Select(lambda row: row[index])
        return None

    def ImportString(self, data:str, hasHeader=True):
        """
        Imports a csv instance from a string

        :param data: a csv string to load from
        :param hasHeader: Indicates whether the first row contains headers.
        """
        return self.ImportStream(_StringIO(data), hasHeader=hasHeader)
    
    def ImportStream(self, streamOrFilepath:str|_IO, hasHeader=True):
        """
        Imports a csv instance from a stream like object or filepath

        :param stream: a stream or filepath to load from
        :param hasHeader: Indicates whether the first row contains headers.
        """

        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'r', newline='', encoding=self._encoding)
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath, encoding=self._encoding, newline='') #convert from binary to text stream since csv only supports text
            self._ImportStream(stream, hasHeader)
        finally:
            if(fp): #if we created a new filehandle, then close it
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream

    def _ImportStream(self, stream:_IO, hasHeader:bool):
        self.Rows = []
        self.Headers = []
        reader = _csv.reader(stream, delimiter=self.Delimiter, lineterminator='\n')
        if(hasHeader):
            self.Headers = next(reader)

        self.Rows = list(reader)
    
    def ExportString(self):
        """Exports the CSV instance to a string"""
        io = _StringIO()
        self.ExportStream(io)
        return io.getvalue()

    def ExportStream(self, streamOrFilepath:str|_IO):
        """Exports the CSV instance to a specified file path or a stream"""
        # Regular export: Create a new file or overwrite existing one and write the data.

        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'w', newline='', encoding=self._encoding)
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath, encoding=self._encoding, newline='') #convert from binary to text stream since csv only supports text
            self._ExportStream(stream)
        finally:
            if(fp):
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream
        return

    def _ExportStream(self, stream:_IO):
        csv_writer = _csv.writer(stream, delimiter=self.Delimiter, lineterminator='\n')
        if(self.Headers):
            csv_writer.writerow(self.Headers)
        csv_writer.writerows(self.Rows)
        stream.flush()


class _ColumnList(_MutableSequence[str]):
        def __init__(self, context: 'CSVParser', items:list[str] = []):
            self.__context__ = context
            self.__list__ = list(items)

        def __ResolveIndex__(self, index:str|int):
            if isinstance(index, int):
                return index
            
            # If the key is a string, try to find the index by item name
            if not(self.__context__.Headers):
                raise AttributeError("No headers attached in csv document")
            try:
                return self.__context__.Headers.index(index)
            except ValueError:
                raise AttributeError(f"Invalid Column Name '{index}'")
            
        def __getitem__(self, index:int|str) -> str:
            index = self.__ResolveIndex__(index)
            return self.__list__[index]

        def __setitem__(self, index, value):
            index = self.__ResolveIndex__(index)
            self.__list__[index] = value
        
        def __delitem__(self, index):
            index = self.__ResolveIndex__(index)
            del self.__list__[index]

        def insert(self, index, value):
            index = self.__ResolveIndex__(index)
            self.__list__.insert(index, value)

        def __len__(self):
            return len(self.__list__)
        
        def __repr__(self) -> str:
            return self.__list__.__repr__()
        
        def __eq__(self, other):
            if isinstance(other, _ColumnList):
                return self.__list__ == other.__list__
            if isinstance(other, list):
                return self.__list__ == other
            return False
        

class _RowList(_MutableSequence[_ColumnList]):
    def __init__(self, context: 'CSVParser', items: list[_ColumnList] = []):
        self.__context__ = context
        self.__list__ = [self.__AsRow__(item) for item in items]

    def __AsRow__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError("RowList can only contain iterables of type list or tuple")
        return _ColumnList(self.__context__, value)

    def __getitem__(self, index) -> _ColumnList:
        return self.__list__[index]

    def __setitem__(self, index, value):
        self.__list__[index] = self.__AsRow__(value)

    def __delitem__(self, index):
        del self.__list__[index]

    def insert(self, index, value):
        self.__list__.insert(index, self.__AsRow__(value))

    def __len__(self):
        return len(self.__list__)

    def __repr__(self):
        return self.__list__.__repr__()
    
    def __eq__(self, other):
        if isinstance(other, _RowList):
            return self.__list__ == other.__list__
        if isinstance(other, list):
            return self.__list__ == other
        return False
