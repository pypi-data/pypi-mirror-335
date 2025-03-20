import time as _time
from typing import Callable as _Callable
from simpleworkspace.types.time import TimeSpan as _TimeSpan

class StopWatch:
    def __init__(self) -> None:
        self.timeHistory = []
        self.__timeElapsed = 0
        self.__isRunning = False
        self._GetCurrentTime = _time.perf_counter

    def Start(self):
        if(self.__isRunning):
            return
        self.__isRunning = True
        self.timeHistory.append({
            "timestamp": self._GetCurrentTime(),
            "isStartEvent": True
        })
        self.__UpdateTimeElapsed()
        return
    
    def Stop(self):
        if not(self.__isRunning):
            return
        self.__isRunning = False
        self.timeHistory.append({
            "timestamp": self._GetCurrentTime(),
            "isStartEvent": False
        })
        return
    
    def Reset(self):
        '''Stops and resets the timer'''
        self.__init__()
        return

    def __UpdateTimeElapsed(self):
        endTime = self._GetCurrentTime() #take end time directly to avoid spending time while calculating
        self.__timeElapsed = 0
        startTime = None
        for timeEvent in self.timeHistory:
            if(timeEvent["isStartEvent"]):
                startTime = timeEvent["timestamp"]
                continue
            self.__timeElapsed += timeEvent["timestamp"] - startTime
            startTime = None
        if(startTime is not None):
            self.__timeElapsed += endTime - startTime
    
    @property
    def Elapsed(self):
        '''Returns the elapsed timespan'''
        self.__UpdateTimeElapsed()
        return _TimeSpan(seconds=self.__timeElapsed)

    @property
    def ElapsedSeconds(self):
        '''Returns the elapsed time in seconds'''
        return self.Elapsed.TotalSeconds

    @property
    def ElapsedMilliSeconds(self):
        '''Returns the elapsed time in milliseconds'''
        return self.Elapsed.TotalMilliSeconds
        
    def __enter__(self):
        self.Start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Stop()
        return
    
class Timer:
    ''' A live timer running on separate thread to perform events at each tick interval or after certain period has passed'''
    def __init__(self, tickInterval = _TimeSpan(seconds=1)) -> None:
        """
        :param tickInterval: Specifies how often the timer ticks, and therefore also how responsive it is
        """
        from simpleworkspace.utility.concurrent.task import ITask

        if(type(tickInterval) is not _TimeSpan):
            raise TypeError("tick interval must be of type TimeSpan")

        self.tickInterval = tickInterval
        self.Elapsed = _TimeSpan()
        '''Gets elapsed time since timer has been running'''
        self._stopwatch = StopWatch()
        self._eventListeners_OnTick = []
        self._eventListeners_OnElapsed = []
        self._eventListeners_OnInterval = []
        self._tickingTask:ITask = None
                  
    def AddEventListener_OnTick(self, callback: _Callable):
        '''Calls a callback at each tick of the timer'''
        self._eventListeners_OnTick.append(callback)
    
    def AddEventListener_OnElapsed(self, elapsed:_TimeSpan, callback: _Callable):
        '''Calls a callback once after a certain period of time has elapsed'''
        self._eventListeners_OnElapsed.append({
            "targetElapsed": elapsed.TotalSeconds,
            "callback": callback
        })

    def AddEventListener_OnInterval(self, interval: _TimeSpan, callback: _Callable):
        '''Calls a callback every time the specified interval passes'''
        self._eventListeners_OnInterval.append({
            "interval": interval.TotalSeconds,
            "callback": callback,
            "effective_elapsed": 0
        })

    @property
    def IsRunning(self):
        return self._tickingTask and self._tickingTask.IsRunning
    
    def Stop(self):
        '''Sends cancellation request to timer thread without blocking'''
        if(not self._tickingTask.IsRunning):
            return
        self._tickingTask.Cancel()

    def Start(self):
        '''Starts the timer and its live thread'''
        from simpleworkspace.utility.concurrent.task import ITask

        if self._tickingTask and self._tickingTask.IsRunning:
            return
        
        class TickingTask(ITask):
            def _Action(task):
                self._stopwatch.Start()
                while not task._cancellationToken.is_set():
                    self._Tick(self._stopwatch.Elapsed)
                    task._cancellationToken.wait(self.tickInterval.TotalSeconds)
                self._stopwatch.Stop()
                task._cancellationToken.clear()
            
        self._tickingTask = TickingTask()
        self._tickingTask.Daemon = True #allows python to exit
        self._tickingTask.Start()

    def _Tick(self, newElapsedTime:_TimeSpan):
        prevElapsed = self.Elapsed
        self.Elapsed = newElapsedTime
        tickDuration = self.Elapsed - prevElapsed

        for listener in self._eventListeners_OnTick:
            listener()

        i = 0
        while i < len(self._eventListeners_OnElapsed):
            listener = self._eventListeners_OnElapsed[i]
            if(self.Elapsed.TotalSeconds >= listener["targetElapsed"]):
                listener["callback"]()
                del self._eventListeners_OnElapsed[i]
            else: #only increment index when not removing an element
                i += 1

        for listener in self._eventListeners_OnInterval:
            listener['effective_elapsed'] += tickDuration.TotalSeconds
            if(listener['effective_elapsed'] >= listener['interval']):
                listener["callback"]()
            listener['effective_elapsed'] = 0