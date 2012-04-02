# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RiverSegment'
        db.create_table('lizard_blockbox_riversegment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lizard_blockbox', ['RiverSegment'])

        # Adding model 'Scenario'
        db.create_table('lizard_blockbox_scenario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('lizard_blockbox', ['Scenario'])

        # Adding model 'Year'
        db.create_table('lizard_blockbox_year', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lizard_blockbox', ['Year'])

        # Adding model 'FloodingChance'
        db.create_table('lizard_blockbox_floodingchance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('lizard_blockbox', ['FloodingChance'])

        # Adding model 'Measure'
        db.create_table('lizard_blockbox_measure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_blockbox', ['Measure'])

        # Adding model 'Delta'
        db.create_table('lizard_blockbox_delta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('riversegment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.RiverSegment'])),
            ('measure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Measure'])),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Scenario'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Year'])),
            ('flooding_chance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.FloodingChance'])),
            ('delta', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4)),
        ))
        db.send_create_signal('lizard_blockbox', ['Delta'])

        # Adding model 'ReferenceValue'
        db.create_table('lizard_blockbox_referencevalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('riversegment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.RiverSegment'])),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Scenario'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Year'])),
            ('flooding_chance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.FloodingChance'])),
            ('reference', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4)),
            ('target', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4)),
        ))
        db.send_create_signal('lizard_blockbox', ['ReferenceValue'])


    def backwards(self, orm):
        
        # Deleting model 'RiverSegment'
        db.delete_table('lizard_blockbox_riversegment')

        # Deleting model 'Scenario'
        db.delete_table('lizard_blockbox_scenario')

        # Deleting model 'Year'
        db.delete_table('lizard_blockbox_year')

        # Deleting model 'FloodingChance'
        db.delete_table('lizard_blockbox_floodingchance')

        # Deleting model 'Measure'
        db.delete_table('lizard_blockbox_measure')

        # Deleting model 'Delta'
        db.delete_table('lizard_blockbox_delta')

        # Deleting model 'ReferenceValue'
        db.delete_table('lizard_blockbox_referencevalue')


    models = {
        'lizard_blockbox.delta': {
            'Meta': {'object_name': 'Delta'},
            'delta': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '4'}),
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Scenario']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Year']"})
        },
        'lizard_blockbox.floodingchance': {
            'Meta': {'object_name': 'FloodingChance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'lizard_blockbox.measure': {
            'Meta': {'object_name': 'Measure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.referencevalue': {
            'Meta': {'object_name': 'ReferenceValue'},
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '4'}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Scenario']"}),
            'target': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '4'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Year']"})
        },
        'lizard_blockbox.riversegment': {
            'Meta': {'object_name': 'RiverSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.IntegerField', [], {})
        },
        'lizard_blockbox.scenario': {
            'Meta': {'object_name': 'Scenario'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_blockbox.year': {
            'Meta': {'object_name': 'Year'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['lizard_blockbox']
