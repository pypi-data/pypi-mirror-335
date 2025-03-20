class HardwareInfo:

    __cache_GetId__:str = None
    @classmethod
    def GetId(cls):
        """
        Gets an unique hardward identifier
        * windows: Gets motherboard id
        * Mac: Gets id based on multiple hardware components such as motherboard
        * Linux: Gets an unique identifier for the current installation \n
            * Note: This identifier is modifiable and changes between OS installation. \
                    A motherboard id can be retrieved with "dmidecode -s system-uuid" but requires root privileges, \
                    therefore machine-id is more suitable
        """
        from simpleworkspace.types.os import OperatingSystemEnum
        import subprocess, os

        if(cls.__cache_GetId__):
            return cls.__cache_GetId__

        platform = OperatingSystemEnum.GetCurrentOS()
        if(platform == OperatingSystemEnum.Linux):
            if os.access("/etc/machine-id", os.R_OK):
                with open("/etc/machine-id", "r") as fp:
                    id = fp.read().strip() #machine id followed by single \n
            else:
                raise LookupError("Machine does not support /etc/machine-id or is missing read accedd")
        elif(platform == OperatingSystemEnum.Windows):
            #the command outputs first line "UUID" and a couple of \r between, so we use bytes to avoid converting them to newlines
            result = subprocess.run(["wmic", "csproduct", "get", "uuid"], capture_output=True, check=True)
            #we then split on first \n and take the next line, and strip away empty spaces and \r
            id = result.stdout.decode("utf-8").split('\n')[1].strip()
        elif(platform == OperatingSystemEnum.MacOS):
            id = subprocess.run(
                ["ioreg", "-d2", "-c", "IOPlatformExpertDevice", "|", "awk", "-F", "'/IOPlatformUUID/{print $(NF-1)}'"],
                capture_output=True, check=True, text=True).stdout.strip()
        else:
            raise NotImplementedError("The current OS does not have id retrieval implemented")
        
        if (id is None) or (id == ""):
            raise LookupError("The retrieved was empty")

        cls.__cache_GetId__ = id
        return id