#!/usr/bin/env python
"""
Script to run SeisWaveDownloader directly without installation
"""

import sys
import argparse
from seiswavedownloader import get_config, download_cont, download_event

def main():
    """
    Main entry point for the SeisWaveDownloader package.
    This function can be used to run the package as a script.
    """
    
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

if __name__ == '__main__':
    main() 