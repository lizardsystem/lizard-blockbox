# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from cgi import escape
from collections import defaultdict
from datetime import datetime
from hashlib import md5
import StringIO
import csv
import logging
import operator
import os
import urllib
import urlparse

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic.base import RedirectView
from django.views.static import serve
from lizard_map.lizard_widgets import Legend
from lizard_map.views import MapView
from lizard_ui.layout import Action
from lizard_ui.models import ApplicationIcon
from lizard_ui.views import UiView
from xhtml2pdf import pisa

from lizard_management_command_runner.models import ManagementCommand
from lizard_management_command_runner import tasks

from lizard_blockbox import models
from lizard_blockbox.utils import namedreach2riversegments, namedreach2measures
from lizard_blockbox.utils import UnicodeWriter


SELECTED_MEASURES_KEY = 'selected_measures_key'
VIEW_PERM = 'lizard_blockbox.can_view_blockbox'
YEAR_SESSION_KEY = 'blockbox_year'
logger = logging.getLogger(__name__)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode("ISO-8859-1")), result)

    if pdf.err:
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=blokkendoos-report.pdf'
    response.write(result.getvalue())
    return response


def generate_report(request, template='lizard_blockbox/report.html'):
    """
    Uses PISA to generate a PDF report
    """

    measures = models.Measure.objects.filter(
        short_name__in=_selected_measures(request))

    measures_header = []
    if measures.count() != 0:
        measures_header = [field['label'] for field in measures[0].pretty()
                           if field['label'] != 'Riviertak']
    total_cost = {
        'minimal': 0.0,
        'maximal': 0.0,
        'expected': 0.0
        }

    reaches = defaultdict(list)

    for measure in measures:
        if measure.reach:
            try:
                trajectory = measure.reach.trajectory_set.get()
            except (measure.reach.DoesNotExist,
                    measure.reach.MultipleObjectsReturned):
                reach_name = measure.reach.slug
            else:
                reach_name = trajectory.name
        else:
            reach_name = 'unknown'
        measure_p = [i for i in measure.pretty() if i['label'] != 'Riviertak']
        reaches[reach_name].append(measure_p)

        total_cost['minimal'] += measure.minimal_investment_costs or 0.0
        total_cost['maximal'] += measure.maximal_investment_costs or 0.0
        total_cost['expected'] += measure.investment_costs or 0.0
    result = []
    for name, measures in reaches.items():
        reach = {'name': name,
                 'amount': len(measures),
                 'measures': measures}
        result.append(reach)
    result.sort(key=lambda x: x['amount'], reverse=True)

    # Build the graph map url
    session = request.session
    querystring = dict((i, session['map_location'][i]) for i in
                        ('top', 'bottom', 'left', 'right'))
    querystring['vertex'] = session['vertex']
    querystring['river'] = session['river']
    querystring['selected_year'] = _selected_year(request)
    querystring['measures'] = ';'.join(session[SELECTED_MEASURES_KEY])
    querystring = urllib.urlencode(querystring)
    path = reverse('lizard_blockbox.plain_graph_map')
    domain = Site.objects.get_current().domain
    if hasattr(settings, 'BLOCKBOX_DOMAIN_PREFIX'):
        domain = settings.BLOCKBOX_DOMAIN_PREFIX + domain

    graph_map_url = urlparse.urlunparse(('http', domain, path, '',
                                         querystring, ''))

    graph_map_url = urllib.urlencode({'url': graph_map_url,
                                      'width': 1280,
                                      'height': 800,
                                      'delay': 500})
    image_url = urlparse.urlunparse(('http', 'screenshotter.lizard.net/', '',
                                     '', graph_map_url, ''))
    logger.info(image_url)

    return render_to_pdf(
        'lizard_blockbox/report.html',
        {'date': datetime.now(),
         'image_url': image_url,
         'pagesize': 'A4',
         'reaches': result,
         'measures_header': measures_header,
         'total_cost': total_cost})


