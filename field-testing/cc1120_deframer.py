#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CC1120 Packet Deframer Block for GNU Radio
Author: Diego
Description:
    Reads an unpacked stream of bits (0 or 1 as uint8), searches for the 32-bit CC1120 sync word,
    decodes the 8-bit payload length field, and outputs the decoded payload bytes.
"""

import numpy as np
from gnuradio import gr

class CC1120Deframer(gr.basic_block):
    """CC1120 Packet Deframer Block
    
    Parameters:
    - sync_word: 32-bit binary string (e.g., '11010110011111111110000011101' or '00011010110011111111110000011101')
    - debug: Boolean flag to enable debug print statements
    """
    def __init__(self, sync_word="11010110011111111110000011101", debug=False):
        gr.basic_block.__init__(
            self,
            name='CC1120 Deframer',
            in_sig=[np.uint8],
            out_sig=[np.uint8]
        )
        self.debug = str(debug).lower() in ("true", "1")
        self.sync_word = sync_word.zfill(32)  # Pad to 32 bits
        self.sync_len = len(self.sync_word)
        self.sync_val = int(self.sync_word, 2)
        self.sync_mask = (1 << self.sync_len) - 1

        self.state = "SYNC"  # States: SYNC, LENGTH, PAYLOAD
        self.shift_reg = 0
        self.payload_len = 0
        self.temp_payload_len = 0
        self.bit_counter = 0
        self.payload = []
        self.out_queue = []

        if self.debug:
            print(f"[DEBUG] CC1120 Deframer initialized with sync_word={sync_word}")

    def forecast(self, noutput_items, ninputs):
        return [max(1, noutput_items * 8) for _ in range(ninputs)]

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        for val in in0:
            bit = int(val) & 1

            if self.state == "SYNC":
                self.shift_reg = ((self.shift_reg << 1) | bit) & self.sync_mask
                if self.shift_reg == self.sync_val:
                    self.state = "LENGTH"
                    self.temp_payload_len = self.bit_counter = 0

            elif self.state == "LENGTH":
                self.temp_payload_len = (self.temp_payload_len << 1) | bit
                self.bit_counter += 1
                if self.bit_counter == 8:
                    self.payload_len = self.temp_payload_len
                    self.payload = []
                    if self.debug:
                        print(f"[DEBUG] Payload len decoded: {self.payload_len}")
                    if self.payload_len > 0:
                        self.state = "PAYLOAD"
                        self.temp_payload_len = self.bit_counter = 0
                    else:
                        self.state = "SYNC"
                        self.shift_reg = 0

            elif self.state == "PAYLOAD":
                self.temp_payload_len = (self.temp_payload_len << 1) | bit
                self.bit_counter += 1
                if self.bit_counter == 8:
                    self.payload.append(self.temp_payload_len)
                    self.temp_payload_len = self.bit_counter = 0

                    if len(self.payload) == self.payload_len:
                        self.out_queue.extend(self.payload)
                        if self.debug:
                            print(f"[DEBUG] Decoded complete packet: {self.payload}")
                        self.state = "SYNC"
                        self.shift_reg = 0

        out_idx = 0
        while out_idx < len(out0) and len(self.out_queue) > 0:
            out0[out_idx] = self.out_queue.pop(0)
            out_idx += 1

        self.consume(0, len(in0))
        return out_idx

# Alias for embedded Python block compatibility
blk = CC1120Deframer

if __name__ == '__main__':
    print("Testing CC1120Deframer standalone block...")
    deframer = CC1120Deframer(debug=True)
    print("Block initialized successfully.")
