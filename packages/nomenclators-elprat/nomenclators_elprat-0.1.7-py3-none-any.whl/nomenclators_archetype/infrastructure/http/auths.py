"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón(y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
import os
import jwt


AUTH_SECRET_KEY_ENV_NAME = "AUTH_SECRET_KEY"
AUTH_SECRET_KEY_DEFAULT = "nomenclators_archetype_secret_key"
AUTH_SECRET_KEY = os.getenv(AUTH_SECRET_KEY_ENV_NAME, AUTH_SECRET_KEY_DEFAULT)

APPLICATION_ID_ENV_NAME = "APPLICATION_ID"
APPLICATION_ID_DEFAULT = "Nomenclators Archetype Library"
APPLICATION_ID = os.getenv(APPLICATION_ID_ENV_NAME, APPLICATION_ID_DEFAULT)


def get_user_from_jwt(session_id):
    """Extrae el usuario del token JWT en la petición"""

    if not session_id:
        return None

    try:
        token = session_id.split(" ")[1]
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=["HS256"])

        return payload.get("sub", None)

    except jwt.ExpiredSignatureError:
        return "Token expirado"
    except jwt.InvalidTokenError:
        return "Token inválido"
