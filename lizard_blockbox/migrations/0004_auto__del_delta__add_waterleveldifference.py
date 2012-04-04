# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Delta'
        db.delete_table('lizard_blockbox_delta')

        # Adding model 'WaterLevelDifference'
        db.create_table('lizard_blockbox_waterleveldifference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('riversegment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.RiverSegment'])),
            ('measure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Measure'])),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Scenario'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Year'])),
            ('flooding_chance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.FloodingChance'])),
            ('reference_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.ReferenceValue'])),
            ('level_difference', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('lizard_blockbox', ['WaterLevelDifference'])


    def backwards(self, orm):
        
        # Adding model 'Delta'
        db.create_table('lizard_blockbox_delta', (
            ('reference_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.ReferenceValue'])),
            ('riversegment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.RiverSegment'])),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Scenario'])),
            ('delta', self.gf('django.db.models.fields.FloatField')()),
            ('flooding_chance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.FloodingChance'])),
            ('measure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Measure'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Year'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('lizard_blockbox', ['Delta'])

        # Deleting model 'WaterLevelDifference'
        db.delete_table('lizard_blockbox_waterleveldifference')


    models = {
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
        'lizard_blockbox.reach': {
            'Meta': {'object_name': 'Reach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_blockbox.referencevalue': {
            'Meta': {'unique_together': "(('riversegment', 'scenario', 'year', 'flooding_chance'),)", 'object_name': 'ReferenceValue'},
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.FloatField', [], {}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Scenario']"}),
            'target': ('django.db.models.fields.FloatField', [], {}),
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
        'lizard_blockbox.waterleveldifference': {
            'Meta': {'object_name': 'WaterLevelDifference'},
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_difference': ('django.db.models.fields.FloatField', [], {}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'reference_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.ReferenceValue']"}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Scenario']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Year']"})
        },
        'lizard_blockbox.year': {
            'Meta': {'object_name': 'Year'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['lizard_blockbox']
