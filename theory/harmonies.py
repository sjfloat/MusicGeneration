"""This models common intervals and chords, 
thus making it easy to generate "good" sounding
notes given a starting note."""

from scales import tone, semitone
import sys

common_intervals = dict(
    P1=0,d2=0,
    m2=semitone,A1=semitone,
    M2=semitone*2,d3=semitone*2,
    m3=semitone*3,A2=semitone*3,
    M3=semitone*4,d4=semitone*4,
    P4=semitone*5,A3=semitone*5,
    d5=semitone*6,A4=semitone*6,
    P5=semitone*7,d6=semitone*7,
    m6=semitone*8,A5=semitone*8,
    M6=semitone*9,d7=semitone*9,
    m7=semitone*10,A6=semitone*10,
    M7=semitone*11,d8=semitone*11,
    P8=semitone*12,A7=semitone*12)

_mod = sys.modules[__name__]
for (name,intv) in common_intervals.items():
    def curry(n, i):
        def f(note):
            return note + i
        f.__name__ = "interval_" + name
        f.__doc__ = "Given a note, return note at " + name
        return f
    setattr(_mod, name, curry(name, intv))

common_chords = dict(
    M=(P1,M3,P5),
    m=(P1,m3,P5),
    Aug5=(P1,M3,A5),
    m7=(P1,m3,P5,m7),
    M6=(P1,M3,P5,M6),
    M7=(P1,M3,P5,M7),
    dom7=(P1,M3,P5,m7),
    sus2=(P1,M2,P5),
    sus4=(P1,P4,P5),
    add2=(P1,M2,M3,P5),
    power=(P1,P5),
    dim5=(P1,M3,d5),
    dM7=(P1,M3,d5,M7),
    dm7=(P1,M3,d5,m7),
    AugM7=(P1,M3,A5,M7),
    Aug7=(P1,M3,A5,m7)
    )

def chord_for_root(root, chord_tuple):
    """Given a root node and a chord tuple, 
    generate all the notes in the chord.

    >>> chord_for_root(60,(P1,M3,P5))
    (60,64,67)
    """
    return tuple([f(root) for f in chord_tuple])

for (name, ctuple) in common_chords.items():
    def curry(name, chord_tuple):
        def f(note):
            return chord_for_root(note, chord_tuple)
        f.__name__ = "chord_" + name
        f.__doc__ = "Given a note, generate the {0} chord".format(name)
        return f
    setattr(_mod, "chord_" + name, curry(name,ctuple))