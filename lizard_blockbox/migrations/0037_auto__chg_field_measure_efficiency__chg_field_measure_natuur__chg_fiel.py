# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Measure.efficiency'
        db.alter_column('lizard_blockbox_measure', 'efficiency', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Measure.natuur'
        db.alter_column('lizard_blockbox_measure', 'natuur', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Measure.grondverzet'
        db.alter_column('lizard_blockbox_measure', 'grondverzet', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Measure.efficiency'
        db.alter_column('lizard_blockbox_measure', 'efficiency', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True))

        # Changing field 'Measure.natuur'
        db.alter_column('lizard_blockbox_measure', 'natuur', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True))

        # Changing field 'Measure.grondverzet'
        db.alter_column('lizard_blockbox_measure', 'grondverzet', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True))

    models = {
        'lizard_blockbox.citylocation': {
            'Meta': {'object_name': 'CityLocation'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'km': ('django.db.models.fields.IntegerField', [], {}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']"})
        },
        'lizard_blockbox.measure': {
            'Meta': {'ordering': "('km_from',)", 'object_name': 'Measure'},
            'efficiency': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'exclude': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'exclude_rel_+'", 'null': 'True', 'to': "orm['lizard_blockbox.Measure']"}),
            'grondverzet': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_costs': ('lizard_blockbox.fields.EmptyStringUnknownFloatField', [], {'null': 'True', 'blank': 'True'}),
            'km_from': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'km_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maximal_investment_costs': ('lizard_blockbox.fields.EmptyStringUnknownFloatField', [], {'null': 'True', 'blank': 'True'}),
            'measure_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mhw_profit_cm': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'mhw_profit_m2': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'minimal_investment_costs': ('lizard_blockbox.fields.EmptyStringUnknownFloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'natuur': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']", 'null': 'True', 'blank': 'True'}),
            'riverpart': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.namedreach': {
            'Meta': {'object_name': 'NamedReach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_blockbox.reach': {
            'Meta': {'ordering': "('number',)", 'object_name': 'Reach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'lizard_blockbox.riversegment': {
            'Meta': {'object_name': 'RiverSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.IntegerField', [], {}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']"})
        },
        'lizard_blockbox.subsetreach': {
            'Meta': {'object_name': 'SubsetReach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'km_from': ('django.db.models.fields.IntegerField', [], {}),
            'km_to': ('django.db.models.fields.IntegerField', [], {}),
            'named_reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.NamedReach']"}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']"})
        },
        'lizard_blockbox.trajectory': {
            'Meta': {'object_name': 'Trajectory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'reach': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_blockbox.Reach']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.vertex': {
            'Meta': {'object_name': 'Vertex'},
            'header': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'named_reaches': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_blockbox.NamedReach']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.vertexvalue': {
            'Meta': {'object_name': 'VertexValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'vertex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Vertex']"}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'2100'", 'max_length': '4'})
        },
        'lizard_blockbox.waterleveldifference': {
            'Meta': {'object_name': 'WaterLevelDifference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_difference': ('django.db.models.fields.FloatField', [], {}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'protection_level': ('django.db.models.fields.CharField', [], {'default': "'1250'", 'max_length': '4'}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"})
        }
    }

    complete_apps = ['lizard_blockbox']