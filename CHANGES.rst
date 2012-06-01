Changelog of lizard-blockbox
===================================================


0.1 (unreleased)
----------------

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
