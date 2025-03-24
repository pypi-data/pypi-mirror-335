from pydub import AudioSegment

class AudioMixer:
    def __init__(self):
        pass

    def mix_audios(self, audio_files, output_file, volume_adjustments=None):
        """
        Mix multiple audio files into one.

        :param audio_files: List of paths to audio files to mix.
        :param output_file: Path to save the mixed audio file.
        :param volume_adjustments: List of volume adjustments for each audio file.
        """
        mixed = AudioSegment.silent(duration=0)

        for i, audio_file in enumerate(audio_files):
            audio = AudioSegment.from_file(audio_file)
            if volume_adjustments and i < len(volume_adjustments):
                audio = audio + volume_adjustments[i]
            mixed = mixed.overlay(audio)

        mixed.export(output_file, format="mp3")
        print(f"Mixed audio saved to {output_file}")