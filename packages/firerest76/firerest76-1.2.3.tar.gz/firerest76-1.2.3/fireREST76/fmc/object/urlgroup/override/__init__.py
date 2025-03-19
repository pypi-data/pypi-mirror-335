from fireREST76.defaults import API_RELEASE_610
from fireREST76.fmc import ChildResource


class Override(ChildResource):
    CONTAINER_NAME = 'UrlGroup'
    CONTAINER_PATH = '/object/urlgroups/{uuid}'
    PATH = '/object/urlgroups/{container_uuid}/overrides/{uuid}'
    MINIMUM_VERSION_REQUIRED_GET = API_RELEASE_610
