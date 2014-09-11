from club.models import ClubInvite
from django.shortcuts import get_object_or_404
from users.models import Athlete, PRIVACY_LEVELS
from django.core.exceptions import PermissionDenied
from club import ROLES

class UserInviteMixin(object):
  invite = None

  def dispatch(self, *args, **kwargs):
    self.check_invite() # Load invite first
    out = super(UserInviteMixin, self).dispatch(*args, **kwargs)
    return out

  def get_context_data(self, *args, **kwargs):
    context = super(UserInviteMixin, self).get_context_data(*args, **kwargs)

    # Add invite if any
    if self.invite:
      context['invite'] = self.invite

    return context

  def check_invite(self):
    # Load a potential invite from session
    try:
      self.invite = ClubInvite.objects.get(slug=self.request.session['invite'])
    except :
      return False
    return True


class ProfilePrivacyMixin(object):
  '''
  Check the user has any right to view a public profile
  Loads available rights according to context
  '''
  member = None
  privacy = [] # Rights available to visitor

  def get_member(self):
    '''
    Load the requested athlete
    with available privacy for connected visitor
    '''
    self.member = get_object_or_404(Athlete, username=self.kwargs['username'])

    # Load all member privacy settings
    fields = [k[12:-8] for k in Athlete.__dict__ if 'privacy' in k] # all the fields as 'get_privacy_%s_display'
    rights = self.load_visitor_rights()
    self.privacy = [f for f in fields if getattr(self.member, 'privacy_%s' % f) in rights]

    # Check basic profile access
    if 'profile' not in self.privacy:
      raise PermissionDenied

    return self.member

  def dispatch(self, *args, **kwargs):
    # Check you have the rights
    self.get_member()

    return super(ProfilePrivacyMixin, self).dispatch(*args, **kwargs)

  def get_context_data(self, *args, **kwargs):
    context = super(ProfilePrivacyMixin, self).get_context_data(*args, **kwargs)
    context['member'] = self.member
    context['privacy'] = self.privacy
    context['levels'] = dict(PRIVACY_LEVELS)
    context['roles'] = dict(ROLES)
    return context

  def load_visitor_rights(self):
    '''
    Load the visitor rights for connected visitor
    '''

    # All rights when visitor is member
    if self.request.user == self.member:
      return ('public', 'club', 'private')

    # Club & public rights
    # when visitor is in same club
    if self.request.user.is_authenticated():
      member_clubs = set([m['club__id'] for m in self.member.memberships.values('club__id')])
      user_clubs = set([m['club__id'] for m in self.request.user.memberships.values('club__id')])
      if len(member_clubs & user_clubs) > 0:
        return ('public', 'club')

    # By default, public
    return ('public', )
