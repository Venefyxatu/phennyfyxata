# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Writer'
        db.create_table('scores_writer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nick', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal('scores', ['Writer'])

        # Adding model 'War'
        db.create_table('scores_war', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('endtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('scores', ['War'])

        # Adding model 'ParticipantScore'
        db.create_table('scores_participantscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('writer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scores.Writer'])),
            ('war', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scores.War'])),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('scores', ['ParticipantScore'])


    def backwards(self, orm):
        # Deleting model 'Writer'
        db.delete_table('scores_writer')

        # Deleting model 'War'
        db.delete_table('scores_war')

        # Deleting model 'ParticipantScore'
        db.delete_table('scores_participantscore')


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
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'scores.writer': {
            'Meta': {'object_name': 'Writer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        }
    }

    complete_apps = ['scores']