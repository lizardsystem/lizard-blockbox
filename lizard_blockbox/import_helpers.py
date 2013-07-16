"""Helper functions used by the data import management commands."""

import json
import os
import shutil
import subprocess

import xlrd

from django.db import transaction
from django.conf import settings

from lizard_blockbox import models
from lizard_blockbox import utils


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


def run_commands_in(data_dir, commands, shell=False, no_extra_output=False):
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
            if not no_extra_output:
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


# Fetch blockbox data command

def fetch_blockbox_data(stdout):
    DATA_DIR = os.path.join(settings.BUILDOUT_DIR, 'deltaportaal/data')

    # Note: stored user:password combination in deltaportaal's settings
    COMMANDS = """
rm -rf excelsheets factsheets geojson shapefiles
wget -nv -nH -r -N ftp://{ftp_credentials}@ftp.deltares.nl
""".format(ftp_credentials=settings.DELTARES_FTP_CREDENTIALS)

    stdout.write(run_commands_in(DATA_DIR, COMMANDS))
    stdout.write("Fetched blockbox data...\n")


# Parse shapes blockbox command

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
            DATA_DIR, SHAPE_COMMAND, no_extra_output=True).split("\n")
              if shape]
    run_commands_in(
        DATA_DIR, RM_COMMANDS)

    output = ''
    for shape in shapes:
        json_file = os.path.join(
            JSON_DIR,
            os.path.basename(shape).replace('shp', 'json'))

        output += run_commands_in(DATA_DIR, """
ogr2ogr -f GeoJSON -s_srs EPSG:28992 -t_srs EPSG:900913 {jsonfile} {shape}
""".format(jsonfile=json_file, shape=shape))
#         output += run_commands_in(DATA_DIR, """
# ogr2ogr -f GeoJSON -s_srs EPSG:28992 -t_srs EPSG:900913 -simplify 0.05 {jsonfile} {shape}
# """.format(jsonfile=json_file, shape=shape))

    stdout.write(output)
    stdout.write("Parsed blockbox geojson...\n")


# Parse kilometers json command

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


# Merge measures blockbox command

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


# Copy JSON to blockbox command

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


# Parse trajectory classification command

def parse_trajectory_classification_excelfile(excelpath, stdout):
    stdout.write("Parsing '{excel}'\n".format(excel=excelpath))
    wb = xlrd.open_workbook(excelpath)
    for sheet in wb.sheets():
        parse_trajectory_classification_sheet(sheet)


@transaction.commit_on_success
def parse_trajectory_classification_sheet(sheet):
    for row_nr in xrange(1, sheet.nrows):
        name, reach_slug, km_from, km_to = sheet.row_values(row_nr)
        km_from, km_to = int(km_from), int(km_to)
        reach, _ = models.Reach.objects.get_or_create(slug=reach_slug)
        named_reach, _ = models.NamedReach.objects.get_or_create(name=name)

        models.SubsetReach.objects.get_or_create(
            reach=reach,
            named_reach=named_reach,
            km_from=km_from,
            km_to=km_to)


# Import city names command

def import_city_names(excelpath, stdout):
    wb = xlrd.open_workbook(excelpath)
    for sheet in wb.sheets():
        import_city_names_sheet(sheet)


@transaction.commit_on_success
def import_city_names_sheet(sheet):
    for row_nr in xrange(1, sheet.nrows):
        km, city, reach_slug = sheet.row_values(row_nr)[:3]
        reach = models.Reach.objects.get(slug=reach_slug)
        models.CityLocation.objects.create(
            km=int(km), city=city, reach=reach)


# Import vertex xls command

def import_vertex_xls(excelpath, stdout):
    wb = xlrd.open_workbook(excelpath)
    for sheet in wb.sheets():
        import_vertex_sheet(sheet, stdout)


@transaction.commit_on_success
def import_vertex_sheet(sheet, stdout):
    # The first row (0) of the sheet contains irrelevant comments;
    # the first two columns are always location and reach. So
    # we're interested in the headers in the rest of the 2nd row:
    vertices = build_vertex_dict(sheet.row_values(1)[2:])

    # Then, for every row after the first two, import it
    for row_nr in xrange(2, sheet.nrows):
        import_vertex_row(vertices, sheet.row_values(row_nr))


