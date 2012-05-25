# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Measure.name'
        db.alter_column('lizard_blockbox_measure', 'name', self.gf('django.db.models.fields.TextField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Measure.name'
        db.alter_column('lizard_blockbox_measure', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))


    models = {
        'lizard_blockbox.floodingchance': {
            'Meta': {'object_name': 'FloodingChance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'lizard_blockbox.measure': {
            'Meta': {'ordering': "('km_from',)", 'object_name': 'Measure'},
            'b_o_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'benefits': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'damage': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'km_from': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'km_to': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'measure_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mhw_profit_cm': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'mhw_profit_m2': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'quality_of_environment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']", 'null': 'True', 'blank': 'True'}),
            'reinvestment': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'riverpart': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'total_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'})
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
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"})
        },
        'lizard_blockbox.riversegment': {
            'Meta': {'object_name': 'RiverSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.IntegerField', [], {}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']"}),
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
