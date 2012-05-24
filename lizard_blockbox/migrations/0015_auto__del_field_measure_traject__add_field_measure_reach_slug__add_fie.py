# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Measure.traject'
        db.delete_column('lizard_blockbox_measure', 'traject')

        # Adding field 'Measure.reach_slug'
        db.add_column('lizard_blockbox_measure', 'reach_slug', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_blockbox.Reach'], null=True, blank=True), keep_default=False)

        # Adding field 'Measure.riverpart'
        db.add_column('lizard_blockbox_measure', 'riverpart', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'Measure.mwh_profit_cm'
        db.add_column('lizard_blockbox_measure', 'mwh_profit_cm', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.mhw_profit_m2'
        db.add_column('lizard_blockbox_measure', 'mhw_profit_m2', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.investment_costs'
        db.add_column('lizard_blockbox_measure', 'investment_costs', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.benefits'
        db.add_column('lizard_blockbox_measure', 'benefits', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.b_o_costs'
        db.add_column('lizard_blockbox_measure', 'b_o_costs', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.reinvestment'
        db.add_column('lizard_blockbox_measure', 'reinvestment', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.damage'
        db.add_column('lizard_blockbox_measure', 'damage', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'Measure.total_costs'
        db.add_column('lizard_blockbox_measure', 'total_costs', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Measure.quality_of_environment'
        db.add_column('lizard_blockbox_measure', 'quality_of_environment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Changing field 'Measure.km_from'
        db.alter_column('lizard_blockbox_measure', 'km_from', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Measure.km_to'
        db.alter_column('lizard_blockbox_measure', 'km_to', self.gf('django.db.models.fields.FloatField')(null=True))


    def backwards(self, orm):
        
        # Adding field 'Measure.traject'
        db.add_column('lizard_blockbox_measure', 'traject', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Deleting field 'Measure.reach_slug'
        db.delete_column('lizard_blockbox_measure', 'reach_slug_id')

        # Deleting field 'Measure.riverpart'
        db.delete_column('lizard_blockbox_measure', 'riverpart')

        # Deleting field 'Measure.mwh_profit_cm'
        db.delete_column('lizard_blockbox_measure', 'mwh_profit_cm')

        # Deleting field 'Measure.mhw_profit_m2'
        db.delete_column('lizard_blockbox_measure', 'mhw_profit_m2')

        # Deleting field 'Measure.investment_costs'
        db.delete_column('lizard_blockbox_measure', 'investment_costs')

        # Deleting field 'Measure.benefits'
        db.delete_column('lizard_blockbox_measure', 'benefits')

        # Deleting field 'Measure.b_o_costs'
        db.delete_column('lizard_blockbox_measure', 'b_o_costs')

        # Deleting field 'Measure.reinvestment'
        db.delete_column('lizard_blockbox_measure', 'reinvestment')

        # Deleting field 'Measure.damage'
        db.delete_column('lizard_blockbox_measure', 'damage')

        # Deleting field 'Measure.total_costs'
        db.delete_column('lizard_blockbox_measure', 'total_costs')

        # Deleting field 'Measure.quality_of_environment'
        db.delete_column('lizard_blockbox_measure', 'quality_of_environment')

        # Changing field 'Measure.km_from'
        db.alter_column('lizard_blockbox_measure', 'km_from', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Measure.km_to'
        db.alter_column('lizard_blockbox_measure', 'km_to', self.gf('django.db.models.fields.IntegerField')(null=True))


    models = {
        'lizard_blockbox.floodingchance': {
            'Meta': {'object_name': 'FloodingChance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'lizard_blockbox.measure': {
            'Meta': {'ordering': "('km_from',)", 'object_name': 'Measure'},
            'b_o_costs': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'benefits': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'damage': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_costs': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'km_from': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'km_to': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'measure_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mhw_profit_m2': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'mwh_profit_cm': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'quality_of_environment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'reach_slug': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Reach']", 'null': 'True', 'blank': 'True'}),
            'reinvestment': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'riverpart': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'total_costs': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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
