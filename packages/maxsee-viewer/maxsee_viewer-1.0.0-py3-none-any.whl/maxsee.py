# Reading data from MaxSee Wifi microscope
# See https://www.chzsoft.de/site/hardware/reverse-engineering-a-wifi-microscope/.

# Copyright (c) 2020, Christian Zietz <czietz@gmx.net> /
#               2025 Johannes Löhnert <loehnert.kde@gmx.de>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = ["receive_maxsee"]

import socket
import logging
from queue import Queue
from threading import Thread, Event
from contextlib import contextmanager

HOST = "192.168.29.1"  # Microscope hard-wired IP address
SPORT = 20000  # Microscope command port
RPORT = 10900  # Receive port for JPEG frames


def L():
    return logging.getLogger(__name__)


@contextmanager
def receive_maxsee():
    """MaxSee receiver context.

    Images are received in an own thread, which lives as long as the context
    manager.

    Yields a ``Queue`` instance.  Each time a frame is complete, it is put on
    the queue. Items are bytes instances.

    The queue buffers at most 5 frames, then it starts dropping the oldest frame
    on each new one.

    If another thread does heavy work (say, displaying an image :-)), it can
    happen that UDP packets are missed and JPG data would be corrupt. The
    receiver detects this and drops corrupt frames.
    """
    # Start receive loop
    receiver = Queue(5)
    stop = Event()
    # Open sockets here, to crash immediately should they be blocked.
    # Open command socket for sending
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_ctrl:
        # Open receive socket and bind to receive port
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_rcv:
            s_rcv.bind(("", RPORT))
            s_rcv.setblocking(False)
            # Send commands like naInit_Re() would do
            s_ctrl.sendto(b"JHCMD\x10\x00", (HOST, SPORT))
            s_ctrl.sendto(b"JHCMD\x20\x00", (HOST, SPORT))
            # Heartbeat command, starts the transmission of data from the scope
            s_ctrl.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))
            s_ctrl.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))
            L().debug("Sent start command")

            t = Thread(target=_recv_loop, args=(stop, receiver, s_ctrl, s_rcv), name=__name__ + "._recv_loop")
            t.start()
            try:
                yield receiver
            finally:
                stop.set()


def _recv_loop(stop: Event, receiver: Queue, s_ctrl:socket.socket, s_rcv:socket.socket):
    try:
        _recv_loop_inner(stop, receiver, s_ctrl, s_rcv)
    finally:
        # Stop data command, like in naStop()
        s_ctrl.sendto(b"JHCMD\xd0\x02", (HOST, SPORT))
        L().debug("Sent stop command")


def _recv_loop_inner(
    stop: Event, receiver: Queue, s_ctrl: socket.socket, s_rcv: socket.socket
):
    buf = b""
    packetnum_prev = 0
    corrupt_frame = False
    while not stop.is_set():
        try:
            data = s_rcv.recv(1450)
        except Exception as e:
            L().info("recv failed", exc_info=True)
            stop.wait(0.1)
            continue
        if len(data) <= 8:
            continue
        # Header
        framenum = data[0] + data[1] * 256
        packetnum = data[3]
        L().debug(f"received {len(data)} bytes. {framenum=}, {packetnum=}")
        if packetnum == 0:
            # New frame started. Yield the finished frame and reset buf.
            if corrupt_frame:
                L().info(f"Skip corrupt frame {framenum=}")
            else:
                # Drop oldest frame if full. Single producer so this is safe.
                if receiver.full():
                    receiver.get()
                receiver.put(buf)
            # Send a heartbeat every 50 frames (arbitrary number) to keep data flowing
            if framenum % 50 == 0:
                s_ctrl.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))
            buf = b""
            corrupt_frame = False
        elif packetnum != packetnum_prev + 1:
            # Lost or swapped packets. Skip frame.
            corrupt_frame = True
        buf += data[8:]
        packetnum_prev = packetnum
