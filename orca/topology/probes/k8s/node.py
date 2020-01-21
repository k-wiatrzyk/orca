
from orca.common import logger
from orca.k8s import client as k8s_client
from orca.topology.probes import graph as graph_fetcher
from orca.topology.probes.k8s import extractor, linker, probe

log = logger.get_logger(__name__)


class NodeExtractor(extractor.KubeExtractor):

    def extract_properties(self, entity):
        properties = {}
        properties['name'] = entity.metadata.name
        return properties


class NodeProbe(probe.Probe):

    def run(self):
        log.info("Starting K8S watch on resource: node")
        extractor = NodeExtractor()
        handler = probe.KubeHandler(self._graph, extractor)
        watch = k8s_client.ResourceWatch(self._client.CoreV1Api(), 'node', namespaced=False)
        watch.add_handler(handler)
        watch.run()


class NodeToClusterMatcher(linker.Matcher):

    def are_linked(self, pod, node):
        return True


class NodeToClusterLinker(linker.Linker):

    @staticmethod
    def create(graph, client):
        node_fetcher = graph_fetcher.Fetcher(graph, 'node')
        cluster_fetcher = graph_fetcher.Fetcher(graph, 'cluster')
        matcher = NodeToClusterMatcher()
        return NodeToClusterLinker(
            graph, 'node', node_fetcher, 'cluster', cluster_fetcher, matcher)
