"""
basic.py

basic functions

Copyright (c) 2017 Idiap Research Institute, http://www.idiap.ch/
Written by Weipeng He <weipeng.he@idiap.ch>
"""

import numpy as np
import scipy.io.wavfile

def load_wav(filename):
    """Load wav file, convert to normalized float value

    Args:
        filename : string or open file handle.

    Returns:
        fs       : sample rate.
        signal   : multi-channel time-domain signal.
    """
    fs, signal = scipy.io.wavfile.read(filename)
    if not np.issubdtype(signal.dtype, np.float):
        assert np.issubdtype(signal.dtype, np.integer)
        signal = signal.astype(float) / abs(np.iinfo(signal.dtype).min)
    if signal.ndim == 1:
        signal = np.expand_dims(signal, axis=1)
    return fs, signal.T

def save_wav(filename, fs, signal):
    """Save audio data as wave file.

    Args:
        filename : string or open file handle.
        fs       : sample rate.
        signal   : multi-channel time-domain signal.
    """
    scipy.io.wavfile.write(filename, fs, signal.T)

def cola_hamming(win_size, hop_size):
    """ Hamming window, periodic and constant-overlap-add (COLA, sum=1)

    Args:
        win_size : window size
        hop_size : hop size

    Returns:
        w        : window coefficients
    """
    return np.hamming(win_size + 1)[0:win_size] \
                / 1.08 * hop_size / win_size * 2
    
def stft(signal, window, win_size, hop_size):
    """Convert time-domain signal to time-frequency domain.

    Args:
        signal   : multi-channel time-domain signal
        window   : window function, see cola_hamming as example.
        win_size : window size
        hop_size : hop size

    Returns:
        tf       : multi-channel time-frequency domain signal.
    """
    assert signal.ndim == 2
    w = window(win_size, hop_size)
    return np.array([[np.fft.fft(c[t:t+win_size] * w) 
        for t in xrange(0, len(c) - win_size, hop_size)] for c in signal])

def istft(tf, hop_size):
    """Inverse STFT

    Args:
        tf       : multi-channel time-frequency domain signal.
        window   : window function, see cola_hamming as example.
        win_size : window size
        hop_size : hop size

    Returns:
        signal   : multi-channel time-domain signal
    """
    tf = np.asarray(tf)
    nch, nframe, nfbin = tf.shape
    signal = np.zeros((nch, (nframe - 1) * hop_size + nfbin))
    for t in xrange(nframe):
        signal[:, t*hop_size:t*hop_size+nfbin] += \
                np.real(np.fft.ifft(tf[:, t]))
    return signal

def freq_upsample(s, upsample):
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

def power(signal):
    """Signal power

    Args:
        signal : multi-channel time-domain signal

    Returns:
        power  : power of each channel.
    """
    nch, nsamples = signal.shape
    return np.einsum('ct,ct->c', signal, signal) / float(nsamples)

def snr(sandn, noise):
    """Signal-to-noise ratio given signal with noise and noise

    Args:
        sandn : signal and noise multi-channel time-domain signal
        noise : noise multi-channel time-domain signal

    Returns:
        snr   : snr of each channel in dB.
    """
    pnos = power(noise)
    psig = power(sandn) - pnos
    return 10 * np.log10(psig / pnos)

# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

