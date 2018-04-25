# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
from copy import copy
import logging
import urlparse
import urllib
import json

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView

from lizard_ui.forms import LoginForm
from lizard_ui.layout import Action
from lizard_ui import uisettings


DEFAULT_APPLICATION_SCREEN = 'home'

logger = logging.getLogger(__name__)


class ViewContextMixin(object):
    """View mixin that adds the view object to the context.

    Make sure this is near the front of the inheritance list: it should come
    before other mixins that (re-)define ``get_context_data()``.

    When you use this mixin in your view, you can do ``{{ view.some_method
    }}`` or ``{{ view.some_attribute }}`` in your class and it will call those
    methods or attributes on your view object: no more need to pass in
    anything in a context dictionary, just stick it on ``self``!

    """
    def get_context_data(self, **kwargs):
        """Return context with view object available as 'view'."""
        try:
            context = super(ViewContextMixin, self).get_context_data(**kwargs)
        except AttributeError:
            context = {}
        context.update({'view': self})
        return context


class ViewNextURLMixin(object):
    """View mixin that adds next url redirect parsing.

    This can be used for login or logout functionality.
    """

    default_redirect = '/'

    def next_url(self):
        # Used to fill the hidden field in the LoginForm
        return self.request.GET.get('next', self.default_redirect)

    def check_url(self, next_url=None):
        """Check if the next url is valid."""

        if next_url is None:
            next_url = self.default_redirect

        netloc = urlparse.urlparse(next_url)[1]
        # Security check -- don't allow redirection to a different
        # host.
        if netloc and netloc != self.request.get_host():
            return self.default_redirect

        return next_url


