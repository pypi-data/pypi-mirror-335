
========
pyggwave
========

A fork of tiny data-over-sound library with improved documentation and Python compatibility.


.. code:: python

    # generate audio waveform for string "hello python"
    waveform = pyggwave.encode("hello python")

    # decode audio waveform
    text = pyggwave.decode(instance, waveform)


--------
Features
--------

* Audible and ultrasound transmissions available
* Bandwidth of 8-16 bytes/s (depending on the transmission protocol)
* Robust FSK modulation
* Reed-Solomon based error correction

------------
Installation
------------
::

    pip install pyggwave

---
API
---

encode()
--------

.. code:: python

    encode(payload, [protocolId], [volume], [instance])

Encodes ``payload`` into an audio waveform.


Output of ``help(pyggwave.encode)``:

.. code::

    cython_function_or_method in module pyggwave
    
    encode(
        self,
        payload: 'bytes | str',
        protocol_id: 'int' = 5,
        volume: 'int' = 100
    ) -> 'bytes'
        Encode payload into an audio waveform.
        @param {string} payload, the data to be encoded
        @return Generated audio waveform bytes representing 16-bit signed integer samples.
    

decode()
--------

.. code:: python

    decode(instance, waveform)

Analyzes and decodes ``waveform`` into to try and obtain the original payload.
A preallocated pyggwave ``instance`` is required.


Output of ``help(pyggwave.decode)``:

.. code::

    cython_function_or_method in module pyggwave
    
    decode(self, frame: 'bytes') -> 'bytes | None'
        Analyze and decode audio waveform to obtain original payload
        @param {bytes} waveform, the audio waveform to decode
        @return The decoded payload if successful.
    


-----
Usage
-----

* Encode and transmit data with sound:

.. code:: python

    import pyggwave
    import pyaudio

    p = pyaudio.PyAudio()

    ggwave = pyggwave.GGWave()

    # generate audio waveform for string "hello python"
    waveform = ggwave.encode("hello python", protocol_id=3)

    print("Transmitting text 'hello python' ...")
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True, frames_per_buffer=4096)
    stream.write(waveform, len(waveform) // 4)

    ggwave.free()

    stream.stop_stream()
    stream.close()

    p.terminate()

* Capture and decode audio data:

.. code:: python

    import pyggwave
    import pyaudio

    p = pyaudio.PyAudio()

    ggwave = pyggwave.GGWave()

    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)

    print('Listening ... Press Ctrl+C to stop')

    try:
        while True:
            data = stream.read(1024, exception_on_overflow=False)
            res = ggwave.decode(data)

            if res:
                try:
                    print('Received text: ' + res.decode("utf-8"))
                except as exc:
                    print(exc)
    except KeyboardInterrupt:
        pass

    ggwave.free()

    stream.stop_stream()
    stream.close()

    p.terminate()

----
More
----

Check out `<http://github.com/ggerganov/ggwave>`_ for more information about ggwave!

-----------
Development
-----------

Check out `pyggwave python package on Github <https://github.com/tpyauheni/pyggwave/tree/master/bindings/python>`_.
