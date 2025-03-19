from typing import Callable, List, Mapping
from functools import partial

from bottle import Bottle, PluginError, request, response

from JWT import Token


def auth_required(callable: Callable):
    setattr(callable, "auth_required", True)
    return callable


class BaseAuth(object):
    @staticmethod
    def authenticate(*args, **kwargs):
        pass

    @staticmethod
    def get_user(*args, **kwargs):
        pass


class JWTPluginError(Exception):
    ...


class JWTPlugin(object):
    name = "JWTPlugin"
    api = 2

    def __init__(self, secret: str, config: Mapping[str, object], payload: List[str] = None, debug: bool = False) -> None:
        """
            config: List[Mapping[str, object]]: Objeto que conterá classes e endpoints para autenticação.
            ex:
            config -> {'model': AdminAuth, 'endpoint': '/admin/auth'}

            A classe responsável pela autenticação (AdminAuth, UserAuth) devem implementar uma interface.

            payload exemplo: {"id": None, "email": None}
        """
        self.secret = secret
        self.config = config
        self.payload = payload

    def authenticate(self, model: BaseAuth, secret: str, pl: Mapping[str, object]={}):
        """ Método utilizado para gerar o token.0

        Args:
            model (BaseAuth): Modelo utilizado para utilizar informações para geraro token
            secret (str): segredo para criptografia do token JWT
            pl (Mapping[str, object]): payload customizado. Defaults to {}.

        Raises:
            JWTPluginError: Erro quando payload é inválida.

        Returns:
            _type_: return Mapping[str, object] com token e refresh_token.
        """
        data = request.json
        user = model.authenticate(**data)
        payload = {}
        if pl:
            for key in pl:
                payload[key] = getattr(user, key) if hasattr(user, key) else None
                if payload[key] == None:
                    del payload[key]
        else:
            payload["id"] = user.id if hasattr(user, "id") else None
            if payload["id"] == None:
                del payload["id"]
            if not payload:
                raise JWTPluginError("Modelo não possui nenhum parametro compativel com atributos de autenticação.")
            if not "exp" in payload:
                payload['exp'] = ""
        token = Token(payload=payload, secret=secret)
        payload['token'] = token.create()
        objRefreshToken = Token(payload, secret=secret)
        refresh_token = objRefreshToken.create()
        response.content_type = "application/json"
        response.status = 200
        return {"token": payload['token'], "refresh_token": refresh_token}
    
    def refresh(self, model, secret, payload={}):
        refresh_jwt = request.get_header("Refresh-Jwt")
        decoded = Token(secret=secret).decode(refresh_jwt)
        token = decoded['token']
        del decoded['token']
        user = model.get_user(**decoded)
        if decoded:
            payload = {}
            if payload:
                for key in payload:
                    payload[key] = getattr(user, key) if hasattr(user, key) else None
                    if payload[key] == None:
                        del payload[key]
            else:
                payload["id"] = user.id if hasattr(user, "id") else None
                if payload["id"] == None:
                    del payload["id"]
                    if not payload:
                        raise JWTPluginError("Modelo não possui nenhum parametro compativel com atributos de autenticação.")
                if not "exp" in decoded:
                    payload['exp'] = ""
            token = Token(payload=payload, secret=secret, expire_time=0.05)
            payload['token'] = token.create()
            refresh_token = Token(payload, secret=secret)
            response.content_type = "application/json"
            response.status = 200
            return {"token": token.create(), "refresh_token": refresh_token.create()}

    def setup(self, app: Bottle):
        for plugin in app.plugins:
            if isinstance(plugin, JWTPlugin):
                raise PluginError("Encontrado uma outra instancia do plugin.")
            else:
                model = self.config['model']
                if issubclass(model, BaseAuth):
                    # model, configs, pl, secret
                    app.post(self.config['endpoint'], callback=partial(self.authenticate, model, self.secret, self.payload))
                    app.post(f"{self.config['endpoint']}/refresh", callback=partial(self.refresh, model, self.secret, self.payload))
                else:
                    raise JWTPluginError("Não implementa interface de autenticação.")

    def apply(self, callback, _):
        def injector(*args, **kwargs):
            return callback(*args, **kwargs)

        if not hasattr(callback, "auth_required"):
            return injector

        def wrapper(*args, **kwargs):
            header_token = request.get_header("Authorization")
            decoded = Token(secret=self.secret).decode(header_token)
            model = self.config['model']
            user = model.get_user(**decoded)
            if user:
                kwargs["user"] = user
                return injector(*args, **kwargs)
            return injector(*args, **kwargs)

        return wrapper