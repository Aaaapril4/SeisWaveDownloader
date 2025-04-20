from obspy.clients.fdsn.mass_downloader import RectangularDomain
import configparser
import argparse

def get_config(para_path):
    para = configparser.ConfigParser()
    para.read(para_path)

    domain = RectangularDomain(
        minlatitude = para["Map Info"].getfloat("minLatitude"),
        maxlatitude = para["Map Info"].getfloat("maxLatitude"),
        minlongitude = para["Map Info"].getfloat("minLongitude"),
        maxlongitude = para["Map Info"].getfloat("maxLongitude"))

    return para, domain