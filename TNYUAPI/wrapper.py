import requests

from operator import attrgetter
import os

API_ROOT_URL = "https://api.tnyu.org/v3/"


class InvalidSearchAttributeError(Exception):

    """
    This exception is raised when in a sort method is invoked by an
    invalid attribute
    """

    def __init__(self, message):
        super(InvalidSearchAttributeError, self).__init__(message)


class AuthenticationException(Exception):

    """
    This exception is raised when a protected resource is accessed without
    authentication
    """
    pass


class TNYUAPI(object):

    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_all_events(self, sort_by=None):
        """
        Return a list of Event objects for all events
        """
        resources = self.get_resource('events')['data']
        events = [Event.from_json(self, x) for x in resources]

        if sort_by:
            if not hasattr(events[0], sort_by):
                raise InvalidSearchAttributeError()
            return sorted(events, key=attrgetter(sort_by))

        return events

    def get_all_people(self, sort_by=None):
        resources = self.get_resource('people')['data']
        people = [Person.from_json(self, x) for x in resources]

        if sort_by:
            if not hasattr(people[0], sort_by):
                raise InvalidSearchAttributeError()
            return sorted(people, key=attrgetter(sort_by))

        return people

    def get_all_venues(self, sort_by=None):
        resources = self.get_resource('venues')['data']
        venues = [Venue.from_json(self, x) for x in resources]

        if sort_by:
            if not hasattr(venues[0], sort_by):
                raise InvalidSearchAttributeError()
            return sorted(venues, key=attrgetter(sort_by))

        return venues

    def get_all_organizations(self, sort_by=None):
        resources = self.get_resource('organizations')['data']
        org = [Organization.from_json(self, x) for x in resources]

        if sort_by:
            if not hasattr(org[0], sort_by):
                raise InvalidSearchAttributeError()
            return sorted(org, key=attrgetter(sort_by))

        return org

    def get_all_teams(self, sort_by=None):
        resources = self.get_resource('teams')['data']
        teams = [Team.from_json(self, x) for x in resources]

        if sort_by:
            if not hasattr(teams[0], sort_by):
                raise InvalidSearchAttributeError()
            return sorted(teams, key=attrgetter(sort_by))

        return teams

    def get_resource(self, path):
        headers = {
            'content-type': 'application/vnd.api+json',
            'accept': 'application/*, text/*',
            'authorization': 'Bearer ' + self.api_key
        }

        r = requests.get(API_ROOT_URL + path, headers=headers)
        return r.json()


class Organization(object):

    def __init__(self, client, org_id, json_obj=None):
        self.id = org_id
        self.client = client

        if json_obj:
            self._attributes = json_obj['attributes']
            self._relationships = json_obj['relationships']
        else:
            # Pull data from the API using event id
            res = client.get_resource('organizations/%s' % self.id)['data']
            self._attributes = res['attributes']
            self._relationships = res['relationships']

    @classmethod
    def from_json(cls, client, json_obj):
        """
        Allow instantiation of an Person object from JSON
        """
        return Organization(client, json_obj['id'], json_obj)

    def liaisons(self):
        liaisons_list = self._relationships['liaisons']['data']
        tmp = []

        for each_person in liaisons_list:
            # Check if the person id exists in the API anymore
            try:
                tmp.append(Person(self.client, each_person['id']))
            except:
                continue

        return tmp

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Org object has no attribute " + attr)
        return self._attributes[attr]

    def __repr__(self):
        return self.name


class Person(object):

    def __init__(self, client, person_id, json_obj=None):
        self.id = person_id
        self.client = client

        if json_obj:
            self._attributes = json_obj['attributes']
            self._relationships = json_obj['relationships']
        else:
            # Pull data from the API using event id
            res = client.get_resource('people/%s' % self.id)['data']
            self._attributes = res['attributes']
            self._relationships = res['relationships']

    @classmethod
    def from_json(cls, client, json_obj):
        """
        Allow instantiation of an Person object from JSON
        """
        return Person(client, json_obj['id'], json_obj)

    def organization(self):
        org_data = self._relationships['currentEmployer']['data']
        if org_data:
            return Organization(self.client, org_data['id'])
        return None


    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Person object has no attribute " + attr)
        return self._attributes[attr]

    def __repr__(self):
        return self.name


class Team(object):

    """
    This class represents a Tech @ NYU Team
    """

    def __init__(self, client, team_id, json_obj=None):
        self.id = team_id
        self.client = client

        if json_obj:
            self._attributes = json_obj['attributes']
        else:
            # Pull data from the API using event id
            res = client.get_resource('teams/%s' % self.id)['data']
            self._attributes = res['attributes']

    @classmethod
    def from_json(cls, client, json_obj):
        """
        Allow instantiation of an Event object from JSON
        """
        return Team(client, json_obj['id'], json_obj)

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Team object has no attribute " + attr)
        return self._attributes[attr]


class Venue(object):

    """
    This class represents a Tech @ NYU event venue
    """

    def __init__(self, client, venue_id, json_obj=None):
        self.id = venue_id
        self.client = client

        if json_obj:
            self._attributes = json_obj['attributes']
            self._relationships = json_obj['relationships']
        else:
            # Pull data from the API using event id
            res = client.get_resource('venues/%s' % self.id)['data']
            self._attributes = res['attributes']
            self._relationships = res['relationships']
            self._relationships = json_obj['relationships']

    @classmethod
    def from_json(cls, client, json_obj):
        """
        Allow instantiation of an Event object from JSON
        """
        return Venue(client, json_obj['id'], json_obj)

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Venue object has no attribute " + attr)
        return self._attributes[attr]

    def __repr__(self):
        return self.name


class Event(object):

    """
    Class to represent a Tech @ NYU Event
    """

    def __init__(self, client, event_id, json_obj=None):
        self.id = event_id
        self.client = client

        if json_obj:
            self._attributes = json_obj['attributes']
        else:
            # Pull data from the API using event id
            res = client.get_resource('events/%s' % self.id)['data']
            self._attributes = res['attributes']
            self._relationships = res['relationships']

    @classmethod
    def from_json(cls, client, json_obj):
        """
        Allow instantiation of an Event object from JSON
        """
        return Event(client, json_obj['id'], json_obj)

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Event object has no attribute " + attr)
        return self._attributes[attr]

    def venue(self):
        venue_id = self._relationships['venue']['data']['id']
        return Venue(self.client, venue_id)

    def __repr__(self):
        return self.title.encode('utf-8')

if __name__ == '__main__':
    api = TNYUAPI(api_key=os.environ['TNYU_API_KEY'])
    peeps = api.get_all_people()
    print peeps[1].organization()