def generate_csv(request):
    response = HttpResponse(mimetype='application/csv')
    response['Content-Disposition'] = 'filename=blokkendoos-report.csv'
    writer = UnicodeWriter(response, dialect='excel', delimiter=';',
                           quoting=csv.QUOTE_ALL)

    writer.writerow(['Titel', 'Code', 'Type', 'Km van', 'Km tot', 'Riviertak',
                     'Rivierdeel', 'MHW winst m', 'MHW winst m2',
                     'Minimale investeringskosten (ME)',
                     'Investeringskosten (ME)',
                     'Maximale investeringskosten (ME)'])
    measures = models.Measure.objects.filter(
        short_name__in=_selected_measures(request))

    summed_minimal_investment_costs = 0.0
    summed_maximal_investment_costs = 0.0
    summed_investment_costs = 0.0

    def floatf(f):
        if f is None:
            return "Onbekend"
        return "{:.1f}".format(f)

    for measure in measures:
        # mhw_profit_cm must be a number not None
        mhw_profit_cm = measure.mhw_profit_cm or 0.0

        writer.writerow([measure.name, measure.short_name,
                         measure.measure_type, measure.km_from, measure.km_to,
                         measure.reach, measure.riverpart,
                         floatf(mhw_profit_cm / 100),
                         floatf(measure.mhw_profit_m2),
                         floatf(measure.minimal_investment_costs),
                         floatf(measure.investment_costs),
                         floatf(measure.maximal_investment_costs)])

        summed_minimal_investment_costs += (
            measure.minimal_investment_costs or 0)
        summed_maximal_investment_costs += (
            measure.maximal_investment_costs or 0)
        summed_investment_costs += (
            measure.investment_costs or 0)

    writer.writerow([''] * 9 + ['Totaal:'] * 3)
    writer.writerow([''] * 9 + [
            floatf(summed_minimal_investment_costs),
            floatf(summed_investment_costs),
            floatf(summed_maximal_investment_costs)])

    selected_vertex = _selected_vertex(request)
    selected_year = _selected_year(request)
    selected_protection_level = _selected_protection_level(selected_vertex)
    writer.writerow(['Strategie:', selected_vertex.name])
    writer.writerow(['Geselecteerd zichtjaar:', selected_year])
    writer.writerow(['Geselecteerd beschermingsniveau:',
                     '1 / %s' % selected_protection_level])

    writer.writerow([])
    fieldnames = [_('reach'), _('reach kilometer'),
                  _('remaining water level rise in m')]
    writer.writerow(fieldnames)

    # Get the segments in the trajectory in with the selected river is.
    river = _selected_river(request)

    # Expand using the 'hoofdtrajecten' list
    reaches = models.NamedReach.objects.get(name=river
                                          ).expanded_reaches()

    segments = models.RiverSegment.objects.filter(reach__in=reaches
                                                  ).order_by('location')

    water_levels = (_segment_level(segment, measures, selected_vertex,
                                   selected_year, selected_protection_level)
                    for segment in segments)
    water_levels = (level for level in water_levels if level is not None)

    for water_level in water_levels:
        writer.writerow([water_level['location_segment'],
                         water_level['location'],
                         water_level['measures_level'],
                         ])
    return response


