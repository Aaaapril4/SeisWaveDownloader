"""
SeisWaveDownloader - A package for downloading seismic waveform data from IRIS
"""

__version__ = "0.1.0"

from .download import (
    get_station,
    get_event_radius,
    get_nettime,
    download_cont,
    download_event
)
from .config import get_config

def main():
    """
    Main entry point for the SeisWaveDownloader package.
    This function can be used to run the package as a script.
    """
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Download seismic data from IRIS')
    parser.add_argument('--mode', type=str, choices=['continuous', 'event'],
                      help='Download mode: continuous or event')
    parser.add_argument('--config', type=str, default='para.ini',
                      help='Path to configuration file (default: para.ini)')
    
    args, unknown = parser.parse_known_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    para, domain = get_config(args.config)
    
    if args.mode == 'continuous':
        download_cont(para, domain)
    elif args.mode == 'event':
        download_event(para, domain)
    else:
        print("Please specify a download mode: --mode continuous or --mode event")
        sys.exit(1)
