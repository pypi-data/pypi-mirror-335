from simpleworkspace import assets
from simpleworkspace.types.time import TimeSpan as _TimeSpan

def File(audio_file_path):
    """Plays a blocking sound file"""
    import subprocess
    subprocess.call(["ffplay", "-nodisp", "-autoexit", "-hide_banner", "-loglevel", "quiet", audio_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def Notification_Completed():
    File(assets.Audio_Notification_Completed)

def Notification_Error():
    File(assets.Audio_Notification_Error)

def Alarm_Sirens(duration:_TimeSpan=None):
    from simpleworkspace.utility.time import StopWatch

    stopwatch = StopWatch()
    stopwatch.Start()
    while True:
        File(assets.Audio_Alarms_Siren)
        if(duration is not None) and (stopwatch.Elapsed > duration):
            break