class BlockboxView(MapView):
    """Show reach including pointers to relevant data URLs."""
    template_name = 'lizard_blockbox/blockbox.html'
    edit_link = '/admin/lizard_blockbox/'
    required_permission = VIEW_PERM
    # We don't want empty popups, so disable it.
    javascript_click_handler = ''

    @property
    def content_actions(self):
        actions = super(BlockboxView, self).content_actions
        to_table_text = _('Show table')
        to_map_text = _('Show map')
        switch_map_and_table = Action(
            name=to_table_text,
            description=_('Switch between a graph+map view and a graph+table '
                          'view.'),
            icon='icon-random',
            url='#table',
            data_attributes={'to-table-text': to_table_text,
                             'to-map-text': to_map_text},
            klass='toggle_map_and_table')
        actions.insert(0, switch_map_and_table)

        if self.request.user.has_perm(
            'lizard_management_command_runner.execute_managementcommand'):
            actions.insert(0, Action(
                    name=_("Import data"),
                    description=_(
                        "Page for automatically importing the blockbox data"),
                    icon='icon-download-alt',
                    url=reverse('lizard_blockbox.automatic_import')))

        return actions

    @property
    def site_actions(self):
        actions = super(BlockboxView, self).site_actions
        index = len(getattr(settings, 'UI_SITE_ACTIONS', [])) - 1
        url = settings.STATIC_URL + 'lizard_blockbox/manual.pdf'
        action = Action(
            name=_('How does the "block box" work?'),
            description=_('''A short manual may be found
                <a href="{}" target="_blank">here</a>
                (in Dutch).'''.format(url)),
            icon='icon-info-sign',
            klass='has_clickover_south'
        )
        actions.insert(index, action)
        return actions

    def reaches(self):
        reaches = models.NamedReach.objects.all().values('name')
        selected_river = _selected_river(self.request)
        for reach in reaches:
            if reach['name'] == selected_river:
                reach['selected'] = True
        return reaches

    @property
    def selected_year(self):
        return _selected_year(self.request)

    def measures_per_reach(self):
        """Return selected measures, sorted per reach."""
        selected_measures = _selected_measures(self.request)
        reaches = defaultdict(list)
        measures = models.Measure.objects.filter(
            short_name__in=selected_measures)

        for measure in measures:
            if measure.reach:
                try:
                    trajectory = measure.reach.trajectory_set.get()
                except measure.reach.DoesNotExist, \
                        measure.reach.MultipleObjectsReturned:
                    reach_name = measure.reach.slug
                else:
                    reach_name = trajectory.name
            else:
                reach_name = 'unknown'
            reaches[reach_name].append(measure)
        result = []
        # print models.Measure._meta.fields
        for name, measures in reaches.items():
            measures.sort(key=lambda x: x.km_from)
            reach = {'name': name,
                     'amount': len(measures),
                     'measures': measures}
            result.append(reach)
        result.sort(key=lambda x: x['name'])
        return result

    def investment_costs(self):
        return _investment_costs(self.request)

    def measure_headers(self):
        """Return headers for measures table."""
        measure = models.Measure.objects.all()[0]
        return [field['label'] for field in measure.pretty()]

    def measures(self):
        measures_ids = namedreach2measures(_selected_river(self.request))
        measures = models.Measure.objects.filter(short_name__in=measures_ids)
        selected_measures = _selected_measures(self.request)
        available_factsheets = _available_factsheets()
        # selected_river = _selected_river(self.request)
        result = []
        for measure_obj in measures:
            measure = {}
            measure['fields'] = measure_obj.pretty()
            measure['selected'] = measure_obj.short_name in selected_measures
            measure['name'] = unicode(measure_obj)
            measure['short_name'] = measure_obj.short_name
            if measure_obj.short_name in available_factsheets:
                try:
                    # This reverse() can fail due to unexpected
                    # characters in short_name, in that case we don't
                    # show a PDF link
                    measure['pdf_link'] = reverse(
                        'measure_factsheet',
                        kwargs={'measure': measure_obj.short_name})
                except NoReverseMatch:
                    measure['pdf_link'] = None
            result.append(measure)

        return result

    @property
    def legends(self):
        result_graph_legend = FlotLegend(
            name="Effecten grafiek",
            div_id='measure_results_graph_legend')
        all_types = models.Measure.objects.all().values_list(
            'measure_type', flat=True)
        labels = []
        for measure_type in set(all_types):
            if measure_type is None:
                labels.append(['x', 'Onbekend'])
            else:
                labels.append([measure_type[0].lower(), measure_type])
        labels.sort()
        measures_legend = FlotLegend(
            name="Maatregelselectie grafiek",
            div_id='measures_legend',
            labels=labels)

        labels = [
            # text, level
            ['> 2.00', 'riverlevel-9'],
            ['1.00 - 2.00', 'riverlevel-8'],
            ['0.80 - 1.00', 'riverlevel-7'],
            ['0.60 - 0.80', 'riverlevel-6'],
            ['0.40 - 0.60', 'riverlevel-5'],
            ['0.20 - 0.40', 'riverlevel-4'],
            ['0.00 - 0.20', 'riverlevel-3'],
            ['-0.20 - -0.00', 'riverlevel-2'],
            ['-0.40 - -0.20', 'riverlevel-1'],
            ['< -0.40', 'riverlevel-0']
            ]
        map_measure_results_legend = MapLayerLegend(
            name="Rivieren (kaart)",
            labels=labels)

        labels = [
            # text, color
            ['Niet geselecteerd', 'measure'],
            ['Geselecteerd', 'selected-measure'],
        ]
        selected_measures_map_legend = MapLayerLegend(
            name="Maatregelen (kaart)",
            labels=labels)

        result = [result_graph_legend, measures_legend,
                  map_measure_results_legend,
                  selected_measures_map_legend]
        result += super(BlockboxView, self).legends
        return result


