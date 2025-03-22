#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import json

import requests
from .lib.utils import load_csv_labels
from .lib.models import Cnn14_pruned
from .lib.inference import AudioModelInference, PredictionTracker
from torch import load as loadModel
from torch.cuda import is_available as hasCUDA
from librosa.core import load as loadAudio
from typer import Argument, Option, BadParameter
from typing_extensions import Annotated
from platformdirs import user_cache_dir
from pathlib import Path

samplerate = 32000
model_winsize = 1024
stft_hopsize = 320
stft_window = "hann"
n_mels = 64
mel_fmin = 50
mel_fmax = 14000

checkpoint_url = "https://zenodo.org/records/7939403/files/checkpoint_closeto_.44.pt?download=1"

default_labels_path = os.path.join(os.path.dirname(__file__), "config", "audioset_labels.csv")
default_top_k = 10
cache_dir = user_cache_dir('epanns')
default_checkpoint_path = os.path.join(cache_dir, "checkpoint_closeto_.44.pt")

def download_checkpoint():
  try:
    os.makedirs(os.path.dirname(default_checkpoint_path), exist_ok=True)
    response = requests.get(checkpoint_url, stream=True)
    response.raise_for_status()
    with open(default_checkpoint_path, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
          if chunk:
            file.write(chunk)
  except requests.exceptions.RequestException as e:
      sys.exit(f"Error downloading from {checkpoint_url}")
  except IOError as e:
      sys.exit(f"Error writing file {default_checkpoint_path}")

def save_prediction(pred: any, output_dir: str, file: str):
  file_name = Path(file).stem
  os.makedirs(output_dir, exist_ok=True)
  file_path = os.path.join(output_dir, f'{file_name}.json')
  with open(file_path, 'w') as file_out:
    json.dump(pred, file_out)

def check_path(value: str):
  if not os.path.isfile(value) and not os.path.isdir(value):
    raise BadParameter("Path does not exist")
  return value

def check_checkpoint_path(value: str):
  if value != default_checkpoint_path and not os.path.isfile(value):
    raise BadParameter("File does not exist")
  return value

def check_top_k(value: int):
  if value < 1:
      raise BadParameter("Top K must be 1 or greater")
  return value

def predict(
  audio_path: str = "",
  top_k: int = default_top_k,
  checkpoint_path: str = default_checkpoint_path,
  audioset_labels_path: str = default_labels_path
):
  if checkpoint_path == default_checkpoint_path and not os.path.isfile(checkpoint_path):
    print(f"Downloading model to {default_checkpoint_path}", file=sys.stderr)
    download_checkpoint()

  print(f"Loading labels from {audioset_labels_path}", file=sys.stderr)
  _, _, audioset_labels = load_csv_labels(audioset_labels_path)
  num_audioset_classes = len(audioset_labels)

  print(f"Loading model", file=sys.stderr)
  model = Cnn14_pruned(
    samplerate, model_winsize, stft_hopsize, n_mels,
    mel_fmin, mel_fmax, num_audioset_classes,
    p1=0,p2=0,p3=0,p4=0,p5=0,p6=0,p7=0.5,p8=0.5,p9=0.5,p10=0.5,p11=0.5,p12=0.5
  )

  print(f"Loading checkpoint from {checkpoint_path}", file=sys.stderr)
  checkpoint = loadModel(checkpoint_path, map_location=lambda storage, loc: storage)
  model.load_state_dict(checkpoint)

  print(f"Loading audio from {audio_path}", file=sys.stderr)
  (audio, _) = loadAudio(audio_path, sr=samplerate, mono=True)

  device = "cuda" if hasCUDA() else "cpu"
  print(f"Running inference on {device}", file=sys.stderr)
  inference = AudioModelInference(
      model, model_winsize, stft_hopsize, samplerate,
      stft_window, n_mels, mel_fmin, mel_fmax)
  tracker = PredictionTracker(audioset_labels)
  dl_inference = inference(audio, device)
  top_preds = tracker(dl_inference, top_k)
  return top_preds

def run(
  audio_path: Annotated[Path, Argument(help="Path to the audio file or directory", callback=check_path)] = "",
  top_k: Annotated[int, Option(help="Number of classes to return", callback=check_top_k)] = default_top_k,
  checkpoint_path: Annotated[Path, Option(help="Path of checkpoint", callback=check_checkpoint_path)] = default_checkpoint_path,
  audioset_labels_path: Annotated[Path, Option(help="Path of labels", callback=check_path)] = default_labels_path,
  output_dir: Annotated[Path, Option(help="Directory to output the predictions")] = ""
):
  audio_path = audio_path.resolve()
  output_dir = output_dir.resolve()
  if os.path.isdir(audio_path):
    top_preds = []
    for file in os.listdir(audio_path):
      file_path = os.path.join(audio_path, file)
      pred = predict(file_path, top_k, checkpoint_path, audioset_labels_path)
      top_preds.append(pred)
      if output_dir != "": 
        save_prediction(pred, output_dir, file)
  else: 
    top_preds = predict(audio_path, top_k, checkpoint_path, audioset_labels_path)
    if output_dir != "": 
      save_prediction(top_preds, output_dir, audio_path)
  
  print(json.dumps(top_preds, indent=2))
