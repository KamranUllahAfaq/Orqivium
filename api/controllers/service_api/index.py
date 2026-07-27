from flask_restx import Resource

from configs import orqivium_config
from controllers.common.fields import IndexInfoResponse
from controllers.common.schema import register_response_schema_models
from controllers.service_api import service_api_ns

register_response_schema_models(service_api_ns, IndexInfoResponse)


@service_api_ns.route("/")
class IndexApi(Resource):
    @service_api_ns.response(200, "Success", service_api_ns.models[IndexInfoResponse.__name__])
    def get(self) -> dict[str, str]:
        return {
            "welcome": "Orqivium OpenAPI",
            "api_version": "v1",
            "server_version": orqivium_config.project.version,
        }