def build_vertex_dict(row_values):
    vertices = []

    for vertex in row_values:
        vertex = vertex.strip()
        header = ''
        year = "2100"  # Let's use a default in case we don't find a year

        # The first part of the vertex should be the year
        if ':' in vertex:
            parts = vertex.split(':')
            first_part = parts[0].strip()
            if first_part in models.VertexValue.YEARS:
                year = first_part
                vertex = ':'.join(parts[1:]).strip()

        # Process the rest, which may contain a header
        if ':' in vertex:
            # A vertex can contain multiple colons, only the
            # first one is the header
            text = vertex.split(':')
            # The header and the vertex can contain superfluous spaces.
            header = text[0].strip()
            vertex = ':'.join(text[1:]).strip()
        instance, _ = models.Vertex.objects.get_or_create(
            header=header, name=vertex)

        instance.year = year  # Not saved on this model! But this is a
                              # convenient place to keep the variable
                              # around for below

        vertices.append(instance)

    return dict(enumerate(vertices, 2))


def import_vertex_row(vertices, row):
    # Skip unused slug 'ST' (Steurgat)
    if row[1].strip() == 'ST':
        return

    reach = models.Reach.objects.get(slug=row[1].strip())

    riversegment, _ = models.RiverSegment.objects.get_or_create(
        location=row[0], reach=reach)

    for col_nr, vertex in vertices.iteritems():
        value = row[col_nr]
        if not value:
            continue  # Skip this column, but there may still be data
                      # in later columns
        models.VertexValue.objects.get_or_create(
            riversegment=riversegment,
            vertex=vertex,
            year=vertex.year,  # Set the year we saved above
            defaults={'value': value})


def link_vertices_with_namedreaches():
    for named_reach in models.NamedReach.objects.all():
        rs = utils.namedreach2riversegments(named_reach)
        vertices = models.Vertex.objects.filter(
            vertexvalue__riversegment__in=rs).distinct()
        for vertex in vertices:
            vertex.named_reaches.add(named_reach)
            vertex.save()


# Import measure xls

def flush_database(stdout):
    # Delete all objects from models.
    stdout.write("Flushing measures.\n")
    for model in ('RiverSegment', 'Measure',
                  'WaterLevelDifference',
                  'Reach', 'NamedReach', 'SubsetReach',
                  'CityLocation', 'Vertex', 'VertexValue',
                  'Trajectory'):
        getattr(models, model).objects.all().delete()


def import_measure_xls(excelpath, stdout):
    stdout.write("Parsing measures from '{excel}'.\n"
                 .format(excel=excelpath))

    wb = xlrd.open_workbook(excelpath)
    for sheet in wb.sheets():
        import_measure_sheet(sheet, stdout)


@transaction.commit_on_success
def import_measure_sheet(sheet, stdout):
    short_name = sheet.name
    if isinstance(short_name, float):
        short_name = int(short_name)
    short_name = unicode(short_name).strip()
    measure, created = models.Measure.objects.get_or_create(
        short_name=short_name)

    if not created:
        # Measure exists.
        return
    for row_nr in xrange(1, sheet.nrows):
        import_measure_row(measure, sheet.row_values(row_nr), row_nr, stdout)


