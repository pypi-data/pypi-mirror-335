from fireREST76.defaults import API_RELEASE_610
from fireREST76.fmc import Resource


class ApplicationTag(Resource):
    PATH = '/object/applicationtags/{uuid}'
    MINIMUM_VERSION_REQUIRED_GET = API_RELEASE_610
