from fireREST76.defaults import API_RELEASE_700
from fireREST76.fmc import Resource


class IdentityPolicy(Resource):
    PATH = '/policy/identitypolicies/{uuid}'
    MINIMUM_VERSION_REQUIRED_GET = API_RELEASE_700
