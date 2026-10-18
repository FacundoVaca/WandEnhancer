# House model generator

Builds `PZVoxelStudioViewpoint/common/media/voxel-studio/houses/` and
`package-houses.properties` from the game's own files.

Inputs (from a Project Zomboid 42 install, not in this repo):
`media/newtiledefinitions.tiles.txt`, `media/tileGeometry.txt`,
`media/texturepacks/Tiles2x.pack`.

Each model is the tile's `tileGeometry` shapes (boxes, cylinders, polygons),
or for a `WallObject` (posters, paintings) a plate on the wall it hangs on,
textured by projecting every vertex back onto the tile's 2x isometric sprite.

1. `python3 parse_tiles.py tiles.json`
2. `python3 -c "import geom,json;json.dump(geom.parse('tileGeometry.txt'),open('geom.json','w'))"`
3. Build `bound.txt` (sprites already bound by the manifests) and
   `candidates.json`, then `python3 build_houses.py`.
