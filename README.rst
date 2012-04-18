lizard-blockbox
===============

Introduction
------------

Blockbox translates to 'Blokkendoos' in Dutch. 
Blokkendoos is the name of a Windows (VB) application written by one of our clients. 


What does it do? (short version)
--------------------------------

In The Netherlands, we have some large rivers such as the Maas and the IJssel. 
A bunch of measures can be taken to alter (improve) their characteristics.
Blokkendoos presents a list of measures which the user can apply on a river to see the effect they will have in a graph and on a map.

.. image:: http://i.imgur.com/C8F6p.png


Rewriting
---------

They asked Nelen & Schuurmans to 'port' this traditional desktop app to the web.

Porting, in this case, involves a lot more than you'd think:

 - Transition from desktop to client-server architecture.
 - An HTML interface, with IE7 compatibility as a must-have.
 - Keeping 'state' in a stateless environment (HTTP).
 - Data untangling.

At the same time, the map had to be added to the mix (it wasn't built into the original VB app)


Technologies used
-----------------

 - Django / Lizard as the base of the app
 - Backbone.js to structure the clientside coffeescript
 - Coffeescript to produce more readable code
 - OpenLayers, jQuery, Flot (for the graph)
 - FxCanvas for making Flot perform reasonably (instead of excanvas)