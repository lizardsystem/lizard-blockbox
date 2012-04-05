# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'ReferenceValue', fields ['flooding_chance', 'riversegment', 'scenario', 'year']
        db.delete_unique('lizard_blockbox_referencevalue', ['flooding_chance_id', 'riversegment_id', 'scenario_id', 'year_id'])

        # Adding field 'RiverSegment.x'
        db.add_column('lizard_blockbox_riversegment', 'x', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'RiverSegment.y'
        db.add_column('lizard_blockbox_riversegment', 'y', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'RiverSegment.x'
        db.delete_column('lizard_blockbox_riversegment', 'x')

        # Deleting field 'RiverSegment.y'
        db.delete_column('lizard_blockbox_riversegment', 'y')

        # Adding unique constraint on 'ReferenceValue', fields ['flooding_chance', 'riversegment', 'scenario', 'year']
        db.create_unique('lizard_blockbox_referencevalue', ['flooding_chance_id', 'riversegment_id', 'scenario_id', 'year_id'])


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
            'Meta': {'object_name': 'ReferenceValue'},
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
            'location': ('django.db.models.fields.IntegerField', [], {}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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
