# DSP ENV
I want an environment to practice doing some DSP things. First up is TDOA/FDOA processing.

## Structure
I'm going to structure the environment as
 * sig/ <- signal generation, waveforms, etc.
 * sim/ <- geometry, kinematics, etc.
 * rx/ <- TDOA/FDOA estimators
 * geo/ <- geolocation engine/solver
 * viz/ <- visualization stuff
 * exp/ <- experiments, notebooks, etc.

## Roadmap
For now, I'm just going to write everything in Python. I may eventually do some C++/MATLAB stuff but this will make it easiest to start.
First up I want to just write the basics: simple kinematics and range/doppler calculation given some fake values.
Then, probably more complicated waveforms and kinematics. Then noise, estimators, etc.