class PlainGraphMapView(BlockboxView):
    required_permission = None
    template_name = 'lizard_blockbox/report_map_template.html'
    # Don't show the login modal for a pdf.
    modal_for_pdf_view = True

    def get_context_data(self, **kwargs):
        # Parse QueryString
        session = self.request.session
        measures = set(self.request.GET.get('measures').split(';'))
        session[SELECTED_MEASURES_KEY] = measures
        session['vertex'] = self.request.GET.get('vertex')
        session[YEAR_SESSION_KEY] = self.request.GET.get(
            'selected_year', '2100')
        session['river'] = self.request.GET.get('river')
        session['map_location'] = dict((i, self.request.GET.get(i))
            for i in ('top', 'bottom', 'left', 'right'))
        session.save()
        return super(PlainGraphMapView, self).get_context_data(**kwargs)


class FlotLegend(Legend):
    """UI widget for a flot graph legend."""
    template_name = 'lizard_blockbox/flot_legend_item.html'
    div_id = None
    labels = {}  # Only used for label explanation of y axis measure kinds.


class MapLayerLegend(Legend):
    """UI widget for a json map layer legend."""
    template_name = 'lizard_blockbox/map_layer_legend_item.html'
    labels = []


class SelectedMeasuresView(UiView):
    """Show info on the selected measures."""
    template_name = 'lizard_blockbox/selected_measures.html'
    required_permission = VIEW_PERM
    page_title = "Geselecteerde blokkendoos maatregelen"

    def selected_names(self):
        """Return set of selected measures from session."""
        return _selected_measures(self.request)

    def measures_per_reach(self):
        """Return selected measures, sorted per reach."""
        reaches = defaultdict(list)
        measures = models.Measure.objects.filter(
            short_name__in=self.selected_names())

        for measure in measures:
            if measure.reach:
                reach_name = measure.reach.slug
            else:
                reach_name = 'unknown'
            reaches[reach_name].append(measure)
        result = []
        # print models.Measure._meta.fields
        for name, measures in reaches.items():
            reach = {'name': name,
                     'amount': len(measures),
                     'measures': measures}
            result.append(reach)
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    @property
    def to_bookmark_url(self):
        """Return URL with the selected measures stored in the URL."""
        short_names = sorted(list(self.selected_names()))
        selected = ';'.join(short_names)
        url = reverse('lizard_blockbox.bookmarked_measures',
                      kwargs={'selected': selected})
        return url

    @property
    def breadcrumbs(self):
        result = super(SelectedMeasuresView, self).breadcrumbs
        result.append(Action(name=self.page_title))
        return result


class BookmarkedMeasuresView(RedirectView):
    """Show info on the measures as selected by the URL."""
    permanent = False

    def get_redirect_url(self, **kwargs):
        semicolon_separated = self.kwargs['selected']
        short_names = set(semicolon_separated.split(';'))
        # put them on the session
        self.request.session[SELECTED_MEASURES_KEY] = short_names
        return reverse('lizard_blockbox.home')


