from abc import ABC, abstractmethod
from typing import Callable
from supsisim.shv.client import ShvClient
from supsisim.shv.SHVInstance import SHVInstance
import asyncio
import subprocess
import shlex

class ImageUpdateMethod(ABC):
    def __init__(self, name: str, path_to_img: str):
        self.name: str = name
        self.path_to_img = path_to_img

    @abstractmethod
    async def upload(self, queue: asyncio.Queue) -> None:
        """
        Perform the upload.
        Each time an event happens (a succesful step or failure)
        it is reported using the supplied callback.
        """
        pass

    @abstractmethod
    async def stop_upload(self) -> None:
        """
        Stop the upload.
        """
        pass

class OpenocdUpdateMethod(ImageUpdateMethod):
    def __init__(self, params: str, path_to_img: str):
        super().__init__("openocd", path_to_img)
        self.params = params

    async def s1(self, params) -> [bool, str, str]:
        completed = subprocess.run(params, capture_output=True, text=True, timeout=20)
        if completed.returncode == 0:
            return [True, completed.stdout, completed.stderr]
        return [False, completed.stdout, completed.stderr]

    async def upload(self, queue: asyncio.Queue) -> None:
        """
        Flash using openocd.
        """
        if "@PYSIM_IMG@" not in self.params:
            queue.put_nowait("No @PYSIM_IMG@ in params found.")
            queue.put_nowait(False)
            return
        self.params = self.params.replace("@PYSIM_IMG@", self.path_to_img)

        params = ["openocd"] + shlex.split(self.params)
        ret = await self.s1(params)
        if not ret[0]:
            queue.put_nowait("Launching openocd failed. Output:")
            if ret[1] != "":
                queue.put_nowait("STDOUT:\n" + ret[1])
            if ret[2] != "":
                queue.put_nowait("STDERR:\n" + ret[2])
            queue.put_nowait(False)
            return

        queue.put_nowait("Flashed succesfully. Output:")
        queue.put_nowait(ret[1])
        queue.put_nowait(True)

    async def stop_upload(self) -> None:
        print("STOP")

class SHVUpdateMethod(ImageUpdateMethod):
    def __init__(self, path_to_img: str, shvclient: ShvClient, shvparams):
        super().__init__("SHV Update", path_to_img)
        self.shvclient = shvclient
        self.shvparams = shvparams

    async def upload(self, queue: asyncio.Queue) -> None:
        try:
            self.shvclient.update_parameters_and_connect(
                self.shvparams.ip,
                self.shvparams.port,
                self.shvparams.user,
                self.shvparams.passw,
                self.shvparams.devid,
                self.shvparams.mount
            )
        except:
            queue.put_nowait("Error connecting to the SHV broker!")
            queue.put_nowait(False)
            return

        queue.put_nowait("Connected to the SHV broker!")

        self.shvclient.disconnect()
        queue.put_nowait(True)
        
    async def stop_upload(self) -> None:
        pass

