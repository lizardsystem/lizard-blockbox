# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'ReferenceValue.reference'
        db.alter_column('lizard_blockbox_referencevalue', 'reference', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'ReferenceValue.target'
        db.alter_column('lizard_blockbox_referencevalue', 'target', self.gf('django.db.models.fields.FloatField')())

        # Adding unique constraint on 'ReferenceValue', fields ['flooding_chance', 'riversegment', 'scenario', 'year']
        db.create_unique('lizard_blockbox_referencevalue', ['flooding_chance_id', 'riversegment_id', 'scenario_id', 'year_id'])

        # Adding field 'Delta.reference_value'
        db.add_column('lizard_blockbox_delta', 'reference_value', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['lizard_blockbox.ReferenceValue']), keep_default=False)

        # Changing field 'Delta.delta'
        db.alter_column('lizard_blockbox_delta', 'delta', self.gf('django.db.models.fields.FloatField')())


    def backwards(self, orm):
        
        # Removing unique constraint on 'ReferenceValue', fields ['flooding_chance', 'riversegment', 'scenario', 'year']
        db.delete_unique('lizard_blockbox_referencevalue', ['flooding_chance_id', 'riversegment_id', 'scenario_id', 'year_id'])

        # Changing field 'ReferenceValue.reference'
        db.alter_column('lizard_blockbox_referencevalue', 'reference', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4))

        # Changing field 'ReferenceValue.target'
        db.alter_column('lizard_blockbox_referencevalue', 'target', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4))

        # Deleting field 'Delta.reference_value'
        db.delete_column('lizard_blockbox_delta', 'reference_value_id')

        # Changing field 'Delta.delta'
        db.alter_column('lizard_blockbox_delta', 'delta', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=4))


    models = {
        'lizard_blockbox.delta': {
            'Meta': {'object_name': 'Delta'},
            'delta': ('django.db.models.fields.FloatField', [], {}),
            'flooding_chance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.FloodingChance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.Measure']"}),
            'reference_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_blockbox.ReferenceValue']"}),
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
        'lizard_blockbox.year': {
            'Meta': {'object_name': 'Year'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['lizard_blockbox']
