# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WriterStats'
        db.create_table('scores_writerstats', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('warcount', self.gf('django.db.models.fields.IntegerField')()),
            ('wordcount', self.gf('django.db.models.fields.IntegerField')()),
            ('wpm', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('scores', ['WriterStats'])

        # Adding model 'WarParticipants'
        db.create_table('scores_warparticipants', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('war', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scores.War'])),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scores.Writer'])),
        ))
        db.send_create_signal('scores', ['WarParticipants'])

        # Adding field 'War.starttime'
        db.rename_column('scores_war', 'timestamp', 'starttime')

        # Adding field 'Writer.alias'
        db.add_column('scores_writer', 'alias',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scores.Writer'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'WriterStats'
        db.delete_table('scores_writerstats')

        # Deleting model 'WarParticipants'
        db.delete_table('scores_warparticipants')

        # Adding field 'War.timestamp'
        db.add_column('scores_war', 'timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(default=None),
                      keep_default=False)

        # Deleting field 'War.starttime'
        db.delete_column('scores_war', 'starttime')

        # Deleting field 'Writer.alias'
        db.delete_column('scores_writer', 'alias_id')


    models = {
        'scores.participantscore': {
            'Meta': {'object_name': 'ParticipantScore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'war': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scores.War']"}),
            'writer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scores.Writer']"})
        },
        'scores.war': {
            'Meta': {'object_name': 'War'},
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {})
        },
        'scores.warparticipants': {
            'Meta': {'object_name': 'WarParticipants'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scores.Writer']"}),
            'war': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scores.War']"})
        },
        'scores.writer': {
            'Meta': {'object_name': 'Writer'},
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scores.Writer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        },
        'scores.writerstats': {
            'Meta': {'object_name': 'WriterStats'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'warcount': ('django.db.models.fields.IntegerField', [], {}),
            'wordcount': ('django.db.models.fields.IntegerField', [], {}),
            'wpm': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        }
    }

    complete_apps = ['scores']