@permission_required(VIEW_PERM)
def fetch_factsheet(request, measure):
    """Return download header for nginx to serve pdf file."""

    # ToDo: Better security model based on views...
    if not ApplicationIcon.objects.filter(url__startswith='/blokkendoos'):
        # ToDo: Change to 403 with templates
        raise Http404

    if not measure in _available_factsheets():
        # There is no factsheet for this measure
        raise Http404

    if '+' in measure:
        # Nginx fails to serve files with a '+' in their name. Encoding
        # the '+' doesn't work, because there is an Nginx issue that says
        # it doesn't decode X-Accel-Redirect paths.
        # In short, we just do these ourselves...
        # XXX
        filepath = os.path.join(
            settings.BUILDOUT_DIR, 'deltaportaal', 'data', 'factsheets',
            '{measure}.pdf'.format(measure=measure))
        return serve(request, filepath, '/')

    response = HttpResponse()
    response['X-Accel-Redirect'] = '/factsheets/%s.pdf' % measure
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % measure
    # content-type is set in nginx.
    response['Content-Type'] = ''
    return response


def _available_factsheets():
    """Return a list of the available factsheets."""

    cache_key = 'available_factsheets'
    factsheets = cache.get(cache_key)
    if factsheets:
        return factsheets

    factsheets = [i.rstrip('.pdf') for i in os.listdir(settings.FACTSHEETS_DIR)
                  if i.endswith('pdf')]
    cache.set(cache_key, factsheets, 60 * 60 * 12)
    return factsheets


def _segment_level(segment, measures, selected_vertex, selected_year,
                   protection_level):
    measures_level = segment.waterleveldifference_set.filter(
        measure__in=measures,
        protection_level=protection_level).aggregate(
        ld=Sum('level_difference'))['ld'] or 0
    try:
        vertex_level = models.VertexValue.objects.get(
            vertex=selected_vertex,
            riversegment=segment,
            year=selected_year).value
    except models.VertexValue.DoesNotExist:
        return

    return {'vertex_level': vertex_level,
            'measures_level': vertex_level + measures_level,
            'location': segment.location,
            'location_reach': '%i_%s' % (segment.location,
                                         segment.reach.slug),
            'location_segment': segment.reach.slug,
            }


def _water_levels(request):
    selected_river = _selected_river(request)
    selected_measures = _selected_measures(request)
    selected_vertex = _selected_vertex(request)
    selected_year = _selected_year(request)
    selected_protection_level = _selected_protection_level(selected_vertex)
    cache_key = (str(selected_river) + str(selected_vertex.id) +
                 selected_year + selected_protection_level +
                 ''.join(selected_measures))
    cache_key = md5(cache_key).hexdigest()
    water_levels = cache.get(cache_key)
    if not water_levels:
        logger.info("Cache miss for _water_levels")
        measures = models.Measure.objects.filter(
            short_name__in=selected_measures)
        riversegments = namedreach2riversegments(selected_river)
        segment_levels = [
            _segment_level(
                segment, measures, selected_vertex,
                selected_year, selected_protection_level)
            for segment in riversegments]
        water_levels = [segment for segment in segment_levels if segment]
        cache.set(cache_key, water_levels, 5 * 60)
    return water_levels


@never_cache
def calculated_measures_json(request):
    """Calculate the result of the measures."""

    water_levels = _water_levels(request)
    measures = _list_measures_json(request)
    cities = _city_locations_json(request)

    response = HttpResponse(mimetype='application/json')
    json.dump({'water_levels': water_levels,
               'measures': measures,
               'cities': cities},
               response)
    return response


def _available_vertices(request):
    selected_river = _selected_river(request)
    selected_year = _selected_year(request)
    vertices = models.Vertex.objects.filter(named_reaches__name=selected_river
                                            ).order_by('header', 'name')

    # Rule: we only show vertices with "1:250" in the name if the
    # selected river is "Onbedijkte Maas", because that is the only
    # river for which there is 1:250 data over its entire reach.
    if selected_river != "Onbedijkte Maas":
        vertices = vertices.exclude(name__contains="1:250")

    vertices = [vertex for vertex in vertices
                if models.VertexValue.objects.filter(
            vertex=vertex, year=selected_year).count()]
    return vertices


@never_cache
def vertex_json(request):
    vertices = _available_vertices(request)
    to_json = defaultdict(list)
    for vertex in vertices:
        to_json[vertex.header].append([vertex.id, vertex.name])
    response = HttpResponse(mimetype='application/json')
    json.dump(to_json, response)
    return response


