import json

from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields

from orca.common import logger
from orca.topology.prometheus import alert as prom_alert
from orca.topology import probe

log = logger.get_logger(__name__)


class IngestEndpoint(Resource):

    def __init__(self, api, graph):
        super().__init__()
        self._graph = graph


class Prometheus(IngestEndpoint):

    """Prometheus ingest endpoint."""

    def post(self):
        payload = request.json
        log.info(json.dumps(payload))
        extractor = prom_alert.AlertExtractor()
        for alert in payload['alerts']:
            node = extractor.extract(alert)
            self._graph.add_node(node)


class Falco(IngestEndpoint):

    """Falco ingest endpoint."""

    def post(self):
        payload = request.json
        log.info(json.dumps(payload))


class Elastalert(IngestEndpoint):

    """Elastalert ingest endpoint."""

    def post(self):
        payload = request.json
        log.info(json.dumps(payload))


def initialize(graph):
    api = Namespace('ingestor', description='Ingestor API')
    api.add_resource(Prometheus, '/prometheus', resource_class_args=[graph])
    api.add_resource(Falco, '/falco', resource_class_args=[graph])
    api.add_resource(Elastalert, '/elastalert', resource_class_args=[graph])
    return api