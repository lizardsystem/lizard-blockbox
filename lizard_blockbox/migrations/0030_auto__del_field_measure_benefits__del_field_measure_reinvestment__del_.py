# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Measure.benefits'
        db.delete_column('lizard_blockbox_measure', 'benefits')

        # Deleting field 'Measure.reinvestment'
        db.delete_column('lizard_blockbox_measure', 'reinvestment')

        # Deleting field 'Measure.damage'
        db.delete_column('lizard_blockbox_measure', 'damage')

        # Deleting field 'Measure.b_o_costs'
        db.delete_column('lizard_blockbox_measure', 'b_o_costs')

        # Deleting field 'Measure.quality_of_environment'
        db.delete_column('lizard_blockbox_measure', 'quality_of_environment')

        # Adding field 'Measure.life_costs'
        db.add_column('lizard_blockbox_measure', 'life_costs', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.investment_m2'
        db.add_column('lizard_blockbox_measure', 'investment_m2', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Measure.benefits'
        db.add_column('lizard_blockbox_measure', 'benefits', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.reinvestment'
        db.add_column('lizard_blockbox_measure', 'reinvestment', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.damage'
        db.add_column('lizard_blockbox_measure', 'damage', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'Measure.b_o_costs'
        db.add_column('lizard_blockbox_measure', 'b_o_costs', self.gf('lizard_blockbox.fields.EmptyStringFloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.quality_of_environment'
        db.add_column('lizard_blockbox_measure', 'quality_of_environment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Deleting field 'Measure.life_costs'
        db.delete_column('lizard_blockbox_measure', 'life_costs')

        # Deleting field 'Measure.investment_m2'
        db.delete_column('lizard_blockbox_measure', 'investment_m2')


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
            'exclude': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'exclude_rel_+'", 'null': 'True', 'to': "orm['lizard_blockbox.Measure']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'investment_m2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'km_from': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'km_to': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'life_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'measure_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mhw_profit_cm': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'mhw_profit_m2': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reach': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']", 'null': 'True', 'blank': 'True'}),
            'riverpart': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'total_costs': ('lizard_blockbox.fields.EmptyStringFloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'lizard_blockbox.namedreach': {
            'Meta': {'object_name': 'NamedReach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_blockbox.reach': {
            'Meta': {'object_name': 'Reach'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_blockbox.referencevalue': {
            'Meta': {'object_name': 'ReferenceValue'},
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
            'vertex': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Vertex']"})
        },
        'lizard_blockbox.waterleveldifference': {
            'Meta': {'object_name': 'WaterLevelDifference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_difference': ('django.db.models.fields.FloatField', [], {}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'reference_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.ReferenceValue']"}),
            'riversegment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.RiverSegment']"})
        }
    }

    complete_apps = ['lizard_blockbox']