@never_cache
@require_POST
@permission_required(VIEW_PERM)
def select_vertex(request):
    """Select the vertex."""
    request.session['vertex'] = request.POST['vertex']
    return HttpResponse()


@never_cache
def protection_level_json(request):
    response = HttpResponse(mimetype='application/json')
    json.dump(_available_protection_levels(request), response)
    return response


@never_cache
@require_POST
@permission_required(VIEW_PERM)
def select_protection_level(request):
    """Select 1/250 or 1/1250 protection level."""
    available = _available_protection_levels(request)
    chosen = request.POST['level']
    if not chosen in available:
        chosen = available[0]
    request.session['protection_level'] = chosen
    return HttpResponse()


def _selected_protection_level(vertex):
    # There is a special vertex for the 1:250 strategy on the Maas, it
    # should use the 1:250 protection level values, 1:1250 is used
    # everywhere else.
    if vertex and vertex.name and "1:250" in vertex.name:
        return "250"
    else:
        return "1250"


def _selected_vertex(request):
    """Return the selected vertex."""

    available_vertices = _available_vertices(request)
    available_vertices_ids = [i.id for i in available_vertices]

    if (not 'vertex' in request.session or
        int(request.session['vertex']) not in available_vertices_ids):
        vertex = available_vertices[0]
        request.session['vertex'] = vertex.id
        return vertex
    return models.Vertex.objects.get(id=request.session['vertex'])


def _selected_river(request):
    """Return the selected river"""
    available_reaches = models.NamedReach.objects.values_list(
        'name', flat=True).distinct().order_by('name')
    if not 'river' in request.session:
        request.session['river'] = available_reaches[0]
    if request.session['river'] not in available_reaches:
        logger.warn("Selected river %s doesn't exist anymore.",
                    request.session['river'])
        request.session['river'] = available_reaches[0]
    return request.session['river']


def _available_protection_levels(request):
    named_reach = models.NamedReach.objects.get(name=_selected_river(request))
    return named_reach.protection_levels


def _selected_year(request):
    """Return the selected year"""
    if not YEAR_SESSION_KEY in request.session:
        request.session[YEAR_SESSION_KEY] = '2100'
    return request.session[YEAR_SESSION_KEY]


def _selected_measures(request):
    """Return selected measures."""

    if not SELECTED_MEASURES_KEY in request.session:
        request.session[SELECTED_MEASURES_KEY] = set()
    return request.session[SELECTED_MEASURES_KEY]


def _unselectable_measures(request):
    """Return measure IDs that are not selectable.

    Current implementation is a temporary hack. Just disallow the measure two
    IDs further down the line...

    """

    return set(models.Measure.objects.filter(
        short_name__in=_selected_measures(request),
        exclude__isnull=False
    ).values_list('exclude__short_name', flat=True))


def _investment_costs(request):
    investment_costs = {
        'minimum': 0.0,
        'expected': 0.0,
        'maximum': 0.0
        }

    measures = models.Measure.objects.filter(
        short_name__in=_selected_measures(request))

    for measure in measures:
        investment_costs['minimum'] += (
            measure.minimal_investment_costs or 0)
        investment_costs['expected'] += (
            measure.investment_costs or 0)
        investment_costs['maximum'] += (
            measure.maximal_investment_costs or 0)

    for c in investment_costs:
        investment_costs[c] = round(investment_costs[c], 2)

    return investment_costs


