# Yamcs Teststing

## Use Python Script

Start Yamcs. Run in this folder:

```bash
cd tests/yamcs
docker compose up
```

Open <http://localhost:8090> and go to `Telemetry/Parameters`.

Open the simulation_flowgraph_udp.grc in GNU Radio and run it.

Then install dependencies and start the simulator:

```bash
cd tests/yamcs
python -m venv venv
source venv/bin/activate
pip install spacepacket
python simulator.py
```

This will send CCSDS Telemetry Packets to GNURadio via UDP. A raw packet may look like this: `0064c000000700000001410f22cf`.

Additional flowgraphs can be used. For example, simulation_flowgraph.grc does not require to run the simulation and sends `0064c000000700000001410f22cf` (padded to fill the TM Frame) every second to Yamcs via UDP.

Moreover flowgraphs using SDR hardware are available. For transmission, you can use the flowgraph limesdr_tx_ccsds.grc or limesdr_tx_ccsds_udp.grc (if you want to use the simulator.py) and for reception, you can use the rtlsdr_rx_ccsds.grc.
