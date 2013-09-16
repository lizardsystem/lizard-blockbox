Changelog of lizard-blockbox
===================================================


0.21 (2013-09-16)
-----------------

- Set permissions to read all on factsheets.
  This way NGINX can serve the factsheets directly.


0.20.2 (2013-07-31)
-------------------

- A higher delay on screenshotter 100 ms wasn't enough.


0.20.1 (2013-07-24)
-------------------

- Fix unexpected indent.


0.20 (2013-07-24)
-----------------

- Add simplify functionality on shape.


0.19 (2013-07-17)
-----------------

- Remove bug where we checked if the file we were going to generate
  existed.

- Add link to the automatic import page from BlockboxView


0.18 (2013-07-09)
-----------------

- Fix bug where run_import command got confused by its own helpful
  extra output.


0.17 (2013-07-08)
-----------------

- Add a page for automatic imports, based on
  lizard-management-command-runner.


0.15 (2013-06-05)
-----------------

- Do not serve factsheets with a '+' in their name over
  X-Accel-Redirect, because Nginx always 404s on them.


0.14 (2013-06-03)
-----------------

- Fix bug with sorting measurement list if there are no measurements
  of type "Onbekend".


0.13 (2013-05-23)
-----------------

- Removed the UI control for the protection level, the protection
  level now depends on the chosen vertex. If the vertex has "1:250" in
  its name, that protection level is used, otherwise 1:1250.

- Only show the 1:250 strategy if selected river is "Onbedijkte Maas".

0.12 (2013-05-16)
-----------------

- It seems that not saving the session after setting things in it
  caused the PDF to be generated incorrectly.

- New text in possible strategies (i) hover text.

0.11 (2013-05-15)
-----------------

- Fix issue #34, table with measurements was empty in case an
  unexpected character in a measure's short_name caused reverse() to
  throw an exception.

- Fix issue #35, remove word 'mogelijke' from strategies in the
  template.

- Fix issue #37. We skipped importing the rest of the vertex sheet after
  seeing an empty column...


0.10 (2013-05-08)
-----------------

- Skip importing unused reach slug 'ST' (Steurgat)


0.9 (2013-05-03)
----------------

- Improved vertices selection. Vertices are now filtered on whether there are
  vertexvalues to be found for the selected year. For 2050, many vertices
  don't have values.

- Prevented js errors when no vertices could be found.

- Using compressor to ensure the blockbox.js is always refreshed.


0.8 (2013-05-02)
----------------

- Better error logging in xls import.

- Added "if undefined" to work around missing 'clip' variable if we're not
  using the flash canvas.


0.7 (2013-04-22)
----------------

- Removed now-unused ``the_geom`` field on riversegments. The geometry is
  loaded from a geojson file now.

- Added field for 'protection_level' on WaterLevelDifference.

- Using protection levels in the user interface and filtering water level
  differences on the chosen protection level (when applicable).

- Added field for 'year' on VertexValue.

- Changed the import_measure_xls script: if a row has six values instead of
  five, the sixth is assumed to contain the water level difference for the
  1:250 protection level.

- Removed unused ReferenceValue model.

- Changed the import_vertex_xls script: headers may now start with the year
  (2050 or 2100) followed by a :, and this year value will be saved with the
  VertexValue.  If no year is present, assume 2100.


0.6 (2013-03-28)
----------------

- Using different nginx-internal file path for factsheet file hosting. The
  old path conflicted with another deltaportaal config setting.


0.5 (2013-02-04)
----------------

- Add a small delay on the pdf image generation to get the graph right.


0.4 (2013-01-28)
----------------

- Use new screenshot service.


0.3 (2012-12-19)
----------------

- Remove water levels locations from csv export that don't have a water level.
  The csv export crashed when scenario was used that didn't define water levels
  for all kilometers in the reach.

0.2 (2012-12-13)
----------------

- Removed the sub-headers in the measure table, they don't work well with
  sorting. Instead there's a footer at the bottom now; this is sufficient for
  most tables. Otherwise it takes two days of work.

- Added CSV export.

- Fixed dimensions of the measures table.

- Added color to currently sorted column header.

- Changed legend label 'Hoekpunt' to 'MHW-opgave'.

- Removed whitespace from selected measures page.

- Showing start km in front of selected measures.

- Show investments costs of selected measures.

- Updated river level colors and measure colors.

- Improved CSV export as per request.

- Group selected measures bij reach (not final).

- Added selected strategy (vertex) to csv export.

- Moved total investment costs up in the sidebar.

- Reset selected vertex server side when selecting river.

- Don't choke in JS on missing data from ajax call.

- Just call for calculated measures result once per change.

- Delay first graph render after json call, not before.

- Reduced and optimized ajax calls.

- Added modal popup to say the site is loading (which is long in IE).

- Removed scroll bars from map in pdf export.

- Consistent sorting of selected measures in left sidebar.


0.1 (2012-06-01)
----------------

- Added legend for map layers.

- Requiring lizard-ui 4.0b4 because it include flot (and for some other
  changes). [Reinout]

- Protected all views with the "view blockbox" permission. You need to be the
  admin user now or you must have that permission (globally at the moment, so
  not via lizard-security's permission mapper).

- Added legend for Flot graphs in the right-hand sidebar. [Reinout]

- Added selected measures page, including a bookmarkable one. [Reinout]

- Added dynamic graph, a map with the measure locations and river
  results. [Gijs, Roland, Reinout]

- Added factsheets download support.

- Initial library skeleton created by nensskel.  [Roland]

- Made feature hover balloons pretty. [Berto]
