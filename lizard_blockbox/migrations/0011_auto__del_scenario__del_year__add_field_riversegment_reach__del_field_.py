# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Scenario'
        db.delete_table('lizard_blockbox_scenario')

        # Deleting model 'Year'
        db.delete_table('lizard_blockbox_year')

        # Adding field 'RiverSegment.reach'
        db.add_column('lizard_blockbox_riversegment', 'reach', self.gf('django.db.models.fields.CharField')(default='MA', max_length=100), keep_default=False)

        # Deleting field 'ReferenceValue.year'
        db.delete_column('lizard_blockbox_referencevalue', 'year_id')

        # Deleting field 'ReferenceValue.scenario'
        db.delete_column('lizard_blockbox_referencevalue', 'scenario_id')

        # Deleting field 'WaterLevelDifference.scenario'
        db.delete_column('lizard_blockbox_waterleveldifference', 'scenario_id')

        # Deleting field 'WaterLevelDifference.year'
        db.delete_column('lizard_blockbox_waterleveldifference', 'year_id')


    def backwards(self, orm):
        
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

        # Deleting field 'RiverSegment.reach'
        db.delete_column('lizard_blockbox_riversegment', 'reach')

        # User chose to not deal with backwards NULL issues for 'ReferenceValue.year'
        raise RuntimeError("Cannot reverse this migration. 'ReferenceValue.year' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ReferenceValue.scenario'
        raise RuntimeError("Cannot reverse this migration. 'ReferenceValue.scenario' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'WaterLevelDifference.scenario'
        raise RuntimeError("Cannot reverse this migration. 'WaterLevelDifference.scenario' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'WaterLevelDifference.year'
        raise RuntimeError("Cannot reverse this migration. 'WaterLevelDifference.year' and its values cannot be restored.")


    models = {
        'lizard_blockbox.floodingchance': {
            'Meta': {'object_name': 'FloodingChance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'lizard_blockbox.measure': {
            'Meta': {'ordering': "('km_from',)", 'object_name': 'Measure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'km_from': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'km_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'measure_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'traject': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
            'target': ('django.db.models.fields.FloatField', [], {})
        },
        'lizard_blockbox.riversegment': {
            'Meta': {'object_name': 'RiverSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.IntegerField', [], {}),
            'reach': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'the_geom': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.waterleveldifference': {
            'Meta': {'object_name': 'WaterLevelDifference'},
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_difference': ('django.db.models.fields.FloatField', [], {}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'reference_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.ReferenceValue']"}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"})
        }
    }

    complete_apps = ['lizard_blockbox']
