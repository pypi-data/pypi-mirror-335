# PyAWG

A simple (unofficial) python library to control some functions of Arbitrary Waveform Generators (aka Function / Signal Generators) from various manufacturers.

Currently following function generators are supported. Volunteers are welcome to extend it to support other models keeping the basic functions same.

## Siglent
- [Siglent SDG1000X Series Arbitrary Waveform Generator](https://www.siglenteu.com/download/8715/?tmstv=1740404771) 
  - SDG1032X
  - SDG1062X

## Rigol
- [Rigol DG1000Z Series Arbitrary Waveform Generator](https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DG1000Z_ProgrammingGuide_EN.pdf)
  - DG1032Z
  - DG1062Z

## System Requirements

- Python (>=3.8,<4.0)

## Installation

Installation of the library is very simple via `pip` command as shown below.

```python
>>> pip install pyawg
```

## Usage

Here is an exmaple with Rigol DG1032Z Arbitrary Waveform Generator. For the variants from other manufacturers, the `DEBUG` logs would be printed slightly different based on their respective syntax. 

```python
>>> from pyawg import awg_control, AmplitudeUnit, FrequencyUnit, WaveformType

>>> # Example for Square Wave of 10KHz, 5VPP with offset of 2.5V and phase shift of 90°

>>> awg = awg_control('192.168.1.100')
[2025.03.06 21:12:46][DEBUG] Connected to AWG at 192.168.1.100
[2025.03.06 21:12:46][DEBUG] Sent query: *IDN?, Received: Rigol Technologies,DG1032Z,DG1ZA2012604407,03.01.12  
[2025.03.06 21:12:46][DEBUG] RigolDG1000Z instance created.

>>> awg.set_waveform(1, WaveformType.SQUARE)
[2025.03.06 21:15:51][DEBUG] Sent command: SOUR1:FUNC SQU
[2025.03.06 21:15:51][DEBUG] Channel 1 waveform set to SQU

>>> awg.set_frequency(1, 10, FrequencyUnit.KHZ)
[2025.03.06 21:16:41][DEBUG] Sent command: SOUR1:FREQ 10KHZ
[2025.03.06 21:16:41][DEBUG] Channel 1 frequency set to 10KHZ

>>> awg.set_amplitude(1, 5, AmplitudeUnit.VPP)
[2025.03.06 21:18:19][DEBUG] Sent command: SOUR1:VOLT 5VPP
[2025.03.06 21:18:19][DEBUG] Channel 1 amplitude set to 5VPP

>>> awg.set_offset(1, 2.5)
[2025.03.06 21:20:02][DEBUG] Sent command: SOUR1:VOLT:OFFS 2.5
[2025.03.06 21:20:02][DEBUG] Channel 1 offset voltage set to 2.5 Vdc

>>> awg.set_phase(1, 90)
[2025.03.06 21:25:08][DEBUG] Sent command: SOUR1:PHAS 90
[2025.03.06 21:25:08][DEBUG] Channel 1 phase set to 90°

>>> awg.set_output(1, True)
[2025.03.06 21:25:34][DEBUG] Sent command: OUTP1 ON
[2025.03.06 21:25:34][DEBUG] Channel 1 output has been set to ON
```
