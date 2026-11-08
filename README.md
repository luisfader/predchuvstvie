# Предчувствие 2.2

Роман Роберта Фадера с собственным саундтреком.

- `index.html` — читалка (оглавление, главы, плеер)
- `book.json` — название, описание, список глав
- `chapters/` — главы в Markdown
- `img/` — обложка и иллюстрации (JPG)
- `audio/` — саундтрек: MP3-файлы и `tracks.json`

## Саундтрек

`audio/tracks.json`:

```json
{"tracks":[
  {"file":"01-v-pustyne.mp3","title":"В пустыне","artist":"Luis Fader","chapters":["01.md"]}
]}
```

`chapters` — в каких главах трек включается автоматически.
