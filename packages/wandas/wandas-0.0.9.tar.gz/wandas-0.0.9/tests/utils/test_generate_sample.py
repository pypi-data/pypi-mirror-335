# tests/utils/test_generate_sample.py

from wandas.core.channel import Channel
from wandas.core.channel_frame import ChannelFrame
from wandas.utils.generate_sample import generate_sin


def test_generate_sin_single_frequency() -> None:
    freq = 1000.0
    sampling_rate = 16000
    duration = 1.0
    signal = generate_sin(
        freqs=freq, sampling_rate=sampling_rate, duration=duration, label="Test Signal"
    )

    assert isinstance(signal, ChannelFrame)
    assert signal.label == "Test Signal"
    assert len(signal._channels) == 1
    channel = signal._channels[0]
    assert isinstance(channel, Channel)
    assert channel.sampling_rate == sampling_rate
    assert channel.label == "Channel 1"
    assert len(channel.data) == int(sampling_rate * duration)


def test_generate_sin_multiple_frequencies() -> None:
    freqs = [500.0, 800.0, 1000.0]
    sampling_rate = 16000
    duration = 1.0
    signal = generate_sin(
        freqs=freqs, sampling_rate=sampling_rate, duration=duration, label="Test Signal"
    )

    assert isinstance(signal, ChannelFrame)
    assert signal.label == "Test Signal"
    assert len(signal._channels) == len(freqs)
    for idx, channel in enumerate(signal._channels):
        assert isinstance(channel, Channel)
        assert channel.sampling_rate == sampling_rate
        assert channel.label == f"Channel {idx + 1}"
        assert len(channel.data) == int(sampling_rate * duration)
