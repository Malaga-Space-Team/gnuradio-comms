#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RTLSDR CCSDS Transmission Yamcs
# Author: diego
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import digital, filter, analog, network; from gnuradio.filter import firdes; from gnuradio.fft import window; import math, pmt
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import network
from gnuradio import soapy
import sip
import threading



class rtlsdr_rx_ccsds_yamcs(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "RTLSDR CCSDS Transmission Yamcs", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("RTLSDR CCSDS Transmission Yamcs")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rtlsdr_rx_ccsds_yamcs")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2_160_000
        self.deviation = deviation = 4000
        self.decim = decim = 15
        self.bitrate = bitrate = 1200
        self.rx_samp_rate = rx_samp_rate = samp_rate / decim
        self.channel_transition = channel_transition = 12_000
        self.channel_cutoff = channel_cutoff = deviation + bitrate / 2 + 3_000
        self.yamcs_port = yamcs_port = "10015"
        self.yamcs_host = yamcs_host = "127.0.0.1"
        self.sps = sps = int(samp_rate / bitrate)
        self.rx_sps = rx_sps = rx_samp_rate / bitrate
        self.rx_offset = rx_offset = 0
        self.rx_gain = rx_gain = 20
        self.rf_freq = rf_freq = 436_000_000
        self.lpf = lpf = firdes.low_pass(1.0, samp_rate, channel_cutoff, channel_transition, window.WIN_HAMMING, 6.76)
        self.gain = gain = rx_samp_rate / (2.0 * math.pi * deviation)
        self.freq_offset = freq_offset = 0
        self.afc_alpha = afc_alpha = 1 - math.exp(-2 * math.pi * 10 / rx_samp_rate)
        self.access_key = access_key = '11100001010110101110100010010011'

        ##################################################
        # Blocks
        ##################################################

        self._rx_gain_range = qtgui.Range(-12, 64, 1, 20, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "RX Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_gain_win)
        self._freq_offset_range = qtgui.Range(-20000, 20000, 100, 0, 200)
        self._freq_offset_win = qtgui.RangeWidget(self._freq_offset_range, self.set_freq_offset, "frequency correction", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_offset_win)
        self.soapy_rtlsdr_source_0 = None
        dev = 'driver=rtlsdr'
        stream_args = 'bufflen=16384'
        tune_args = ['']
        settings = ['']

        def _set_soapy_rtlsdr_source_0_gain_mode(channel, agc):
            self.soapy_rtlsdr_source_0.set_gain_mode(channel, agc)
            if not agc:
                  self.soapy_rtlsdr_source_0.set_gain(channel, self._soapy_rtlsdr_source_0_gain_value)
        self.set_soapy_rtlsdr_source_0_gain_mode = _set_soapy_rtlsdr_source_0_gain_mode

        def _set_soapy_rtlsdr_source_0_gain(channel, name, gain):
            self._soapy_rtlsdr_source_0_gain_value = gain
            if not self.soapy_rtlsdr_source_0.get_gain_mode(channel):
                self.soapy_rtlsdr_source_0.set_gain(channel, gain)
        self.set_soapy_rtlsdr_source_0_gain = _set_soapy_rtlsdr_source_0_gain

        def _set_soapy_rtlsdr_source_0_bias(bias):
            if 'biastee' in self._soapy_rtlsdr_source_0_setting_keys:
                self.soapy_rtlsdr_source_0.write_setting('biastee', bias)
        self.set_soapy_rtlsdr_source_0_bias = _set_soapy_rtlsdr_source_0_bias

        self.soapy_rtlsdr_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)

        self._soapy_rtlsdr_source_0_setting_keys = [a.key for a in self.soapy_rtlsdr_source_0.get_setting_info()]

        self.soapy_rtlsdr_source_0.set_sample_rate(0, samp_rate)
        self.soapy_rtlsdr_source_0.set_frequency(0, (rf_freq + rx_offset))
        self.soapy_rtlsdr_source_0.set_frequency_correction(0, 0)
        self.set_soapy_rtlsdr_source_0_bias(bool(False))
        self._soapy_rtlsdr_source_0_gain_value = rx_gain
        self.set_soapy_rtlsdr_source_0_gain_mode(0, bool(False))
        self.set_soapy_rtlsdr_source_0_gain(0, 'TUNER', rx_gain)
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(afc_alpha, 1)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_f(
            256, #size
            bitrate, #samp_rate
            "Recovered Signal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-0.5, 1.5)

        self.qtgui_time_sink_x_1.set_y_label('Bit Value', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(True)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['Sliced Bits (0 or 1)', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['green', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "Demodulated Signal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Demodulated Float Baseband', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Received Signal", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(True)



        labels = ['RF Spectrum', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdu_tagged_stream_to_pdu_1 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_0 = network.socket_pdu('UDP_CLIENT', yamcs_host, yamcs_port, 10000, False)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccf(decim, lpf, (-rx_offset - freq_offset), samp_rate)
        self.digital_symbol_sync_xx_0_0 = digital.symbol_sync_ff(
            digital.TED_GARDNER,
            rx_sps,
            0.045,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts(access_key,
          0, "packet_len")
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_uchar_to_float_1 = blocks.uchar_to_float()
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, "packet_len", True, gr.GR_MSB_FIRST)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(int(rx_sps) , (1.0 / rx_sps), 1000, 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(gain)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.pdu_tagged_stream_to_pdu_1, 'pdus'), (self.network_socket_pdu_0, 'pdus'))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.digital_symbol_sync_xx_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.pdu_tagged_stream_to_pdu_1, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_uchar_to_float_1, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_uchar_to_float_1, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.soapy_rtlsdr_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.soapy_rtlsdr_source_0, 0), (self.qtgui_freq_sink_x_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rtlsdr_rx_ccsds_yamcs")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lpf(firdes.low_pass(1.0, self.samp_rate, self.channel_cutoff, self.channel_transition, window.WIN_HAMMING, 6.76))
        self.set_rx_samp_rate(self.samp_rate / self.decim)
        self.set_sps(int(self.samp_rate / self.bitrate))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.soapy_rtlsdr_source_0.set_sample_rate(0, self.samp_rate)

    def get_deviation(self):
        return self.deviation

    def set_deviation(self, deviation):
        self.deviation = deviation
        self.set_channel_cutoff(self.deviation + self.bitrate / 2 + 3_000)
        self.set_gain(self.rx_samp_rate / (2.0 * math.pi * self.deviation))

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.set_rx_samp_rate(self.samp_rate / self.decim)

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        self.set_channel_cutoff(self.deviation + self.bitrate / 2 + 3_000)
        self.set_rx_sps(self.rx_samp_rate / self.bitrate)
        self.set_sps(int(self.samp_rate / self.bitrate))
        self.qtgui_time_sink_x_1.set_samp_rate(self.bitrate)

    def get_rx_samp_rate(self):
        return self.rx_samp_rate

    def set_rx_samp_rate(self, rx_samp_rate):
        self.rx_samp_rate = rx_samp_rate
        self.set_afc_alpha(1 - math.exp(-2 * math.pi * 10 / self.rx_samp_rate))
        self.set_gain(self.rx_samp_rate / (2.0 * math.pi * self.deviation))
        self.set_rx_sps(self.rx_samp_rate / self.bitrate)

    def get_channel_transition(self):
        return self.channel_transition

    def set_channel_transition(self, channel_transition):
        self.channel_transition = channel_transition
        self.set_lpf(firdes.low_pass(1.0, self.samp_rate, self.channel_cutoff, self.channel_transition, window.WIN_HAMMING, 6.76))

    def get_channel_cutoff(self):
        return self.channel_cutoff

    def set_channel_cutoff(self, channel_cutoff):
        self.channel_cutoff = channel_cutoff
        self.set_lpf(firdes.low_pass(1.0, self.samp_rate, self.channel_cutoff, self.channel_transition, window.WIN_HAMMING, 6.76))

    def get_yamcs_port(self):
        return self.yamcs_port

    def set_yamcs_port(self, yamcs_port):
        self.yamcs_port = yamcs_port

    def get_yamcs_host(self):
        return self.yamcs_host

    def set_yamcs_host(self, yamcs_host):
        self.yamcs_host = yamcs_host

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_rx_sps(self):
        return self.rx_sps

    def set_rx_sps(self, rx_sps):
        self.rx_sps = rx_sps
        self.blocks_moving_average_xx_0.set_length_and_scale(int(self.rx_sps) , (1.0 / self.rx_sps))
        self.digital_symbol_sync_xx_0_0.set_sps(self.rx_sps)

    def get_rx_offset(self):
        return self.rx_offset

    def set_rx_offset(self, rx_offset):
        self.rx_offset = rx_offset
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((-self.rx_offset - self.freq_offset))
        self.soapy_rtlsdr_source_0.set_frequency(0, (self.rf_freq + self.rx_offset))

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.set_soapy_rtlsdr_source_0_gain(0, 'TUNER', self.rx_gain)

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.soapy_rtlsdr_source_0.set_frequency(0, (self.rf_freq + self.rx_offset))

    def get_lpf(self):
        return self.lpf

    def set_lpf(self, lpf):
        self.lpf = lpf
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.lpf)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.analog_quadrature_demod_cf_0.set_gain(self.gain)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((-self.rx_offset - self.freq_offset))

    def get_afc_alpha(self):
        return self.afc_alpha

    def set_afc_alpha(self, afc_alpha):
        self.afc_alpha = afc_alpha
        self.single_pole_iir_filter_xx_0.set_taps(self.afc_alpha)

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key




def main(top_block_cls=rtlsdr_rx_ccsds_yamcs, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
