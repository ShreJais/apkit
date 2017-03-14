"""
cc.py

(general) cross correlations

Copyright (c) 2017 Idiap Research Institute, http://www.idiap.ch/
Written by Weipeng He <weipeng.he@idiap.ch>
"""

import numpy as np
from itertools import izip

def _freq_upsample(s, upsample):
    """ padding in frequency domain, should be used with ifft so that
    signal is upsampled in time-domain.

    Args:
        s        : frequency domain signal
        upsample : an integer indicating factor of upsampling.

    Returns:
        padded signal
    """
    if upsample == 1:
        return s
    assert isinstance(upsample, int) and upsample > 1
    l = len(s)
    if l % 2 == 0:
        h = l / 2
        return upsample * np.concatenate(
                (s[:h], np.array([s[h] / 2.0]),
                 np.zeros(l * (upsample - 1) - 1),
                 np.array([s[h] / 2.0]), s[h+1:]))
    else:
        h = l / 2 + 1
        return upsample * np.concatenate(
                (s[:h], np.zeros(l * (upsample - 1)), s[h:]))

def gcc_phat(x, y, upsample=1):
    """GCC-PHAT

    Args:
        x  : 1-d array, frequency domain signal 1
        y  : 1-d array, frequency domain signal 2
        upsample : an integer indicating factor of upsampling.

    Returns:
        cc : cross correlation of the two signal, 1-d array,
             index corresponds to time-domain signal
    """
    cpsd = x * y.conj()
    cpsd_phat = cpsd / np.abs(cpsd)
    cpsd_phat = _freq_upsample(cpsd_phat, upsample)
    return np.real(np.fft.ifft(cpsd_phat))

def cross_correlation(x, y, upsample=1):
    """Cross correlation

    Args:
        x  : 1-d array, frequency domain signal 1
        y  : 1-d array, frequency domain signal 2
        upsample : an integer indicating factor of upsampling.

    Returns:
        cc : cross correlation of the two signal, 1-d array,
             index corresponds to time-domain signal
    """
    cpsd = _freq_upsample(x * y.conj(), upsample)
    return np.real(np.fft.ifft(cpsd) / np.max(np.abs(cpsd)))

def tdoa(x, y, cc_func, fs=None):
    """Estimate time difference of arrival (TDOA) by finding peak in (G)CC.

    Args:
        x       : 1-d array, frequency domain signal 1
        y       : 1-d array, frequency domain signal 2
        cc_func : cross correlation function.
        fs      : sample rate, if not given (default) the result is number
                  of samples

    Returns:
        tdoa    : estimate of TDOA
    """
    cc = cc_func(x, y)
    peak_at = np.argmax(cc)
    if peak_at > len(cc) / 2:
        peak_at = peak_at - len(cc)
    if fs is None:
        return peak_at
    else:
        return 1.0 * peak_at / fs

def cc_across_time(tfx, tfy, cc_func):
    """Cross correlations across time.

    Args:
        tfx     : time-frequency domain signal 1.
        tfy     : time-frequency domain signal 2.
        cc_func : cross correlation function.

    Returns:
        cc_atime : cross correlation at different time.

    Note:
        If tfx and tfy are not of the same length, the result will be 
        truncated to the shorter one.
    """
    return np.array([cc_func(x, y) for x, y in izip(tfx, tfy)])

def pairwise_cc(tf, cc_func):
    """Pairwise cross correlations between all channels in signal.
    
    Args:
        tf      : multi-channel time-frequency domain signal.
        cc_func : cross correlation function.

    Returns:
        pw_cc   : pairwise cross correlations,
                  dict : (channel id, channel id) -> cross correlation across time.
    """
    nch = len(tf)
    return {(x, y) : cc_across_time(tf[x], tf[y], cc_func)
                for x in range(nch) for y in range(nch) if x < y}

# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

