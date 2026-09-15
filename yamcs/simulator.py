import random
import struct
import time

from spacepacket import (
    PacketType,
    SpacePacket,
    SpacePacketProtocolEntity,
)
from spacepacket.transport import UdpTransport

# for outgoing traffic
udp_transport = UdpTransport(
    routing={
        "*": [("127.0.0.1", 1234)],
    }
)

# for incoming traffic
udp_transport.bind("0.0.0.0", 10025)

entity = SpacePacketProtocolEntity(transport=udp_transport)

tm_count = 0
tc_count = 0
tm_dummy_integer_value = 0
tm_dummy_float_value = 0


def display_received_packet(packet):
    global tc_count
    tc_count += 1
    print()
    print(f"Telecommand received with data field: 0x{packet.packet_data_field.hex()}")


entity.indication = display_received_packet


def wrap_in_tm_frame(
    space_packet: bytes,
    frame_count: int,
    scid: int = 0,
    vcid: int = 0,
    frame_len: int = 223,
) -> bytes:
    """Wraps a CCSDS SpacePacket into a CCSDS TM Transfer Frame (CCSDS 132.0-B).

    Includes standard 6-byte TM primary header and packet padding
    to fill the fixed frame length (up to 223 bytes).
    """
    mcid_vcid = ((0 & 0x03) << 14) | ((scid & 0x03FF) << 4) | ((vcid & 0x07) << 1) | 0
    mc_count = frame_count & 0xFF
    vc_count = frame_count & 0xFF
    data_field_status = (3 << 11) | 0  # Seg Len = 3 (11b), First Header Pointer = 0

    header = struct.pack(">HBBH", mcid_vcid, mc_count, vc_count, data_field_status)

    payload = bytearray(header)
    payload.extend(space_packet)

    pad_len = frame_len - len(payload)
    if pad_len > 0:
        if pad_len < 6:
            raise ValueError("Padding length too short for idle packet")
        idle_hdr = struct.pack(">HHH", 0x07FF, 0xC000, pad_len - 7)
        idle_data = b"\x55" * (pad_len - 6)
        payload.extend(idle_hdr)
        payload.extend(idle_data)

    return bytes(payload)


try:
    while True:
        # some fake telemetry
        tm_dummy_integer_value += 1
        tm_dummy_float_value = random.random() * 100

        data = bytearray(
            struct.pack(">If", tm_dummy_integer_value, tm_dummy_float_value)
        )
        packet = SpacePacket(
            packet_type=PacketType.TELEMETRY,
            apid=100,
            packet_sequence_count=tm_count,
            packet_data_field=data,
        )
        tm_frame = wrap_in_tm_frame(packet.encode(), frame_count=tm_count)
        udp_transport.request(tm_frame)
        # uncomment the next line to see the data that is being sent, example: '0064c000000700000001410f22cf'
        # print(packet.encode().hex())
        tm_count += 1
        print(f"Sent: {tm_count} TM frames. Received: {tc_count} commands.", end="\r")

        time.sleep(2)

except KeyboardInterrupt:
    print()

finally:
    udp_transport.unbind()