@never_cache
@require_POST
@permission_required(VIEW_PERM)
def toggle_measure(request):
    """Toggle a measure on or off."""
    measure_id = request.POST['measure_id']
    selected_measures = _selected_measures(request)
    # Fix for empty u'' that somehow showed up.
    available_shortnames = list(models.Measure.objects.all().values_list(
        'short_name', flat=True))
    to_remove = []
    for shortname in selected_measures:
        if shortname not in available_shortnames:
            to_remove.append(shortname)
            logger.warn(
                "Removed unavailable shortname %r from selected measures.",
                shortname)
    if to_remove:
        selected_measures = selected_measures - set(to_remove)
        request.session[SELECTED_MEASURES_KEY] = selected_measures

    unselectable_measures = _unselectable_measures(request)
    if measure_id in selected_measures:
        selected_measures.remove(measure_id)
    elif measure_id not in available_shortnames:
        logger.error("Non-existing shortname %r passed to toggle_measure",
                     measure_id)
    elif not measure_id in unselectable_measures:
        selected_measures.add(measure_id)
    request.session[SELECTED_MEASURES_KEY] = selected_measures
    return HttpResponse(json.dumps(list(selected_measures)))


@never_cache
@require_POST
@permission_required(VIEW_PERM)
def select_river(request):
    """Select a river."""
    request.session['river'] = request.POST['river_name']
    del request.session['vertex']
    request.session['protection_level'] = _available_protection_levels(
        request)[0]
    return HttpResponse()


@never_cache
@require_POST
@permission_required(VIEW_PERM)
def select_year(request):
    """Select a year (for the vertices)."""
    year = request.POST['year']
    assert year in ['2050', '2100']
    request.session[YEAR_SESSION_KEY] = year
    return HttpResponse()


def _city_locations_json(request):
    """Return the city locations for the selected river."""

    selected_river = _selected_river(request)
    reach = models.NamedReach.objects.get(name=selected_river)
    subset_reaches = reach.subsetreach_set.all()
    segments_join = (models.CityLocation.objects.filter(
                     reach=element.reach,
                     km__range=(element.km_from, element.km_to))
                     for element in subset_reaches)

    # Join the querysets in segments_join into one.
    city_locations = reduce(operator.or_, segments_join)
    city_locations = city_locations.distinct().order_by('km')

    return [[km, city] for km, city in
            city_locations.values_list('km', 'city')]


def _list_measures_json(request):
    """Return a list with all known measures for the second graph."""

    measures = models.Measure.objects.all().values(
        'name', 'short_name', 'measure_type', 'km_from')
    for measure in measures:
        if not measure['measure_type']:
            measure['measure_type'] = 'Onbekend'
    all_types = list(
        set(measure['measure_type'] for measure in measures))

    if 'Onbekend' in all_types:
        all_types[all_types.index('Onbekend')] = 'ZZZZOnbekend'
        all_types.sort(reverse=True)
        all_types[all_types.index('ZZZZOnbekend')] = 'Onbekend'
    else:
        all_types.sort(reverse=True)

    single_characters = []
    for measure_type in all_types:
        if measure_type is 'Onbekend':
            single_characters.append('x')
        else:
            single_characters.append(measure_type[0].lower())
    selected_measures = _selected_measures(request)
    unselectable_measures = _unselectable_measures(request)
    selected_river = _selected_river(request)
    measures_selected_river = namedreach2measures(selected_river)
    for measure in measures:
        measure['selected'] = measure['short_name'] in selected_measures
        measure['selectable'] = (
            measure['short_name'] not in unselectable_measures)
        measure['type_index'] = all_types.index(measure['measure_type'])
        measure['type_indicator'] = single_characters[measure['type_index']]
        measure['show'] = measure['short_name'] in measures_selected_river

    return list(measures)


class AutomaticImportPage(BlockboxView):
    template_name = "lizard_blockbox/automatic_import.html"
    page_title = "Automatische import Blokkendoos"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(
            'lizard_management_command_runner.execute_managementcommand'):
            raise PermissionDenied()
        return super(
            AutomaticImportPage, self).dispatch(request, *args, **kwargs)

    def post(self, request, command):
        """Posting to this URL starts the background task."""
        try:
            management_command = ManagementCommand.objects.get(command=command)
        except ManagementCommand.DoesNotExist:
            return

        # Management command checks the user's rights
        tasks.run_management_command.delay(
            request.user,
            management_command)

        return HttpResponse()

    @property
    def content_actions(self):
        return []

    @property
    def breadcrumbs(self):
        result = super(AutomaticImportPage, self).breadcrumbs
        result.append(Action(name=self.page_title))
        return result
