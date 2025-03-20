import logging

import os
import sys
import glob

import numpy as np
import soundfile

import phoneshift

def assert_nan_inf(wav):
    idx = np.where(np.isnan(wav))[0]
    assert len(idx)==0

    idx = np.where(np.isinf(wav))[0]
    assert len(idx)==0

def assert_diff_sigs(ref, test, thresh_max=phoneshift.float32.eps, thresh_rmse=phoneshift.float32.eps):
    assert ref.shape == test.shape

    assert_nan_inf(test)

    err = ref - test

    if 0:
        os.makedirs(f'test_data/debug', exist_ok=True)
        err = wav - syn
        soundfile.write(f'test_data/debug/{bbasename}.ref.wav', wav, fs)
        soundfile.write(f'test_data/debug/{bbasename}.test.wav', syn, fs)
        soundfile.write(f'test_data/debug/{bbasename}.err.wav', err, fs)

    RMSE = np.sqrt(np.mean(err**2))
    MAXE = max(abs(err))
    info = {'RMSE':phoneshift.lin2db(RMSE), 'MAXE':phoneshift.lin2db(MAXE)}

    if RMSE > thresh_rmse:
        logging.error(f"RMSE is {RMSE} ({phoneshift.lin2db(RMSE)}dB) > {thresh_rmse} ({phoneshift.lin2db(thresh_rmse)}dB)")
        return False, info

    if MAXE > thresh_max:
        logging.error(f'Max diff {MAXE} ({phoneshift.lin2db(MAXE)}dB) > {thresh_max} ({phoneshift.lin2db(thresh_max)}dB)')
        # err_idx = np.where(abs(err)>thresh_max)[0]
        # if len(err_idx)>0:
        #     for n in err_idx:
        #         logging.error(f'ref[{n}]={ref[n]} test[{n}]={test[n]} err={err[n]} ({phoneshift.lin2db(err[n])}dB) > {thresh_max} ({phoneshift.lin2db(thresh_max)}dB)')

        return False, info

    return True, info


def filepaths_to_process():
    fpaths = glob.glob(f"{os.path.dirname(__file__)}/test_data/wav/*.wav")
    assert len(fpaths) > 0
    return fpaths


# def dir_refs(self):
#     return '../phoneshift/sdk_python3/test_data/refs'

# def dir_output(self):
#     return 'test_data/sdk_python3'
