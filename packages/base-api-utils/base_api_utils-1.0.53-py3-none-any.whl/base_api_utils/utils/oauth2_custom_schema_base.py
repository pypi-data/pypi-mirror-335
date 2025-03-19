from .config import config
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class OAuth2CustomSchemaBase(OpenApiAuthenticationExtension):
    target_class = 'base_api_utils.security.oauth2_mock_authentication.OAuth2MockAuthentication'
    name = config('OPEN_API_SECURITY_SCHEMA_NAME')

    def get_security_definition(self, auto_schema):
        return {
            'type': 'oauth2',
            'flows': {
                'implicit': {
                    'authorizationUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.AUTHORIZATION_ENDPOINT')}',
                    'tokenUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.TOKEN_ENDPOINT')}',
                    'refreshUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.REFRESH_TOKEN_ENDPOINT')}',
                    'scopes': {}
                },
            },
            'description': 'OAuth2 authentication.'
        }
