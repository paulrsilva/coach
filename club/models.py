from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
  name = models.CharField(max_length=250)
  slug = models.SlugField(unique=True, max_length=20)
  members = models.ManyToManyField(User, through='ClubMembership')
  main_trainer = models.ForeignKey(User, null=True, blank=True, related_name="club_main_trainer")
  manager = models.ForeignKey(User, related_name="club_manager")

  # Users limits
  max_staff = models.IntegerField(default=1)
  max_trainer = models.IntegerField(default=2)
  max_athlete = models.IntegerField(default=20)

  # Extra infos
  address = models.CharField(max_length=250)
  zipcode = models.CharField(max_length=10)
  city = models.CharField(max_length=250)

  def __unicode__(self):
    return self.name

  def load_stats(self):
    '''
    Count available and used accounts
    '''
    stats = []
    types = ('staff', 'trainer', 'athlete')
    for t in types:
      max = getattr(self, 'max_%s' % t)
      used = self.clubmembership_set.filter(role=t).count()
      stats.append({
        'type' : t,
        'max' : max,
        'used' : used,
        'diff' : max - used,
        'percent' : round(100 * (max - used) / max)
      })
    return stats

class ClubMembership(models.Model):
  CLUB_ROLES = (
    ('athlete', 'Athlete'),
    ('trainer', 'Trainer'),
    ('staff', 'Staff'), # For presidents...
    ('archive', 'Archive'),
  )
  user = models.ForeignKey(User, related_name="memberships")
  club = models.ForeignKey(Club)
  trainers = models.ManyToManyField(User, related_name="trainees")
  role = models.CharField(max_length=10, choices=CLUB_ROLES)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = (('user', 'club'),)

class ClubLink(models.Model):
  club = models.ForeignKey(Club, related_name="links")
  name = models.CharField(max_length=250)
  url = models.URLField(max_length=250)
  position = models.IntegerField()

class ClubInvite(models.Model):
  INVITE_TYPES = (
    ('create', 'Create a club (Beta)'),
  )
  sender = models.ForeignKey(User, related_name="inviter")
  recipient = models.ForeignKey(User, related_name="invitee", null=True)
  club = models.ForeignKey(Club, null=True, blank=True, related_name="invites")
  type = models.CharField(max_length=15, choices=INVITE_TYPES)
  slug = models.CharField(max_length=30, unique=True, blank=True) # not a slug: no char restriction
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  sent = models.DateTimeField(null=True, blank=True)
  used = models.DateTimeField(null=True, blank=True)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.build_slug()
    super(ClubInvite, self).save(*args, **kwargs)

  def build_slug(self, length=10):
    '''
    Build the slug using random chars & digits
    '''
    import string
    import random
    chars = string.letters + string.digits
    self.slug = ''.join(random.Random().sample(chars, length))

  @models.permalink
  def get_absolute_url(self):
    return ('club-invite', (self.slug, ))

  def use(self):
    '''
    Mark the invite as used
    '''
    # Set used
    from datetime import datetime
    self.used = datetime.now()
    self.save()
