# WorldMint Games press kit

Built with [presskit.html](https://github.com/pixelnest/presskit.html) and deployed to https://worldmintgames.com by GitHub Pages on every push to `main`.

- `data/data.xml`: the company page. `data/images/` holds its header, logo and favicon.
- `data/penal-penguins/data.xml`: the game page. Every image in `data/penal-penguins/images/` shows in its gallery, except `header.*`, `logo*` and `favicon.ico`.
- `theme/dark.css` is presskit's dark theme in Times New Roman, recoloured to black, white and the game's interface orange (#e8631c).
- `npm run watch` serves a live preview at http://localhost:8080.

## Screenshots

`tools/capture_screenshots.gd` renders staged screenshots from the game. Copy it and its `.tscn` into the game project's `tools/` folder, then run:

```sh
~/Downloads/macos-g451-s162-gs4162-mp/GodotSteamMultiplayerPeer.app/Contents/MacOS/Godot \
  --path ~/blood-on-the-block --windowed --resolution 1920x1080 \
  res://tools/capture_screenshots.tscn -- <output folder> <shots.json>
```

Each shot in the JSON has a camera `position`, `target` and optional `fov`, plus `penguins` (position, face, color, pattern, blood, snow, limp) and `props` (scene, position). See the JSON files in `tools/`.

`tools/capture_logo.gd` renders the penguin headshot behind the Penal Penguins logo on a transparent background, the same way: run it once with `res://tools/capture_logo.tscn -- <bloody png>` and once with `-- <clean png> clean`. `python3 tools/compose_logo.py <bloody png> <clean png>` then pastes the clean eyes over the bloody ones, sets the penguin peeping over the "PP" lettering (Times New Roman Bold, with razor wire through it) and writes the logo and the game page favicon.
