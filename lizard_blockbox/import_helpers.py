"""Helper functions used by the data import management commands."""

import json
import os
import shutil
import subprocess

from django.conf import settings


class CommandError(Exception):
    def __init__(self, output, *args, **kwargs):
        self.output = output
        super(CommandError, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Error: " + self.output


def stripped_commands(commands):
    """Yield stripped lines, skipping empty lines."""
    for command in commands.split("\n"):
        command = command.strip()
        if command:
            yield command


def run_commands_in(data_dir, commands, shell=False):
    """Cd to data_dir, run the commands, return all output as one
    concatenated string, combing stdin and stderr. If a command fails,
    CommandError is raised, and the other commands won't run.
    _All_ the output, that of previous commands and also the output
    of the erratic command, is available as CommandError.output.
    """

    os.chdir(data_dir)

    output = ''
    try:
        for command in stripped_commands(commands):
            output += "Running {command}.\n".format(command=command)
            if not shell:
                command = command.split()
            output += subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                shell=shell)

        return output
    except subprocess.CalledProcessError as e:
        output += e.output
        raise CommandError(output=output)


def fetch_blockbox_data(stdout):
    DATA_DIR = os.path.join(settings.BUILDOUT_DIR, 'deltaportaal/data')

    # Note: stored user:password combination in deltaportaal's settings
    COMMANDS = """
rm -rf excelsheets factsheets geojson shapefiles
wget -nv -nH -r -N ftp://{ftp_credentials}@ftp.deltares.nl
""".format(ftp_credentials=settings.DELTARES_FTP_CREDENTIALS)

    stdout.write(run_commands_in(DATA_DIR, COMMANDS))
    stdout.write("Fetched blockbox data...\n")


def parse_shapes_blockbox(stdout):
    DATA_DIR = os.path.join(settings.BUILDOUT_DIR, 'deltaportaal/data')
    JSON_DIR = 'geojson'

    SHAPE_COMMAND = """
find ./shapefiles -name *.shp
"""

    RM_COMMANDS = """
rm -rf {jsondir}
mkdir {jsondir}
""".format(jsondir=JSON_DIR)

    shapes = [shape for shape in run_commands_in(
            DATA_DIR, SHAPE_COMMAND).split("\n")
              if shape]
    run_commands_in(
        DATA_DIR, RM_COMMANDS)

    output = ''
    for shape in shapes:
        json_file = os.path.join(
            JSON_DIR,
            os.path.basename(shape).replace('shp', 'json'))

        output += run_commands_in(DATA_DIR, """
ogr2ogr -f GeoJSON -s_srs EPSG:28992 -t_srs EPSG:900913 -simplify 0.05 {jsonfile} {shape}
""".format(jsonfile=json_file, shape=shape))

    stdout.write(output)
    stdout.write("Parsed blockbox geojson...\n")


def parse_kilometers_json(stdout):
    JSON_DIR = os.path.join(
        settings.BUILDOUT_DIR, 'deltaportaal/data/geojson')

    json_file = open(os.path.join(JSON_DIR, 'km_deltaportaal_tot.json'))
    json_data = json.load(json_file)
    for feature in json_data['features']:
        coordinates = feature['geometry']['coordinates']
        #Take first and last element.
        feature['geometry']['coordinates'] = [
            coordinates[0], coordinates[-1]]
        #Only have the properties we need.
        feature['properties'] = {'label': feature['properties']['label']}
    to_file = open(os.path.join(JSON_DIR, 'kilometers.json'), 'wb')
    json.dump(json_data, to_file)
    stdout.write("Parsed kilometers json...\n")


def merge_measures_blockbox(stdout):
    JSON_DIR = os.path.join(
        settings.BUILDOUT_DIR, 'deltaportaal/data/geojson')
    files = ('rivierengebied_totaal.json',)
    concat_measures = {'type': 'FeatureCollection',
                       'features': []}
    for filename in files:
        json_file = open(os.path.join(JSON_DIR, filename))
        features = json.load(json_file)['features']
        for feature in features:
            feature['properties'] = {
                'code': feature['properties']['code'],
                'titel': feature['properties']['maatregel']}
        concat_measures['features'] += features

    concat_json = open(os.path.join(JSON_DIR, 'measures.json'), 'wb')
    json.dump(concat_measures, concat_json)
    stdout.write("Merged blockbox measures...\n")


def copy_json_to_blockbox(stdout):
    JSON_DIR = os.path.join(
        settings.BUILDOUT_DIR, 'deltaportaal/data/geojson')

    shutil.copyfile(
        os.path.join(JSON_DIR, 'measures.json'),
        os.path.join(
            settings.BUILDOUT_DIR, 'deltaportaal',
            'static', 'lizard_blockbox', 'measures.json'))

    shutil.copyfile(
        os.path.join(JSON_DIR, 'kilometers.json'),
        os.path.join(
            settings.BUILDOUT_DIR, 'deltaportaal',
            'static', 'lizard_blockbox', 'kilometers.json'))
    stdout.write("Copied json to blockbox...\n")
