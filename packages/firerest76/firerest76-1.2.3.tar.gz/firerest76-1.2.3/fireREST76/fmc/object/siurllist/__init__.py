from fireREST76.defaults import API_RELEASE_623
from fireREST76.fmc import Resource


class SiUrlList(Resource):
    PATH = '/object/siurllists/{uuid}'
    MINIMUM_VERSION_REQUIRED_GET = API_RELEASE_623
