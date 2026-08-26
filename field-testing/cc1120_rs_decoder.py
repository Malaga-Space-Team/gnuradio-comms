#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CC1120 Robust Stream Reed-Solomon Decoder Block for GNU Radio
Author: Diego
Description:
    Reads an unpacked stream of bits (0 or 1 as uint8), performs sync word detection
    with Hamming distance error tolerance, extracts packet length, and decodes
    the Reed-Solomon RS(N,K) codeword using the reedsolo library.
"""

import numpy as np
from gnuradio import gr
import reedsolo

class CC1120RSDecoder(gr.basic_block):
    """CC1120 Robust Stream Reed-Solomon Decoder Block
    
    Parameters:
    - sync_word: 32-bit binary string (e.g., '00011010110011111111110000011101')
    - threshold: Maximum bit error tolerance in sync word detection (default: 2)
    - ecc_bytes: Number of Reed-Solomon parity bytes (default: 4 for RSCodec(4))
    """
    def __init__(self, sync_word='00011010110011111111110000011101', threshold=2, ecc_bytes=4):
        gr.basic_block.__init__(
            self,
            name='CC1120 RS Stream Decoder',
            in_sig=[np.uint8],
            out_sig=[np.uint8]
        )
        self.sync_bits = np.array([int(b) for b in sync_word], dtype=np.uint8)
        self.sync_len = len(self.sync_bits)
        self.threshold = int(threshold)
        self.ecc_bytes = int(ecc_bytes)
        self.max_packet_len = 128
        self.rsc = reedsolo.RSCodec(self.ecc_bytes)
        self.state = 'SEARCH_SYNC'
        self.buffer = []
        self.len_bits = []
        self.payload_bits = []
        self.bits_needed = 0

    def forecast(self, noutput_items, ninputs):
        return [max(1, noutput_items * 8) for _ in range(ninputs)]

    def general_work(self, input_items, output_items):
        in_bits = input_items[0]
        out = output_items[0]
        in_idx = 0
        out_idx = 0
        
        while in_idx < len(in_bits):
            if self.state == 'READ_PAYLOAD' and out_idx + self.max_packet_len > len(out):
                break

            bit = in_bits[in_idx]
            in_idx += 1
            
            if self.state == 'SEARCH_SYNC':
                self.buffer.append(bit)
                if len(self.buffer) > self.sync_len:
                    self.buffer.pop(0)
                if len(self.buffer) == self.sync_len:
                    diffs = np.sum(np.array(self.buffer, dtype=np.uint8) != self.sync_bits)
                    if diffs <= self.threshold:
                        self.state = 'READ_LEN'
                        self.len_bits = []
                        
            elif self.state == 'READ_LEN':
                self.len_bits.append(bit)
                if len(self.len_bits) == 8:
                    pkt_len = int(np.packbits(self.len_bits)[0])
                    if 5 <= pkt_len <= self.max_packet_len:
                        self.bits_needed = pkt_len * 8
                        self.payload_bits = []
                        self.state = 'READ_PAYLOAD'
                    else:
                        self.state = 'SEARCH_SYNC'
                        self.buffer = []
                    
            elif self.state == 'READ_PAYLOAD':
                self.payload_bits.append(bit)
                if len(self.payload_bits) == self.bits_needed:
                    rs_codeword = bytes(np.packbits(self.payload_bits))
                    try:
                        decoded_payload, _, _ = self.rsc.decode(rs_codeword)
                    except Exception:
                        decoded_payload = rs_codeword[:max(0, len(rs_codeword) - self.ecc_bytes)]
                    
                    dec_arr = np.frombuffer(decoded_payload, dtype=np.uint8)
                    available_space = len(out) - out_idx
                    if len(dec_arr) <= available_space:
                        out[out_idx : out_idx + len(dec_arr)] = dec_arr
                        out_idx += len(dec_arr)
                    self.state = 'SEARCH_SYNC'
                    self.buffer = []
                    
        self.consume(0, in_idx)
        return out_idx

# Alias for embedded Python block compatibility
blk = CC1120RSDecoder

if __name__ == '__main__':
    print("Testing CC1120RSDecoder standalone block...")
    decoder = CC1120RSDecoder()
    print("Block initialized successfully.")
