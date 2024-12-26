import os
import subprocess

def play_audio(audio_file):
    os.environ["PULSE_SERVER"] = "/run/user/1000/pulse/native"
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"
    subprocess.run(["ffplay", "-nodisp", "-autoexit", audio_file])

if __name__ == "__main__":
    play_audio("object_detected.mp3")