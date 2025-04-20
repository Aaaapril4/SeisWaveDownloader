# Seiswave
A lightweight tool to download seismic waveform from IRIS parallelly

## Installation
For anaconda, simply create a new environment, install dependencies and 
```Bash
conda create -n seiswave python=3.9
conda install obspy tqdm
python3 setup.py install
```
## Usage
Two modes: `continuous` or `event`
```Bash
seiswave --mode mode --config pathToConfig
```