"""Unit tests for sample generators."""

import os
import unittest
from . import *
from . import generators
from . import envelopes


class TestSampleGeneration(unittest.TestCase):
    def test_squarewave(self):
        sq_gen = generators.SquareWaveGenerator(2,4)
        data = sq_gen.get(4)
        self.assertEqual(type(data), list)
        self.assertEqual(data, [1.0, -1.0, 1.0, -1.0])

        sq_gen = generators.SquareWaveGenerator(200)
        data = sq_gen.get(40)
        self.assertEqual(data, 40 * [1.0])

    def test_sawtoothwave(self):
        saw_gen = generators.SawtoothWaveGenerator(2,8)
        data = saw_gen.get(8)
        self.assertEqual(data, [-1.0, -0.5, 0.0, 0.5, -1.0, -0.5, 0.0, 0.5])

    def test_sinewave(self):
        sine_gen = generators.SineWaveGenerator(441)
        data = sine_gen.get(100)
        self.assertEqual(type(data), list)
        self.assertTrue(type(data[0]) is float)
        for (i, sample) in enumerate(data):
            if i < 50:
                self.assertTrue(sample >= 0)
            else:
                self.assertTrue(sample <= 0)

    def test_delayed_generator(self):
        constant_gen = generators.ConstantGenerator(constant=-0.5)
        delay_get = generators.DelayedGenerator(source=constant_gen, start_time=0.5)
        data = delay_get.get(SAMPLING_RATE)
        self.assertEqual(min(data[:int(SAMPLING_RATE/2)]), 0)
        self.assertEqual(max(data[:int(SAMPLING_RATE/2)]), 0)
        self.assertEqual(min(data[int(SAMPLING_RATE/2):]), -0.5)
        self.assertEqual(max(data[int(SAMPLING_RATE/2):]), -0.5)

        delay_get = generators.DelayedGenerator(source=constant_gen, start_time=0.0)
        data = delay_get.get(SAMPLING_RATE)
        self.assertEqual(min(data), -0.5)
        self.assertEqual(max(data), -0.5)

        delay_gen = generators.DelayedGenerator(source=constant_gen, start_time=60.0)
        data = delay_gen.get(SAMPLING_RATE)
        self.assertEqual(min(data), 0)
        self.assertEqual(max(data), 0)

    def test_wavefile_generator(self):
        # TODO: Obviously crappy test. I'm not sure how to specify a relative path so that
        # this test wav file is found.
        filename = "C:\\Users\\oconaire\\Documents\\GitHub\\MusicGeneration\\MusicGeneration\\wav_data\\drums\\DR1-0.WAV"
        if os.path.exists(filename):
            wavefile_gen = generators.WaveFileGenerator(filename)
            data = wavefile_gen.get(SAMPLING_RATE)
            print("Data length = %d" % len(data))
            zcr = lambda d: sum([(x*y) < 0 for (x,y) in zip(d[:-1], d[1:])])
            z0 = zcr(data)
            print("ZCR(data) = %d" % z0)
            self.assertTrue(z0 > 100)
            last_sample = int(0.037 * SAMPLING_RATE)
            z1 = zcr(data[last_sample:])
            self.assertEqual(z1, 0)
            self.assertEqual(min(data[last_sample:]), 0)
            self.assertEqual(max(data[last_sample:]), 0)
            self.assertLess(min(data[:last_sample]), -0.25)
            self.assertGreater(max(data[:last_sample]), 0.25)


class TestEnvelopes(unittest.TestCase):
    def test_volume_envelope(self):
        constant_gen = generators.ConstantGenerator()
        vol_env = envelopes.VolumeEnvelope(source=constant_gen, volume=0.33)
        data = vol_env.get(64)
        self.assertEqual(type(data), list)
        self.assertEqual(data, 64 * [0.33])

    def test_standard_envelope_simple(self):
        constant_gen = generators.ConstantGenerator()
        # Total note length of 1 second
        vol_env = envelopes.StandardEnvelope(
            source=constant_gen,
            peak=0.9,
            level=0.8,
            attack=0.1,
            decay=0.1,
            sustain=0.6,
            release=0.2,
            sampling_rate=20)
        data = vol_env.get(21)
        expected = [0.0, 0.45, 0.9, 0.85,
                    0.8, 0.8, 0.8, 0.8, 0.8, 0.8,
                    0.8, 0.8, 0.8, 0.8, 0.8, 0.8,
                    0.8, 0.6, 0.4, 0.2, 0.0]
        for (d,e) in zip(data, expected):
            self.assertAlmostEqual(d, e)

    def test_standard_envelope(self):
        constant_gen = generators.ConstantGenerator()
        # Total note length of 1 second
        vol_env = envelopes.StandardEnvelope(
            source=constant_gen,
            peak=0.9,
            level=0.8,
            attack=0.1,
            decay=0.1,
            sustain=0.6,
            release=0.2)
        data = vol_env.get(SAMPLING_RATE + 1)
        one_tenth = int(SAMPLING_RATE / 10)
        self.assertEqual(type(data), list)
        # Peak and trough should be 0.9 and 0.0
        self.assertAlmostEqual(min(data[:2*one_tenth]), 0.0)
        self.assertAlmostEqual(max(data[:2*one_tenth]), 0.9)
        # Sustain should be 0.8 exactly
        self.assertEqual(min(data[2*one_tenth:8*one_tenth]), 0.8)
        self.assertEqual(max(data[2*one_tenth:8*one_tenth]), 0.8)
        # Release max/min should be 0.8 and 0.0
        self.assertAlmostEqual(min(data[8*one_tenth:SAMPLING_RATE+1]), 0)
        self.assertAlmostEqual(max(data[8*one_tenth:SAMPLING_RATE+1]), 0.8)



def main():
    unittest.main()
