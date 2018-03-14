# ffmpeg commands
Snippets for using ffmpeg

## Add subtitle to mkv
Given: vid.mkv and vid.ass as video and subtitle. Subtitle language is chinese (chi)

Export: output.mkv

Note: Only 1st video stream and 1st audio stream will preserve in output.
Others will be destroyed in convert process.

```bash
ffmpeg -i vid.mkv \
  -i vid.ass \
  -metadata:s:s:0 language=chi \
  -codec copy \
  output.mkv
```

## Add subtitle, select specific audio stream
Given:
 - input.mkv contains audio stream with language `jpn` (May have multiple audio)
 - input.ass is subtitle in chinese (chi)

Output:
Japanese audio, Chinese subtitle with video

```bash
ffmpeg -i input.mkv \
  -i input.ass \
  -map 0:a:language:jpn -map 0:v -map 1:s \
  -metadata:s:s:0 language=chi \
  -codec copy \
  output.mkv
```

## Set subtitle offset
Given:
 - Subtitle is soft-coded
 - Want to offset by -0.2 second

```bash
ffmpeg -i input.mkv \
  -itsoffset -0.2 -i input.mkv \
  -map 0:v -map 0:a -map 1:s \
  -c copy \
  output.mkv
```

## Extract subtitle
Given:
 - Subtitle is soft-coded
 - Want to extract 1st (index = 0) subtitle

```bash
ffmpeg -i input.mkv \
  -map 0:s:0 \
  -c copy \
  subs.ass
```
