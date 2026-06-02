# `isolvocals`

A CLI that removes music/noise from audio (and soon video) files. This is
intended for background music/noise or intro/outro music/noise, not for
synthesizing vocals out of a song, for example.

The CLI currently uses [DeepFilterNet3](https://github.com/Rikorose/DeepFilterNet)
only (although I plan to make it support more models), which is designed for
just this task — to isolate vocals and remove surrounding background noise.

## Features

1. **Lightweight:** can run farely well on just a CPU (faster than real-time!)
2. **Streamable:** output media can be streamed with a media player.

## Installation

### Dependencies

`ffmpeg` must be installed before installing with `pip`.

#### Using `apt`
```
apt install ffmpeg
```

#### Using `brew`
```
brew install ffmpeg
```

#### Using `scoop`
```
scoop install main/ffmpeg
```

### Pip

To install through pip, run:

```
pip install git+https://github.com/ZXSQ1/isolvocals
```

### Uv

To install through uv, run:

```
uv pip install git+https://github.com/ZXSQ1/isolvocals
```

## Todo
- [ ] **Video:** allow videos to be processed and streamed (not just audio).
- [ ] **Load-time:** reduce load-time by optimizing imports.
- [ ] **Models:** support more models.
- [ ] **Temp files:** reduce temporary file creation in the code.
