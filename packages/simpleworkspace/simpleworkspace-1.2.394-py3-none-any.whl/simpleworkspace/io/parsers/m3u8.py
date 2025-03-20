import re as _re
from typing import IO as _IO
from io import TextIOWrapper as _TextIOWrapper, BufferedIOBase as _BufferedIOBase, TextIOBase as _TextIOBase, StringIO as _StringIO
import locale as _locale

class _NoneQuotedValue(str):... #basically a string, but this instance of string does not get quoted on export

class M3U8Parser: 
    class Entry:
        def __init__(self, 
                    Tag:str='',
                    Attributes:dict[str, str] = None,
                    PositionalAttributes:list[str]=None, 
                    URI:str = '', 
                    Comment:str = ''):
            self.Tag = Tag
            self.Attributes:dict[str, str] = {} if Attributes is None else Attributes
            '''KeyValue pair attributes for an entry'''
            self.PositionalAttributes:list[str] = [] if PositionalAttributes is None else PositionalAttributes
            '''for special entries where positional attributes are used'''
            self.URI = URI
            self.Comment = Comment

        def ToString(self):
            strBuilder = f'{self.Tag}'

            if(self.Tag):
                if(self.Tag == '#EXT-X-STREAM-INF'): #specification states mandatory int attribute bandwidth, therefore reasonable to avoid qouting
                    self.Attributes['BANDWIDTH'] = _NoneQuotedValue(self.Attributes['BANDWIDTH'])
                    if("RESOLUTION" in self.Attributes): #not mandatory, but specs wants it without quotes eg "<width>x<height>"
                        self.Attributes['RESOLUTION'] = _NoneQuotedValue(self.Attributes['RESOLUTION'])

                attributeList = [*self.PositionalAttributes]
                for key,value in self.Attributes.items():
                    if(isinstance(value, str)) and (type(value) is not _NoneQuotedValue):
                        value = f'"{value}"'
                    attributeList.append(f'{key}={value}')

                if(attributeList):
                    strBuilder += ':' + ','.join(attributeList)
            
            if(self.URI):
                separation = '\n' if strBuilder else '' #if URI was bundled together with entry, put URI in one line below
                strBuilder += separation + self.URI

            if(self.Comment):# used to preserve comments and empty lines
                separation = '\n' if strBuilder else '' #if comment was bundled together with entry, put comment in one line above
                strBuilder = self.Comment + separation + strBuilder
            return strBuilder
    
    _attributePattern = _re.compile(r'\s*(.+?)\s*=\s*((?:".*?")|.*?)\s*(?:,|$)')
    def __init__(self) -> None:
        self.Entries:list[M3U8Parser.Entry] = [] #some lines might not be entries such as empty lines or comments

    @property
    def IsMaster(self):
        for entry in self.Entries:
            if(entry.Tag == '#EXT-X-STREAM-INF'):
                return True
        return False

    def ImportStream(self, streamOrFilepath:str|_IO):
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'r')
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath) #convert from binary to text stream
            self._ImportStream(stream)
        finally:
            if(fp): #if we created a new filehandle, then close it
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream

    def ImportString(self, data:str):
        return self.ImportStream(_StringIO(data))

    def _ImportStream(self, stream:_TextIOBase):
        self.Entries = []

        entry = None
        for line in stream:
            line = line.strip()
            if(entry is not None) and (line == '' or line.startswith('#')):
                #empty line or comment or another entry, marks the finish of previous entry
                self.Entries.append(entry)
                entry = None

            if(line.startswith('#EXT')):
                tagAndAttributes = line.split(':', maxsplit=1)
                entry = M3U8Parser.Entry(tagAndAttributes[0])
                if(entry.Tag == '#EXTINF'):                     #format "#EXTINF:<DURATION>, [Optional]<TITLE>"
                    extinf_attribs = tagAndAttributes[1].split(',', maxsplit=1)
                    entry.PositionalAttributes.append(extinf_attribs[0].strip())
                    if(len(extinf_attribs) > 1):
                        entry.PositionalAttributes.append(extinf_attribs[1].strip())
                elif(entry.Tag == '#EXT-X-VERSION'):            #format "#EXT-X-VERSION:<VERSION>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-PLAYLIST-TYPE'):      #format "#EXT-X-PLAYLIST-TYPE:<TYPE>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-TARGETDURATION'):     #format "#EXT-X-TARGETDURATION:<DURATION>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-MEDIA-SEQUENCE'):     #format "#EXT-X-MEDIA-SEQUENCE:<SEQUENCE_NUMBER>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-START'):              #format "#EXT-X-START:<TIME_OFFSET>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-ALLOW-CACHE'):        #format "#EXT-X-ALLOW-CACHE:<yes|no>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(entry.Tag == '#EXT-X-PROGRAM-DATE-TIME'):  #format "#EXT-X-PROGRAM-DATE-TIME:<DATE_TIME>"
                    entry.PositionalAttributes.append(tagAndAttributes[1].strip())
                elif(len(tagAndAttributes) > 1):
                    for pair in self._attributePattern.findall(tagAndAttributes[1]):
                        key, value = pair
                        entry.Attributes[key] = value.strip('"')
            elif(line == '') or (line.startswith('#')):  #since line starts with # but not #EXT, then it must be comment line
                self.Entries.append(M3U8Parser.Entry(Comment=line)) #preserve empty newlines and comments on final export
            else:
                entry.URI = line
        if(entry is not None):
            self.Entries.append(entry)

    def ExportString(self):
        io = _StringIO()
        self.ExportStream(io)
        return io.getvalue()
    
    def ExportStream(self, streamOrFilepath:str|_IO):
        fp = None
        streamWrapper = None
        stream = streamOrFilepath
        try:
            if(isinstance(streamOrFilepath, str)):
                stream = fp = open(streamOrFilepath, 'w', newline='') #ensure newlines are written as is without translations
            elif(isinstance(streamOrFilepath, _BufferedIOBase)):
                stream = streamWrapper = _TextIOWrapper(streamOrFilepath, newline='') #convert from binary to text stream
            self._ExportStream(stream)
        finally:
            if(fp): #if we created a new filehandle, then close it
                fp.close()
            if(streamWrapper):
                streamWrapper.detach() #when textiowrapper goes out of scope and is GC collected, it will otherwise close the underlying stream

    def _ExportStream(self, stream: _TextIOBase):
        stream.write(self.ToString())
        stream.flush()

    def GetTags_EXTINF(self):
        """Get entries with tag #EXTINF which points to media URI files"""
        for entry in self.Entries:
            if(entry.Tag == '#EXTINF'):
                yield entry

    def GetTags_EXT_X_STREAM_INF(self):
        """Only master playlist will have these tags, gets #EXT-X-STREAM-INF tags which points to the actual media playlist"""
        for entry in self.Entries:
            if(entry.Tag == '#EXT-X-STREAM-INF'):
                yield entry
    
    def ToString(self):
        return '\n'.join([entry.ToString() for entry in self.Entries])
