import logging
import asyncio
import os
import socket
import argparse

from PeerProtocol import PeerProtocol
from TrackerClientProtocol import TrackerClientProtocol
from SimpleTracker import SimpleTracker

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logging.info ("PyPPSPP starting")

def main(args):
    logging.info("PPSPP Parameters:\n\tTracker: {};\n\tFilename: {};\n\tFilesize: {}B;\n\tSwarm: {};\n\tLive: {};\n\tLive Source: {};"
                 .format(args.tracker, args.filename, args.filesize, args.swarmid, args.live, args.livesrc))

    # Start minimalistic event loop
    loop = asyncio.get_event_loop()
    loop.set_debug(False)

    tracker = SimpleTracker()

    # Create connection to the tracker node
    # All this code should be hidden in the Tracekr and Swarm manager!
    tracker_listen = loop.create_connection(lambda: TrackerClientProtocol(tracker), args.tracker, 6777)
    tracker_transport, traceker_server = loop.run_until_complete(tracker_listen)

    # TODO - check if connected to the Tracekr!
    tracker.SetTrackerProtocol(traceker_server)

    # Create an UDP server
    # Since we are using Tracker, we don't have to run n 6778 port!
    listen = loop.create_datagram_endpoint(PeerProtocol, local_addr=("0.0.0.0", 6778))
    transport, protocol = loop.run_until_complete(listen)

    # At this point we have connection to the tracker and listening UDP socket

    # Start the swarm
    # TODO: This is not the right place to do it...

    # Create the swarm
    protocol.init_swarm(args)

    # Inform tracker about swarm ready to receive connections
    tracker.SetSwarm(protocol.swarm)

    # Register with the tracker
    tracker.RegisterWithTracker(None)

    # Schedule wakeups to catch Ctrl+C in Win32
    # This should be fixed in Python 3.5 
    # Ref: http://stackoverflow.com/questions/24774980/why-cant-i-catch-sigint-when-asyncio-event-loop-is-running
    if os.name == 'nt':
        def wakeup():
            # Call again later
            loop.call_later(0.5, wakeup)
        loop.call_later(0.5, wakeup)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Inform protocol to close
    protocol.CloseProtocol()

    tracker.UnregisterWithTracker()

    # Clean-up
    transport.close()
    loop.close()

if __name__ == "__main__":
    # Set the default parameters
    defaults = {}
    defaults['trackerip'] = "10.51.32.121"
    defaults['filename'] = "C:\\PyPPSPP\\test50MB.bin"
    defaults['swarmid'] = "c902da8128108e105d26597b7570b8411f651444"
    defaults['filesize'] = 52428800
    defaults['live'] = False
    defaults['live_src'] = False

    # Parse command line parameters
    parser = argparse.ArgumentParser(description="Python implementation of PPSPP protocol")
    parser.add_argument("--tracker", help="Tracker IP address", nargs="?", default=defaults['trackerip'])
    parser.add_argument("--filename", help="Filename of the shared file", nargs="?", default=defaults['filename'])
    parser.add_argument("--swarmid", help="Hash value of the swarm", nargs="?", default=defaults['swarmid'])
    parser.add_argument("--filesize", help="Size of the file", nargs="?", type=int, default=defaults['filesize'])
    parser.add_argument("--live", help="Is this a live stream", nargs="?", type=bool, default=defaults['live'])
    parser.add_argument("--livesrc", help="Is this a live stream source", nargs="?", type=bool, default=defaults['live_src'])
    parser.add_argument("--numpeers", help="Limit the number of peers", nargs="?", type=int)
    parser.add_argument("--identifier", help="Free text that will be added to the results file", nargs="?")
    
    # Start the program
    args = parser.parse_args()
    main(args)