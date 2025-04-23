# SeisWaveDownloader
A lightweight tool to download seismic waveforms from IRIS parallelly

## Installation
For Anaconda, simply create a new environment, install dependencies, and install.
```Bash
conda create -n seiswave python=3.9
conda install obspy tqdm
python3 setup.py install
```
## Usage
Two modes: `continuous` or `event`
The connection might be unstable (which I'm still trying to figure out), so try several times and try 1 cpu in the end.
```Bash
seiswave --mode mode --config pathToConfig
```
