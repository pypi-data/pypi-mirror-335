#  Copyright Femtosense 2025
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

"""
Evk2Plugin : IOPlugin, helps SPURunner talk to the EVK2 board

"""
from threading import Thread

try:
    import hid  # https://pypi.org/project/hid/ https://trezor.github.io/cython-hidapi/api.html
except ImportError as e:
    print(
        "Could not import hid. Did you install libhidapi-hidraw0 and libhidapi-libusb0 on Linux or\n"
        "on mac brew install libusb hidapi and then export DYLD_LIBRARY_PATH=/opt/homebrew/lib \n{e}"
    )
from queue import Queue
from typing_extensions import Self
import numpy as np

try:
    from femtobehav import cfg
except ImportError:
    from femtodriver import cfg  # fall back to 1.2 config (eval systems)

from femtodriver.plugins.io_plugin import *

from femtodriver.typing_help import *
from typing import *

# import correct address map for this version
if cfg.ISA == 1.3:
    import femtodriver.addr_map_spu1p3 as am
elif cfg.ISA == 2.0:
    import femtodriver.addr_map_spu2p0 as am
else:
    raise NotImplementedError(f"unrecognized ISA version {cfg.ISA}")

import logging

logger = logging.getLogger(__name__)

EVK2_VID = 0x16C0
EVK2_PID = 0x0486
EVK2_INTERFACE = 0
QUEUE_SIZE = 50
USB_PACKET_LEN = 64
USB_DATA_LEN = 14

COMMANDS = {
    "ack": 0,
    "reset": 1,
    "interrupt": 2,
    "apb_write": 3,
    "apb_read": 4,
    "axis_write": 5,
    "axis_write_end": 6,
    "axis_read_start": 7,
    "axis_read": 8,
    "register_write": 9,
    "register_read": 10,
    "error": 11,
    None: None,
}
CODE_TO_COMMANDS = {v: k for k, v in COMMANDS.items()}

# TODO: fix this redundancy
MSG_CODES = {
    "apb_read": "apb_read",
    "apb_write": "apb_write",
    "axis_read": "axis_read",
    "axis_write": "axis_write",
    "spu_top_read": "register_read",
    "spu_top_write": "register_write",  # not implemented
    "host_write": "reset",  # not implemented
    None: None,
}


class UsbPacket:
    """
    Class describing an exchange of SpuVectors sequence with SPU

    Attributes:
        command (int): command id of the packet (see COMMANDS)
        address (int): address in SPU-001 memory of the data stored in the packet
        data (list(int)): data stored int packet
        length (int): number of values stored in the packet's data field
    """

    def __init__(
        self, command: int, address: int, data: list[int] = [], length: int = 0
    ) -> None:
        """
        Initializes a new UsbPacket object

        Args:
            command (int): command id of the packet (see COMMANDS)
            address (int): address in SPU-001 memory of the data stored in the packet
            data (list(int)): data stored int packet
            length (int): number of values stored in the packet's data field
        Returns:
            None
        """

        self.command: int = command
        self.address: int = address
        self.length: int = min(max(len(data), length), USB_DATA_LEN)
        self.data: list[int] = data

    def serialize(self) -> bytes:
        """
        Serializes the UsbPacket

        Args:
            None
        Returns:
            bytearray: object serialized into bytes
        """

        byte_buffer: bytearray = bytearray()

        byte_buffer.extend(
            int.to_bytes(self.command, 1, byteorder="little", signed=False)
        )
        byte_buffer.append(0)  # 1 byte padding
        byte_buffer.extend(
            int.to_bytes(self.length, 2, byteorder="little", signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.address, 4, byteorder="little", signed=False)
        )
        for d in self.data:
            byte_buffer.extend(
                int.to_bytes(int(d), 4, byteorder="little", signed=False)
            )
        while len(byte_buffer) < USB_PACKET_LEN:
            byte_buffer.append(0)

        return bytes(byte_buffer)

    @classmethod
    def deserialize(cls, byte_buffer) -> Self:
        """
        Deserializes a byte array into a UsbPacket object

        Args:
            byte_buffer (bytearray): byte array containing the UsbPacket serialized data
        Return:
            UsbPacket: deserialized object
        """

        command = int(byte_buffer[0])
        # byte_buffer[1] is padding
        length = int.from_bytes(byte_buffer[2:4], byteorder="little", signed=False)
        address = int.from_bytes(byte_buffer[4:8], byteorder="little", signed=False)
        data = np.frombuffer(
            byte_buffer[8 : 8 + length * 4],
            dtype=np.dtype(np.uint32).newbyteorder("<"),
        ).tolist()
        return cls(command=command, address=address, data=data)


