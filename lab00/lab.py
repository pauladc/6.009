# No Imports Allowed!


def backwards(sound):
    #cast reversed object to list
    reversed_samples = list(reversed(sound.get("samples")))
    reversed_dic = {"rate": sound.get("rate"), "samples": reversed_samples}
    return reversed_dic


def mix(sound1, sound2, p):
    #account for no sound
    if sound1.get("rate") != sound2.get("rate"):
        return None
    else:
        samples1 = [sample*p for sample in sound1.get("samples")]
        samples2 = [sample*(1-p) for sample in sound2.get("samples")]
        #find min length between samples
        truncate = min(len(samples1), len(samples2))
        finalsamples = [samples1[i] + samples2[i] for i in range(truncate)]   
        return {"rate": sound1.get("rate"), "samples": finalsamples}


def convolve(sound, kernel):
    samples = sound.get("samples")
    #presets desired length
    length = len(samples) + len(kernel) - 1
    #initiated to zeros so desired values can be added
    output = [0*i for i in range(length)]
    #will be iterated over to adjust for different kernels
    current_list = []
    for j in range(len(kernel)):
        #zeroes will be added at beginning and end when required (if len < desired length)
        current_list = [0] * j + [sample*kernel[j] for sample in samples] + [0] * (length - len(samples) - j)
        for i in range(length):
            output[i] += current_list[i]
    return {"rate": sound.get("rate"), "samples": output}
    


def echo(sound, num_echoes, delay, scale):
    sample_delay = round(delay * sound['rate'])
    samples = sound.get("samples")
    #desired length
    length = len(samples) + num_echoes * sample_delay
    #first copy plus zeros that will be adjusted
    output = samples.copy() + [0] * num_echoes * sample_delay
    #to be iterated over adjusting for changing scales
    current_list = []
    #will iterate over all echoes (added + 1 to ensure this)
    for i in range(1, num_echoes+1):
        current_list = [0] * sample_delay * i + [float(e)*scale**i for e in samples] + [0] * (len(output)-(sample_delay * i)-len(samples))
        for j in range(length):
            output[j] += current_list[j]
    return {"rate": sound.get("rate"), "samples": output}



def pan(sound):
    r_samples = sound.get("right")
    l_samples = sound.get("left")
    #created to not modify original value
    scaledr = []
    scaledl = []
    for i in range (len(r_samples)):
        scaledr.append(r_samples[i]* i/(len(r_samples)-1))
    for i in range (len(l_samples)):
        scaledl.append(l_samples[i]*(1 - (i/(len(r_samples)-1))))
    return {"rate": sound.get("rate"), "right": scaledr, "left": scaledl}



def remove_vocals(sound):
    r_samples = sound.get("right")
    l_samples = sound.get("left")
    #remove vocals by substracting right from left
    noVocal = [l_samples[i]-r_samples[i] for i in range(len(r_samples))]
    return {"rate": sound.get("rate"), "samples": noVocal}


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
from json import load
from turtle import write
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)

    mystery = load_wav('sounds/mystery.wav')
    #write_wav(backwards(mystery), "mystery_rev.wav")
    #mix1 = load_wav("sounds/synth.wav")
    #mix2 = load_wav("sounds/water.wav")
    #mixfiles = mix(mix1, mix2, 0.2)
    #write_wav(mixfiles, "mixed.wav")
    #chilli = load_wav('sounds/ice_and_chilli.wav')
    #convolved_chilli = convolve(chilli, bass_boost_kernel(1000, 1.5))
    #write_wav(convolved_chilli, "c_chilli.wav")

    # write_wav(backwards(hello), 'hello_reversed.wav')
    car = load_wav('sounds/car.wav', stereo=True)
    write_wav(pan(car), "pan_car.wav")

    chord = load_wav('sounds/chord.wav')
    chord_echoed = echo(chord, 5, 0.3, 0.6)
    write_wav(chord_echoed, "chord_echoed.wav")

    mountain = load_wav('sounds/lookout_mountain.wav', stereo=True)
    write_wav(remove_vocals(mountain), "no_vocals_mountain.wav")