def import_measure_row(measure, row_values, rownr, stdout):
    # Row has either 5 or 6 values; make sure it has 6
    row_values = (tuple(row_values) + (None,))[:6]

    (location, _, _, difference, reach_slug, difference_250) =\
        row_values

    # Skip unused slug 'ST' (Steurgat)
    if reach_slug == 'ST':
        return

    try:
        reach = models.Reach.objects.get(slug=reach_slug)
    except models.Reach.DoesNotExist:
        raise ValueError("Reach with slug=%r not found" % reach_slug)

    # The Meuse has both North and South (Z) kilometers with the same
    # kilometer identifier.
    #XXX: ToDo 68_N > 68, 69_N > 68.5, 68_Z -> 69, 69_Z -> 69.5
    if isinstance(location, basestring):
        if not location.endswith('_N'):
            # Take only the North reaches for Now
            return
        else:
            location = float(location.strip('_N'))

    # We only use the values at integer kilometer marks
    if not location.is_integer():
        return

    try:
        riversegment = models.RiverSegment.objects.get(
            location=location, reach=reach)
    except models.RiverSegment.DoesNotExist:
        #print 'This location does not exist: %i %s' % (
        #    location, reach_slug)
        return

    try:
        difference = float(difference)
    except ValueError:
        raise ValueError(
            ("On line {rownr}, level difference '{difference}' is not "
             "a floating point number.")
            .format(rownr=rownr, difference=difference))

    models.WaterLevelDifference.objects.create(
        riversegment=riversegment,
        measure=measure,
        protection_level="1250",
        level_difference=difference)

    if difference_250:
        try:
            difference_250 = float(difference_250)
        except ValueError:
            raise ValueError(
                ("On line {rownr}, level difference '{difference}' is not "
                 "a floating point number.")
                .format(rownr=rownr, difference=difference_250))

        models.WaterLevelDifference.objects.create(
            riversegment=riversegment,
            measure=measure,
            protection_level="250",
            level_difference=difference_250)


# Import measure table xls

def import_measure_table_xls(excelpath, stdout):
    wb = xlrd.open_workbook(excelpath)
    for sheet in wb.sheets():
        import_measure_table_sheet(sheet, stdout)


@transaction.commit_on_success
def import_measure_table_sheet(sheet, stdout):
    col_names = (
        'name', 'short_name', 'measure_type', 'km_from', 'km_to',
        'reach', 'riverpart', 'mhw_profit_cm', 'mhw_profit_m2',
        'investment_costs', 'life_costs', 'total_costs', 'investment_m2')

    col_index = dict(zip(col_names, xrange(len(col_names))))

    for row_nr in xrange(1, sheet.nrows):
        row_values = sheet.row_values(row_nr)
        short_name = row_values[col_index['short_name']]

        if isinstance(short_name, float):
            # Integers are read as floats, so integerize them.
            row_values[col_index['short_name']] = int(short_name)

        default_values = dict(zip(col_names, row_values))
        default_values['reach'], _ = models.Reach.objects.get_or_create(
            slug=default_values['reach'])
        measure, _ = models.Measure.objects.get_or_create(
            short_name=row_values[col_index['short_name']])

        # km_from and km_to are integers.
        # DB save doesnt automatically converted '' to None.
        for item in ('km_from', 'km_to'):
            if default_values[item] == '':
                default_values[item] = None

        models.Measure.objects.filter(id=measure.id).update(
            **default_values)


# Import excluding measures command

def import_excluding_measures_xls(excelpath, stdout):
    wb = xlrd.open_workbook(excelpath)

    for sheet in wb.sheets():
        import_excluding_measures_sheet(sheet, stdout)


@transaction.commit_on_success
def import_excluding_measures_sheet(sheet, stdout):
    for row_nr in xrange(1, sheet.nrows):
        measure, excluding = sheet.row_values(row_nr)
        excludes = [i.strip() for i in unicode(excluding).split(';')]
        try:
            measure = models.Measure.objects.get(short_name=measure)
        except models.Measure.DoesNotExist:
            continue
        for exclude in excludes:
            try:
                instance = models.Measure.objects.get(short_name=exclude)
            except models.Measure.DoesNotExist:
                continue
            measure.exclude.add(instance)
            measure.save()


# Import trajectory names command

def import_trajectory_names_xls(excelpath, stdout):
    wb = xlrd.open_workbook(excelpath)

    for sheet in wb.sheets():
        import_trajectory_names_sheet(sheet, stdout)


def import_trajectory_names_sheet(sheet, stdout):
    for row_nr in xrange(1, sheet.nrows):
        _, reach_slugs, name = sheet.row_values(row_nr)
        reaches = reach_slugs.split(', ')

        tr, _ = models.Trajectory.objects.get_or_create(name=name)
        for reach_name in reaches:
            reach = models.Reach.objects.get(slug=reach_name.strip())
            tr.reach.add(reach)
            tr.save()