class LoginView(ViewContextMixin, FormView, ViewNextURLMixin):
    """Logs in the user."""

    template_name = 'lizard_ui/login.html'
    form_class = LoginForm
    default_redirect = '/'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            login(self.request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if request.is_ajax():
                return HttpResponse(json.dumps({'success': True}),
                                    mimetype='application/json')

            next_url = form.cleaned_data['next_url']
            redirect_to = self.check_url(next_url)
            return HttpResponseRedirect(redirect_to)

        if request.is_ajax():
            errors = ' '.join(form.non_field_errors())
            for fieldname, errorlist in form.errors.items():
                if fieldname in form.fields:
                    errors += ' ' + form.fields[fieldname].label + ': '
                    errors += ' '.join(errorlist)
                else:
                    errors += ' '.join(errorlist)
            return HttpResponse(json.dumps({'success': False,
                                            'error_message': errors}),
                                mimetype='application/json')
        return self.form_invalid(form)


class LogoutView(View, ViewNextURLMixin):
    """
    Logout for ajax and regualar GET/POSTS.

    This View does a logout for the user,
    redirects to the next url when it's given.
    When the request is done via Ajax an empty response is returned.
    """

    def get(self, request, *args, **kwargs):
        logout(request)
        if request.is_ajax():
            return HttpResponse("")

        redirect_to = self.check_url(self.next_url())
        return HttpResponseRedirect(redirect_to)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class UiView(ViewContextMixin, TemplateView):
    """Base view for a lizard-ui-using view+template.

    This view feeds all necessary blocks with nicely structured data. The
    effect is that we don't need to muck around with lots of template tags
    anymore.

    There are two basic ways in which to customize it:

    - Apps can subclass ``UiView`` and overwrite methods to add or change UI
      elements.

    - Sites can use a subclass, but that doesn't change anything for apps that
      already subclassed themselves or that use UiView directly. So they can
      best customize the ``lizard_ui/lizardbase.html`` template.

    You can specify ``required_permission``. If set, the permission is checked
    (and the user is redirected to the login page if needed).

    """
    template_name = 'lizard_ui/lizardbase.html'
    icon_url_name = 'lizard_ui.icons'
    # ^^^ So that we can subclass this view and still get proper urls.
    show_secondary_sidebar_title = None
    show_secondary_sidebar_icon = None
    show_rightbar_title = None
    require_application_icon_with_permission = False
    # ^^^ If there's no visible application icon, we don't have the necessary
    # permission. At least, that's what this is intended for.
    required_permission = None
    sidebar_is_collapsed = False
    rightbar_is_collapsed = True
    secondary_sidebar_is_collapsed = True
    page_title = None

    def get_context_data(self, **kwargs):
        if self.require_application_icon_with_permission:
            if not self.best_matching_application_icon:
                logger.warn(
                    "Accessing view without required application icon.")
                # TODO: change to 403 (forbidden) with Django 1.4.
                raise Http404
        return super(UiView, self).get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        if self.required_permission:
            if not request.user.has_perm(self.required_permission):
                return HttpResponseRedirect(
                    settings.LOGIN_URL + '?next=%s' % request.path)
        return super(UiView, self).dispatch(request, *args, **kwargs)

    @property
    def gauges_site_id(self):
        """Return gaug.es tracking code (unless we're in debug mode)."""
        if settings.DEBUG:
            return
        return uisettings.GAUGES_SITE_ID

    @property
    def title(self):
        """Return title for use in 'head' tag.

        By default it uses the ``page_title`` attribute, followed by
        ``UI_SITE_TITLE`` (which is 'lizard' by default).

        """
        return ' - '.join([self.page_title, uisettings.SITE_TITLE])

    @property
    def site_actions(self):
        """Return site actions.

        ``UI_SITE_ACTIONS`` are on the left, a login link (if
        ``UI_SHOW_LOGIN`` is True) on the right.

        """
        actions = copy(uisettings.SITE_ACTIONS)

        if uisettings.SHOW_LANGUAGE_PICKER:
            languages = settings.LANGUAGES
            if len(languages) > 1:
                language_code = get_language()  # current language code
                language_name = _('Language')  # sort of default
                try:
                    language_name = dict(settings.LANGUAGES)[language_code.lower()]
                except KeyError:
                    for code, name in languages:
                        if language_code.lower().startswith(code):
                            language_name = name
                            break
                query_string = urllib.urlencode(
                    {'next': self.request.path_info})
                lang_action = Action(icon='icon-flag')
                lang_action.url = '%s?%s' % (
                    reverse('lizard_ui.change_language'), query_string)
                lang_action.name = language_name
                lang_action.description = _('Pick a language')
                lang_action.klass = 'ui-change-language-link'
                actions.append(lang_action)

        if uisettings.SHOW_LOGIN:
            query_string = urllib.urlencode({'next': self.request.path_info})
            if self.request.user.is_authenticated():
                # Name of the user. TODO: link to profile page.
                # The action is just text-with-an-icon right now.
                action = Action(icon='icon-user')
                action.name = self.request.user
                action.description = _('Your current username')
                actions.append(action)
                # Separate logout action.
                action = Action()
                if getattr(settings, 'SSO_ENABLED', False):
                    # point to the SSO logout page (which redirects
                    # to another server)
                    action.url = '%s?%s' % (reverse('logout'),
                                            query_string)
                else:
                    # fall back to the old (local) logout page
                    action.url = '%s?%s' % (reverse('lizard_ui.logout'),
                                            query_string)
                action.name = _('logout')
                action.description = _('Click here to logout')
                action.klass = 'ui-logout-link'
                actions.append(action)
            else:
                action = Action(icon='icon-user')
                if getattr(settings, 'SSO_ENABLED', False):
                    # point to the SSO login page (which redirects
                    # to another server)
                    action.url = '%s?%s' % (reverse('login'),
                                            query_string)
                else:
                    # fall back to the old (local) login form
                    action.url = '%s?%s' % (reverse('lizard_ui.login'),
                                            query_string)
                action.name = _('Login')
                action.description = _('Click here to login')
                if getattr(settings, 'SSO_ENABLED', False):
                    action.klass = 'ui-sso-login-link'
                else:
                    # fall back to the javascript login modal
                    action.klass = 'ui-login-link'
                actions.append(action)
        return actions

    @property
    def breadcrumbs(self):
        """Return breadcrumbs (as a list of actions).

        Overwrite it if you want something really different. Otherwise it
        tries to make a best guess effort by looking at what lizard-ui itself
        knows regarding icons and screens that point at it.

        """
        return []

    @property
    def edit_link(self):
        """Return link to edit ourselves. (Just the link, not an action.)"""
        return None

    @property
    def edit_action(self):
        """Return edit link as an action, ready for content_actions."""
        return Action(name=_('Edit'),
                      description=_('Edit this page.'),
                      url=self.edit_link,
                      icon='icon-edit')

    @property
    def content_actions(self):
        """Return content actions.

        Content actions are different for every kind of object, so by default
        is is just empty. Customization should happen in a subclass,
        logically.

        There's one exception: if there's an edit link, display its action.

        """
        if self.edit_link and self.request.user.is_staff:
            return [self.edit_action]
        return []

    @property
    def sidebar_actions(self):
        """Return sidebar actions.

        If ``UI_SHOW_SIDEBAR_COLLAPSE`` is True, it is shown on the
        left. There's very limited place for actions here, so restrict
        yourself regarding adding new ones.

        """
        collapse_action = Action(
            icon='icon-arrow-left',
            name=_('Apps'),
            description=_('Collapse or expand this panel'),
            klass='collapse-sidebar')
        actions = [collapse_action]
        if self.show_secondary_sidebar_title:
            # Having a title means we want to show it.
            actions.append(
                Action(name=self.show_secondary_sidebar_title,
                       description=_('Collapse or expand this panel'),
                       icon=self.show_secondary_sidebar_icon,
                       klass='secondary-sidebar-button'))
        return actions

    @property
    def rightbar_actions(self):
        """Return rightbar actions.

        By default, the only action is a open/collapse one if its title is
        specified.

        """
        actions = []
        if self.show_rightbar_title:
            # Having a title means we want to show it.
            actions.append(
                Action(name=self.show_rightbar_title,
                       description=_('Collapse or expand this panel'),
                       icon='icon-arrow-left',
                       klass='collapse-rightbar'))
        return actions

    @property
    def orthogonal_action_groups(self):
        """Return groups of orthogonal actions.

        In the bar below the content, the actions are grouped. This is a
        difference with the other action methods: the list(s) of actions are
        themselves inside a list.

        """
        actions = []
        groups = [actions]
        return groups
