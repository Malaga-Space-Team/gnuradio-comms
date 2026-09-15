import numpy as np
from gnuradio import gr
import pmt


def generate_ccsds_sequence(length=255):
    """Generates the CCSDS pseudo-random sequence using the generator polynomial
    h(x) = x^8 + x^7 + x^5 + x^3 + 1 (CCSDS 131.0-B) initialized to 0xFF.
    """
    seq = bytearray(length)
    state = 0xFF
    for i in range(length):
        byte = 0
        for _ in range(8):
            out_bit = state & 1
            feedback = ((state >> 0) ^ (state >> 3) ^ (state >> 5) ^ (state >> 7)) & 1
            state = (state >> 1) | (feedback << 7)
            byte = (byte << 1) | out_bit
        seq[i] = byte
    return np.frombuffer(seq, dtype=np.uint8)


class blk(gr.basic_block):
    """CCSDS Scrambler implementation"""

    def __init__(self):
        gr.basic_block.__init__(self, name="CCSDS Scrambler", in_sig=None, out_sig=None)
        self.d_sequence = generate_ccsds_sequence(255)

        self.message_port_register_out(pmt.intern("out"))
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.msg_handler)

    def msg_handler(self, pmt_msg):
        msg = np.array(pmt.u8vector_elements(pmt.cdr(pmt_msg)), dtype=np.uint8)

        if msg.size > self.d_sequence.size:
            self.d_sequence = generate_ccsds_sequence(msg.size)

        msg ^= self.d_sequence[: msg.size]

        self.message_port_pub(
            pmt.intern("out"),
            pmt.cons(pmt.car(pmt_msg), pmt.init_u8vector(msg.size, msg.tolist())),
        )
