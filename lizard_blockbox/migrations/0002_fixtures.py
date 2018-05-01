# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-01 13:41
from __future__ import unicode_literals

import os

from django.db import migrations
from django.core import serializers

fixture_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../fixtures'))


def load_map_fixtures(apps, schema_editor):
    filename = os.path.join(fixture_path, 'lizard_map.json')

    with open(filename, 'rb') as fixture:
        for obj in serializers.deserialize('json', fixture):
            obj.save()


def remove_maps(apps, schema_editor):
    backgroundmap = apps.get_model("lizard_map", "backgroundmap")
    backgroundmap.objects.all().delete()

    setting = apps.get_model("lizard_map", "setting")
    setting.objects.all().delete()


def load_mgmt_fixtures(apps, schema_editor):
    filename = os.path.join(fixture_path, 'lizard_management_command_runner.json')

    with open(filename, 'rb') as fixture:
        for obj in serializers.deserialize('json', fixture):
            obj.save()

def remove_mgmt(apps, schema_editor):
    managementcommand = apps.get_model("lizard_management_command_runner", "managementcommand")
    managementcommand.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('lizard_blockbox', '0001_initial'),
        ('lizard_map', '0001_initial'),
        ('lizard_management_command_runner', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_map_fixtures, remove_maps),
        migrations.RunPython(load_mgmt_fixtures, remove_mgmt),
    ]