class Evk2Plugin(IOPlugin):
    """
    Evk2Plugin is used by HWRunner to send data to and from the board
    provides:
        setup()
        teardown()
        hw_send()
        hw_recv()

    Attributes:
        device (hid.Device): USB HID connection to EVK2
        alive (bool): flag indicating whether the object is running
        receiver_thread (threding.Thread): thread to read from EVK2 in the background
        rx_queue (Queue): queue to store all incoming packets from EVK2
    """

    def __init__(
        self,
        fake_connection=False,
        fake_hw_recv_vals: ARRAYINT = None,
        logfiledir: str = "io_records",
        host: str | None = None,
    ):
        """
        Initializes the Evk2Plugin object

        Args:
            fake _connection (bool): unused
            fake_hw_recv_vals (ARRAYINT): unused
            logfiledir (str): unused
            host (str): unused
        Returns:
            None
        Raises:
            Exception: if EVK2 could not connect
        """

        self.device: hid.Device = None
        self.alive: bool = None
        self.receiver_thread: Thread = Thread(target=self._reader, name="evk2_rx")
        self.rx_queue: Queue = Queue(QUEUE_SIZE)
        if self.setup():
            super().__init__(logfiledir=logfiledir)
        else:
            raise Exception("No EVK2")

    def __del__(self):
        self.teardown()

    @classmethod
    def _find_device(self, serial_number: int = None) -> Any:
        for dev in hid.enumerate():
            if (
                serial_number is not None
                and dev["serial_number"] == serial_number
                and dev["interface_number"] == EVK2_INTERFACE
            ):
                return dev["path"]
            elif (
                dev["vendor_id"] == EVK2_VID
                and dev["product_id"] == EVK2_PID
                and dev["interface_number"] == EVK2_INTERFACE
            ):
                return dev["path"]
        return None

    def setup(self) -> bool:
        """
        Initiates the EVK2 connection

        Args:
            None
        Returns:
            None
        Raises:
            Exception: if the EVK2 was not detected or could not connect
        """
        device_path = self._find_device()
        if device_path is None:
            logger.error("Error: couldn't find any EVK2 ")
            return False

        try:
            self.device = hid.Device(path=device_path)
        except Exception as e:
            logger.error(f"Error: couldn't connect to EVK2 ({e})")
            return False

        self.alive = True

        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        logger.info(
            f"EVK2 (serial: {self.device.serial} path: {str(device_path)}) connected and ready!"
        )
        return True

    def teardown(self):
        """
        Cleans up the Evk2Plugin object

        Args:
            None
        Returns:
            None
        """
        if self.alive:
            self.alive = False
            self.receiver_thread.join()
            self.device.close()
            logger.info("Closed EVK2")

    def reset(self):
        """
        Sends a request to EVK2 to reset SPU-001

        Args:
            None
        Returns:
            None
        """

        self.hw_send("host", 0, 1, 1, np.zeros((1,), dtype=np.uint32))

    def _reader(self) -> None:
        """
        Routine for the reader thread: reads incoming packets from EVK2 and stores them in a queue

        Args:
            None
        Returns:
            None
        """

        while self.alive:
            rx_buffer = self.device.read(USB_PACKET_LEN, 200)
            if rx_buffer:
                self.rx_queue.put(UsbPacket.deserialize(rx_buffer))

    def _read(self, blocking: bool = True, timeout_s: int = None) -> tuple[str, list]:
        """
        Reads a packet received from EVK2

        Args:
                blocking (bool): flag to make the function blocking and wait until a packet arrives from EVK2
                timeout (int): maximum duration in second before the function retunrs
        Returns:
            tuple[str, list]: packet data as a tuple (command, data)
        """

        try:
            packet = self.rx_queue.get(block=blocking, timeout=timeout_s)
            self.rx_queue.task_done()
            return (packet.command, packet.data)
        except Exception:
            logger.error("Timeout waiting for message from EVK2")
            return (COMMANDS["error"], [])

    def _write(
        self, command: int, address: int, data: list[int] = [], length: int = 0
    ) -> bool:
        """
        Writes a packet to EVK2 and waits for acknowledgment from EVK2

        Args:
            command (int): command id of the packet (see COMMANDS)
            address (int): address in SPU-001 memory of the data stored in the packet
            data (list(int)): data stored int packet
            length (int): number of values stored in the packet's data field
        Returns:
            None
        """
        self.device.write(
            UsbPacket(
                command=command, address=address, data=data, length=length
            ).serialize()
        )
        response_command, _ = self._read(timeout_s=0.2)
        return CODE_TO_COMMANDS[response_command] == "ack"

    @classmethod
    def _breakdown_into_packets(
        cls, command: str, address: int, length: int, data: list[int] = None
    ) -> list[(str, int, int, list[int])]:
        """
        Breaks down a Femtodriver transaction into USB size packets

        Args:
            command (str): command string description (from COMMANDS)
            address (int): start address of the transaction
            length (int): length of the transaction
            data (list[int]): data of the transaction
        Returns:
            list[(str, int, int, list[int])]: list of packets as tuples (command, address, length, data)
        """

        packets = []
        transaction_len = length

        if command == "axis_read":
            # USB_DATA_LEN-2 to keep space for the output parameters
            # (core_id and mailbox_id) in the first packet
            transaction_len += 2
            first_packet_len = min(USB_DATA_LEN - 2, transaction_len)
            packets.append(tuple((command + "_start", address, first_packet_len, None)))
            transaction_len -= first_packet_len
            address += first_packet_len * 4

        while transaction_len > 0:
            packet_len = min(USB_DATA_LEN, transaction_len)
            cmd_suffix = (
                "_end"
                if command == "axis_write" and transaction_len <= USB_DATA_LEN
                else ""
            )
            packets.append(
                tuple(
                    (
                        f"{command}{cmd_suffix}",
                        address,
                        packet_len,
                        data[:packet_len] if data is not None else None,
                    )
                )
            )
            address += packet_len * 4
            data = data[packet_len:] if data is not None else None
            transaction_len -= packet_len

        return packets

    def _hw_send(
        self,
        msgtype: IOTARGET,
        start_addr: int,
        end_addr: int,
        length: int,
        vals: ARRAYU32,
        flush: bool = True,
        comment: Optional[str] = None,
    ) -> None:
        """
        Writes to EVK2

        Args:
            msgtype (IOTARGET): transaction description (from MSG_CODES)
            start_addr (int): start address of the write transaction
            end_addr (int): end address of the write transaction
            length (int): length of the write transaction
            vals (ARRAYU32): data to write
            flush (bool): unused
            comment (str): unused
        Returns:
            None
        """

        if msgtype + "_write" not in MSG_CODES:
            logger.error("weird message type:", msgtype)
            return

        """send raw 32b data to the hardware"""
        packets = self._breakdown_into_packets(
            command=MSG_CODES[msgtype + "_write"],
            address=start_addr,
            length=length,
            data=vals,
        )

        for cmd, addr, len, data in packets:
            logger.debug(f"{cmd}: @{hex(addr)} [{len}] {[hex(d) for d in data]}")
            if not self._write(
                command=COMMANDS[cmd],
                address=addr,
                length=len,
                data=data,
            ):
                raise IOError("EVK2 write failed")

    def _hw_recv(
        self,
        msgtype: IOTARGET,
        start_addr: int,
        end_addr: int,
        length: int,
        comment: Optional[str] = None,
    ) -> list[ARRAYU32]:
        """
        Reads from EVK2

        Args:
            msgtype (IOTARGET): transaction description (from MSG_CODES)
            start_addr (int): start address of the transaction
            end_addr (int): end address of the transaction
            length (int): length of the transaction
            comment (str): unused
        Returns:
            list[ARRAYU32]: list of arrays containing the data read from EVK2
        """

        data = []
        if msgtype + "_read" not in MSG_CODES:
            logger.error("weird message type:", msgtype)
            return [np.array(data).astype(np.uint32)]

        packets = self._breakdown_into_packets(
            command=MSG_CODES[msgtype + "_read"],
            address=start_addr,
            length=length,
            data=None,
        )

        for cmd, addr, len, _ in packets:
            if not self._write(command=COMMANDS[cmd], address=addr, length=len):
                raise IOError("EVK2 read request failed")
            response_command, response_data = self._read()
            if CODE_TO_COMMANDS[response_command] == cmd:
                data.extend(response_data)
                logger.debug(
                    f"{cmd}: @{hex(addr)} [{len}] {[hex(d) for d in response_data]}"
                )
            else:
                raise IOError(
                    f"received wrong response: {CODE_TO_COMMANDS[response_command]} (expected {cmd})"
                )

        return [np.array(data).astype(np.uint32)]
