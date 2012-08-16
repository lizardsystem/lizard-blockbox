Changelog of lizard-blockbox
===================================================


0.2 (unreleased)
----------------

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
