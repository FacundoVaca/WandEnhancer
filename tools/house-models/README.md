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

## Every other missing sprite

`build_all.py` (also needs `tileDepthTextureAssignments.txt` and
`Tiles1x.pack`) walks every sprite in the tile definitions and in
`Tiles2x.pack` that no manifest binds yet, and writes `generated/` plus
`package-generated-*.properties`:

- its own `tileGeometry` shapes;
- a plate on the wall it hangs on (`attachedN/W/S/E`);
- the geometry of the tile whose depth art it borrows;
- otherwise two crossed upright planes carrying its art.

Lit `_on` sprites are bound to their unlit sprite's model instead. Walls,
roofs, floors, doors, windows and fences are skipped: Viewpoint and its
companion mods draw those.
