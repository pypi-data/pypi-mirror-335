# Copyright 2024 Roman Arzumanyan.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http: // www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import python_vali as vali
from queue import Empty
from multiprocessing import Queue
import numpy as np
import logging
from multiprocessing.synchronize import Event as SyncEvent
from argparse import Namespace

import nvtx

LOGGER = logging.getLogger(__file__)


class QueueAdapter:
    def __init__(self, inp_queue: Queue,):
        """
        Constructor

        Args:
            inp_queue (Queue): queue with video chunks
        """

        self.all_done = False
        self.inp_queue = inp_queue

    def read(self, size: int) -> bytes:
        """
        Simple adapter which meets the vali.PyDecoder readable object interface.
        It takes chunks from queue and gives them to decoder.
        Empty bytearray put into queue serves as 'all done' flag.

        Args:
            size (int): requested read size

        Returns:
            bytes: compressed video bytes
        """

        while not self.all_done:
            try:
                chunk = self.inp_queue.get(timeout=0.1)

                if chunk is None:
                    self.all_done = True
                    return bytearray()

                return chunk

            except Empty:
                continue

            except ValueError:
                break

            except Exception as e:
                LOGGER.error(f"Unexpected excepton: {str(e)}")

        return bytearray()


class Decoder:
    """
    Decoder class which takes video track chunks from queue.
    Returns reconstructed video frames as VALI Surfaces.
    It owns the decoded Surface, clone it if needed.
    """

    def __init__(self,
                 inp_queue: Queue,
                 flags: Namespace,):
        """
        Constructor

        Args:
            inp_queue (Queue): queue with video chunks. If it's closed,
                this function may never return.
            flags (Namespace): parsed CLI args
        """

        self.adapter = QueueAdapter(inp_queue)

        # First try to create HW-accelerated decoder.
        # Some codecs / formats may not be supported, fall back to SW decoder then.
        try:
            self.py_dec = vali.PyDecoder(self.adapter, {}, flags.gpu_id)
        except Exception as e:
            # No exception handling here.
            # Failure to create SW decoder is fatal.
            self.py_dec = vali.PyDecoder(self.adapter, {}, gpu_id=-1)

        if not self.py_dec.IsAccelerated:
            # SW decoder outputs to numpy array.
            # Have to initialize uploader to keep decoded frames always in vRAM.
            self.uploader = vali.PyFrameUploader(gpu_id=0)

            self.dec_frame = np.ndarray(shape=(self.py_dec.HostFrameSize),
                                        dtype=np.uint8)

        # If decoder runs on CPU, allocate Surface on GPU #0
        # Otherwise use the actual GPU ID.
        self.surf = vali.Surface.Make(
            self.py_dec.Format,
            self.py_dec.Width,
            self.py_dec.Height,
            max(flags.gpu_id, 0))

    def cuda_stream(self) -> int:
        """
        Get CUDA stream used by decoder

        Returns:
            int: raw CUDA stream handle
        """
        return self.py_dec.Stream

    def width(self) -> int:
        """
        Get video width.

        Returns:
            int: width in pixels
        """
        return self.py_dec.Width

    def height(self) -> int:
        """
        Get video height.

        Returns:
            int: height in pixels
        """
        return self.py_dec.Height

    def format(self) -> vali.PixelFormat:
        """
        Get video pixel format.

        Returns:
            vali.PixelFormat: pixel format
        """
        return self.py_dec.Format

    def framerate(self) -> float:
        """
        Get video frame rate

        Returns:
            float: FPS
        """
        return self.py_dec.Framerate

    @nvtx.annotate()
    def decode(self, dry_run=False) -> vali.Surface:
        """
        Decode single video frame. When decoding is done, will return None.

        Args:
            dry_run (bool, optional): if True, CPU decoder won't upload Surface. Defaults to False.

        Returns:
            vali.Surface: Surface with reconstructed pixels.
        """
        try:
            pkt_data = vali.PacketData()
            if self.py_dec.IsAccelerated:
                success, info, _ = self.py_dec.DecodeSingleSurfaceAsync(
                    surf=self.surf, record_event=False, pkt_data=pkt_data)

                if info == vali.TaskExecInfo.END_OF_STREAM:
                    return None

                if not success:
                    LOGGER.error(f"Failed to decode surface: {info}")
                    return None
            else:
                success, info = self.py_dec.DecodeSingleFrame(
                    self.dec_frame, pkt_data)

                if info == vali.TaskExecInfo.END_OF_STREAM:
                    return None

                if not success:
                    LOGGER.error(f"Failed to decode frame: {info}")
                    return None

                if not dry_run:
                    success, info = self.uploader.Run(
                        self.dec_frame, self.surf)
                    if not success:
                        LOGGER.error(f"Failed to upload frame: {info}")
                        return None

            return self.surf

        except Exception as e:
            LOGGER.error(f"Unexpected exception: {str(e)}")
            return None
