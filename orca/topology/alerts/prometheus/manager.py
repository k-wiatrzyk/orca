# Copyright 2020 OpenRCA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orca.common import config
from orca.common.clients.prometheus import client as prometheus
from orca.topology import ingestor, probe, utils
from orca.topology.alerts import extractor, linker
from orca.topology.alerts.prometheus import extractor as prom_extractor
from orca.topology.alerts.prometheus import upstream

CONFIG = config.CONFIG


def initialize_probes(graph):
    source_mapper = extractor.SourceMapper('prometheus')
    prom_client = prometheus.PrometheusClient.get(url=CONFIG.prometheus.url)
    return [
        probe.PullProbe(
            graph=graph,
            upstream_proxy=upstream.UpstreamProxy(prom_client),
            extractor=prom_extractor.AlertExtractor(source_mapper),
            synchronizer=utils.NodeSynchronizer(graph),
            resync_period=CONFIG.prometheus.resync_period
        )
    ]


def initialize_linkers(graph):
    return [
        linker.Linker(
            graph=graph,
            source_spec=utils.NodeSpec(origin='prometheus', kind='alert'),
            target_spec=utils.NodeSpec(origin='any', kind='any'),
            matcher=linker.AlertToSourceMatcher(),
            bidirectional=False
        )
    ]


def initialize_handler(graph):
    source_mapper = extractor.SourceMapper('prometheus')
    return ingestor.EventHandler(graph, prom_extractor.AlertEventExtractor(source_mapper))
