import json
import atexit

import numpy as np

# Load the compiled library
try:
    from .sdk_python3_module import *
    atexit.register(unload)

    __version__ = import_version

    info = json.loads(import_info_str)

    def ola(wav, fs, *args, **kwargs):

        if wav.ndim == 1:
            return import_ola(wav, fs, *args, **kwargs)
        else:
            nbc = wav.shape[1]
            syn = import_ola(np.mean(wav, axis=1), fs, *args, **kwargs)
            syn = np.repeat(syn[:,None], nbc, axis=1)
            # syn = []
            # for c in range(wav.shape[1]):
            #     X = import_ola(wav[:,c].copy(), fs, *args, **kwargs)
            #     syn.append(X)
            # syn = np.vstack(syn).T

        return syn

    def transform_timescaling(wav, fs, *args, **kwargs):
        if "winlen_inner" not in kwargs:
            kwargs["winlen_inner"] = int(fs*0.010)
        return transform(wav, fs, *args, **kwargs)

    def transform_pitchscaling(wav, fs, *args, **kwargs):
        if "es_order_cst_f0" not in kwargs:
            kwargs["es_order_cst_f0"] = True
        return transform(wav, fs, *args, **kwargs)

    def transform(wav, fs, *args, **kwargs):

        if "ts_pbf" in kwargs:
            pbf = kwargs["ts_pbf"]
            pbf = 1.0/pbf
            if pbf > 1.0:
                tsf = pbf - 1.0
            elif pbf < 1.0:
                tsf = - (1.0/pbf - 1.0)
            else:
                tsf = 0.0
            kwargs["tsf"] = tsf

        if wav.ndim == 1:
            return import_transform(wav, fs, *args, **kwargs)
        else:
            # TODO This does not preserve spatialization
            nbc = wav.shape[1]
            syn = import_transform(np.mean(wav, axis=1), fs, *args, **kwargs)
            syn = np.repeat(syn[:,None], nbc, axis=1)

        return syn

except ModuleNotFoundError as e:

    import os
    import glob

    modulename = os.path.basename(os.path.dirname(__file__))

    print(f"Failed to import {modulename}: {e}")

    modules = glob.glob(os.path.dirname(__file__)+'/*.so')  # TODO .so is wrong on Windows and Mac
    if len(modules)==0:
        print(f"No implementation found. The module is incomplete.\n")
    else:
        import sysconfig
        import platform
        import re

        def get_os_details(abi):
            version = 'unknown version'
            arch = 'unknown arch'
            os = 'unknown os'
            try:
                res = re.search(r'cpython-([^-]+)-([^-]+)-(.+)', abi)

                version = res.group(1)
                version = version[:1]+'.'+version[1:]

                arch = res.group(2)
                osname = res.group(3)
            except:
                # Can't block the information if this fails
                pass

            return f"Python {version}, Arch:{arch}, OS:{osname}"

        abi_current = sysconfig.get_config_var('SOABI')
        print(f"The version of the running python interpreter is {get_os_details(abi_current)} (ABI: {abi_current})")
        print(f"whereas this {modulename} module offers the versions:")
        for libfilepath in modules:
            libfilename = os.path.basename(libfilepath)
            abi_available = libfilename[len('sdk_python3_module.'):-len('.so')]
            print(f"    {get_os_details(abi_available)} (ABI: {abi_available})")

        print(f"It is very likely that this {modulename} module has been compiled for a different Python version, architecture or operating system.")

    raise e
