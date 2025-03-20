from time import time
import sys
from simpleworkspace.types.time import TimeEnum, TimeSpan
import threading
from collections.abc import Iterator
from typing import Callable, Iterable, TypeVar
from collections import defaultdict, deque
from simpleworkspace.utility.concurrent.task import ITask as _ITask


class AnsiEscapeCodes:
    _escape = "\x1b"


    Erase_CurrentLine = f"{_escape}[2K"
    MoveCursor_LineStart = '\r'
    MoveCursor_Up_OneLine = f"{_escape}[1A"   #keeps the column position, 1 specifies n lines
    MoveCursor_Down_OneLine = f"{_escape}[1B" #keeps the column position, 1 specifies n lines
    MoveCursor_StartOfNextLine = '\n'

    @classmethod
    def MoveCursor_Up(cls, lines:int):
        return f"{cls._escape}[{lines}A"

    @classmethod
    def MoveCursor_Down(cls, lines:int):
        return f"{cls._escape}[{lines}B"


_T = TypeVar('_T')
class ProgressBar(Iterator[_T]):
    '''thread safe progressbar'''
    def __init__(self, iterable:Iterable[_T]=None, total=None):
        self.setting_style_bar_fill = "█"
        '''the character to fill the progressbar with'''
        self.setting_style_bar_length = 20
        '''total width in characters of the progressbar'''
        self.setting_style_format_infinity = "{incremented} {unit} [Elapsed={time_elapsed}, Speed={speed:.1f}/s]"
        '''the style used for when the progressbar does not have a known total, since alot of statistics can not be calculated in this scenario'''
        self.setting_style_format_measurable = "|{bar}| {percentage:.1f}% [Elapsed={time_elapsed}|ETA={time_remaining}|Speed={speed:.1f}/s|{unit}={incremented}/{total}]"
        '''the style used for when the progressbar has a known total'''
        self.setting_format_mapping = {'unit': 'pcs'}
        '''Maps data to the formatter'''
        self.setting_printOnIncrement = True
        '''print progressbar on every increment call'''
        self.setting_stream=sys.stdout
        self._setting_incrementHistorySize = 2
        '''calculates average speed within history window size'''
        
        self._extraProgressBars: list[ProgressBar] = []
        self._extraProgressBars_allocated = 0
        self._rootProgressBar:ProgressBar = None

        if total is None and iterable is not None:
            if hasattr(iterable, "__len__"):
                total = len(iterable)

        self.total = total
        self._iterable = iterable
        if self._iterable is not None:
            self._iterator = iter(iterable)
        self.stats_incremented = 0
        '''the total incremented amount'''
        self._stats_startTime = time()  # Track start time
        self._stats_incrementHistory: deque[tuple[float, float]] = deque([(self._stats_startTime, 0)], maxlen=self.setting_incrementHistorySize)

        self._CallbackSettings_OnIncrementSteps = None
        self._CallbackSettings_OnReachedTarget = None

        self._lock = threading.Lock()
        self._task_PrintAsync:_ITask = None

        self._Windows_EnableAnsiEscapeSequence()

    @property
    def setting_incrementHistorySize(self):
        return self._setting_incrementHistorySize
    
    @setting_incrementHistorySize.setter
    def setting_incrementHistorySize(self, newValue:int):
        if(newValue < 1):
            raise ValueError("History size cannot be less than 1, which is necessary to calculate ETA")
        self._setting_incrementHistorySize = newValue
        self._stats_incrementHistory = deque(self._stats_incrementHistory, maxlen=newValue)

    def IsFinished(self):
        if self.total is None:
            return False  # without a total, its not possible to say its finished
        if self.stats_incremented >= self.total:
            return True
        return False

    def Increment(self, increment=1):
        '''Increases the progress bar by the specified increment value'''
        
        with self._lock:
            self.stats_incremented += increment

            printOnIncrement = self.setting_printOnIncrement
            if(self._rootProgressBar is not None): #if this is an child progressbar, then root progressbar is in charge of print setting 
                printOnIncrement = self._rootProgressBar.setting_printOnIncrement
            if printOnIncrement:
                self.Print()

            if self._CallbackSettings_OnIncrementSteps:
                for setting in self._CallbackSettings_OnIncrementSteps:
                    setting["effective_increments"] += increment
                    if setting["effective_increments"] >= setting["increments"]:
                        setting["callback"]()
                        setting["effective_increments"] = 0
            
            if(self._CallbackSettings_OnReachedTarget):
                i = 0
                while i < len(self._CallbackSettings_OnReachedTarget):
                    setting = self._CallbackSettings_OnReachedTarget[i]
                    if(self.stats_incremented >= setting['increments']):
                        setting["callback"]()
                        del self._CallbackSettings_OnReachedTarget[i]
                    else: #only increment index when not removing an element
                        i += 1
        return


    def Print(self):
        '''Prints the progress bar to the console'''

        if(self._rootProgressBar is not None):
            self._rootProgressBar.Print() #incase this is part of a nested progressbar, then use the root to print
            return
        
        self.setting_stream.write(AnsiEscapeCodes.Erase_CurrentLine)  
        self.setting_stream.write(AnsiEscapeCodes.MoveCursor_LineStart)  
        self.setting_stream.write(self.ToString())

        for extraPb in self._extraProgressBars:
            self.setting_stream.write(AnsiEscapeCodes.MoveCursor_StartOfNextLine)
            self.setting_stream.write(AnsiEscapeCodes.Erase_CurrentLine)
            self.setting_stream.write("+" + extraPb.ToString())
        
        emptyExtraPbAllocations = self._extraProgressBars_allocated - len(self._extraProgressBars)
        for i in range(emptyExtraPbAllocations):
            self.setting_stream.write(AnsiEscapeCodes.MoveCursor_StartOfNextLine)
            self.setting_stream.write(AnsiEscapeCodes.Erase_CurrentLine)

        if(self._extraProgressBars_allocated > 0):
            self.setting_stream.write(AnsiEscapeCodes.MoveCursor_Up(self._extraProgressBars_allocated))
        self.setting_stream.write(AnsiEscapeCodes.MoveCursor_LineStart)
        self.setting_stream.flush()

        return
    
    def PrintAsync(self, refreshDelay=1):
        '''
        Prints the progress bar live in a new thread with the refresh delay specified in settings

        disables autoprint on increment if its on, the live progress thread will take care
        of printing it with better statistics since increments are gathered over potentially a longer duration

        :param refreshDelay: how often to refresh bar stats and visuals, delay is specified in seconds
        '''
        
        if(self._task_PrintAsync):
            return
        
        class printAsyncTask(_ITask):
            def _Action(task):
                # prints once right away, then at end of while loop after delay each time, since the delay can be aborted,
                # we want to make sure we get one last refresh
                self.Print()
                while not task.IsCancelled:
                    if self.IsFinished():
                        break
                    task._cancellationToken.wait(refreshDelay)
                    self.Print()
                self.Console_CleanUp()
                self._task_PrintAsync = None
                return
    
        self.setting_printOnIncrement = False

        self._task_PrintAsync = printAsyncTask()
        self._task_PrintAsync.Daemon = True
        self._task_PrintAsync.Start()
        return self._task_PrintAsync

    def ToString(self):
        '''gets the progressbar information as a string'''
        current_time = time()
        elapsedTime = current_time - self._stats_startTime
        elapsedTime_str = self._FormatTime(elapsedTime)

        window_startTime, window_startIncrement = self._stats_incrementHistory[0]
        previousIncrementTime, previousIncrementCount = self._stats_incrementHistory[-1]
        incrementsSinceLastPrint = self.stats_incremented - previousIncrementCount
        self._stats_incrementHistory.append((current_time, self.stats_incremented))
        totalIncrementsInTimeWindow = self.stats_incremented - window_startIncrement
        timespan = current_time - window_startTime  # Time difference between oldest and newest entries
        incrementsPerSecond = totalIncrementsInTimeWindow / timespan if timespan > 0 else 0  # Average increments per second

        formatMapping = defaultdict(str, incremented=self.stats_incremented, time_elapsed=elapsedTime_str, speed=incrementsPerSecond)
        if self.total is None:
            formatMapping.update(self.setting_format_mapping)
            return self.setting_style_format_infinity.format_map(formatMapping)

        # Calculate remaining time
        remainingTime = 0 if incrementsPerSecond == 0 else (self.total - self.stats_incremented) / incrementsPerSecond
        remainingTime_str = self._FormatTime(remainingTime)

        # progressbar style
        filled_length = 0
        if(self.total > 0):
            filled_length = min(int(self.setting_style_bar_length * self.stats_incremented / self.total), self.setting_style_bar_length)  # use min incase bar length is over 100%
        bar = self.setting_style_bar_fill * filled_length + "-" * (self.setting_style_bar_length - filled_length)
        percentage = 0 
        if(self.total > 0):
            percentage = self.stats_incremented * 100 / self.total

        formatMapping.update(bar=bar, percentage=percentage, time_remaining=remainingTime_str, total=self.total)
        formatMapping.update(self.setting_format_mapping)
        return self.setting_style_format_measurable.format_map(formatMapping)

    def Console_CleanUp(self):
        '''
        Cleans up console by flushing out progressbar and adding newline to make it prepared for regular use
        
        - is not needed when iterable supplied or printasync, since these have an definite stop point, eg end of iterable or stop of printasync thread. 
        '''
        
        if(self._extraProgressBars_allocated > 0):
            self.setting_stream.write('\n' * self._extraProgressBars_allocated)

        self.setting_stream.write('\n')
        self.setting_stream.flush()

    def AddEventListener_OnIncrementInterval(self, increments: int, callback: Callable):
        '''
        Set a callback to be executed after every x increments.
        :param increments: The number of increments after which the callback should be executed.
        :param callback: The user-specified function to be called after 'increments' number of increments
        '''
        if self._CallbackSettings_OnIncrementSteps is None:
            self._CallbackSettings_OnIncrementSteps = []
        self._CallbackSettings_OnIncrementSteps.append({"increments": increments, "callback": callback, "effective_increments": 0})
    
    def AddEventListener_OnReachedTarget(self, targetIncrements: int, callback: Callable):
        '''
        Set a callback to be executed one time after specified increments are surpassed.
        :param targetIncrements: The number of increments after which the callback should be executed.
        :param callback: The user-specified function to be called once the reached increments surpasses the specified total
        '''
        if self._CallbackSettings_OnReachedTarget is None:
            self._CallbackSettings_OnReachedTarget = []
        self._CallbackSettings_OnReachedTarget.append({"increments": targetIncrements, "callback": callback})

    def AddProgressBar(self, progressbar:'ProgressBar'):
        if(self._rootProgressBar is not None):
            raise SyntaxError("This progressbar is already attached to a parent, only 1 child depth is supported")
        self._extraProgressBars.append(progressbar)
        progressbar._rootProgressBar = self
        if(len(self._extraProgressBars) > self._extraProgressBars_allocated):
            self._extraProgressBars_allocated = len(self._extraProgressBars)

    def RemoveProgressBar(self, progressbar:'ProgressBar'):
        self._extraProgressBars.remove(progressbar)


    def _FormatTime(self, seconds: float):
        '''
        Formats the given time in seconds to the format HH:MM:SS.
        :param seconds: The time in seconds to format.
        '''
        timespan = TimeSpan(seconds=seconds)
        timeParts = timespan.Partition(minUnit=TimeEnum.Second, maxUnit=TimeEnum.Hour)
        for i in timeParts.keys():
            timeParts[i] = round(timeParts[i])  # remove all decimals
        return "{0:02d}:{1:02d}:{2:02d}".format(timeParts[TimeEnum.Hour], timeParts[TimeEnum.Minute], timeParts[TimeEnum.Second])  # 00:00:00 format

    def __len__(self):
        return self.total

    def __iter__(self):
        return self

    def __next__(self):
        '''Returns the next value from the iterator and increments the progress bar'''

        try:
            value = next(self._iterator)
            self.Increment()
            return value
        except StopIteration:
            self.Console_CleanUp()
            raise StopIteration
    
    def _Windows_EnableAnsiEscapeSequence(self):
        from simpleworkspace.types.os import OperatingSystemEnum
        if(OperatingSystemEnum.GetCurrentOS() != OperatingSystemEnum.Windows):
            return
        
        try:
            import ctypes
            # Constants for console mode
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

            # Get handle to the console
            kernel32 = ctypes.windll.kernel32
            h_stdout = kernel32.GetStdHandle(-11)
            h_stderr = kernel32.GetStdHandle(-12)
            for stream in [h_stdout, h_stderr]:
                # Get current console mode
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(stream, ctypes.byref(mode))

                # Enable virtual terminal processing in console mode
                mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(stream, mode)
        except Exception as ex:
            pass
