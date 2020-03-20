import re
from yaml import load, Loader
from pathlib import Path
from collections import OrderedDict


class GenerateGraphvizSource():
    def _escape_value(self, source_value: str or int or float or bool) -> str:
        if isinstance(source_value, bool):
            if source_value:
                target_value = '"true"'

            else:
                target_value = '"false"'

        elif isinstance(source_value, str):
            target_value = source_value.replace('\r\n', '\n').replace('\n', '\\n').replace('"', '\\"')

            if not target_value.startswith('<') or not target_value.endswith('>'):
                target_value = f'"{target_value}"'

        else:
            target_value = f'"{source_value}"'

        return target_value

    def _serialize_single_line(self, entity_specification: str, entity_params: dict) -> str:
        serialized_entity_definition: str = f'{entity_specification} ['

        index: int
        key: str
        for index, key in enumerate(entity_params.keys()):
            if index > 0:
                serialized_entity_definition += ', '

            serialized_entity_definition += f'{key} = {self._escape_value(entity_params[key])}'

        serialized_entity_definition += '];\n'

        return serialized_entity_definition

    def _serialize_multiple_lines(self, params: dict) -> str:
        serialized_params: str = ''

        key: str
        for key in params.keys():
            serialized_params += f'{key} = {self._escape_value(params[key])};\n'

        return serialized_params

    def _csv_to_list(self, data: list or str) -> list:
        if isinstance(data, str):
            data = re.sub(r'\,\s*', ', ', data, flags=re.MULTILINE)
            data: list = data.split(', ')

        return data

    def _list_to_csv(self, data: str or list) -> str:
        if isinstance(data, list):
            data: str = ', '.join(data)

        return data

    def _merge_element_params(self, element_type: str, element_params: dict, dsl_full_scheme: dict) -> dict:
        element_styles: list = self._csv_to_list(element_params.pop('style', []))
        element_classes: list or str = element_params.pop('class', [])

        if not isinstance(element_classes, list):
            element_classes: list = [element_classes]

        element_type_params: dict = dsl_full_scheme.get('elements', {}).get(element_type, {}).copy()
        element_type_classes: dict = element_type_params.pop('classes', {})
        merged_classes_params: dict = {}

        class_name: str
        for class_name in element_classes:
            class_params: dict = element_type_classes.get(class_name, {})
            element_styles.extend(self._csv_to_list(class_params.get('style', [])))
            merged_classes_params.update(class_params)

        element_styles = sorted(list(set(element_styles)))

        if element_styles:
            element_params.update({'style': self._list_to_csv(element_styles)})

        merged_element_params = {**merged_classes_params, **element_params}

        if element_type == 'cluster':
            element_type_styles: list or str = element_type_params.pop('style', [])

            if element_type_styles:
                element_type_params['style'] = self._list_to_csv(self._csv_to_list(element_type_styles))

            merged_element_params = {**element_type_params, **merged_element_params}

        return merged_element_params

    def _get_nodes(self, dsl_full_scheme: dict) -> OrderedDict:
        def _get_substructure_nodes(substructure: list) -> OrderedDict:
            substructure_nodes: OrderedDict = {}

            substructure_item: dict
            for substructure_item in substructure:
                node_params: dict = substructure_item.get('node', {})
                cluster_params: dict = substructure_item.get('cluster', {})

                if node_params:
                    working_node_params: dict = node_params.copy()
                    node_id: str = working_node_params.pop('id', '')

                    if node_id:
                        working_node_params = self._merge_element_params(
                            'node',
                            working_node_params,
                            dsl_full_scheme
                        )

                        substructure_nodes[node_id] = working_node_params

                elif cluster_params:
                    substructure_nodes.update(_get_substructure_nodes(cluster_params.get('structure', [])))

            return substructure_nodes

        return {'nodes': _get_substructure_nodes(dsl_full_scheme.get('structure', []))}

    def _get_clusters(self, dsl_full_scheme: dict) -> dict:
        def _get_substructure_clusters(substructure: list, parent_cluster_id: str = '') -> dict:
            substructure_clusters: dict = {}
            clusters_count: int = 0
            nodes_count: int = 0

            substructure_item: dict
            for substructure_item in substructure:
                cluster_params: dict = substructure_item.get('cluster', {})
                node_params: dict = substructure_item.get('node', {})

                if cluster_params:
                    working_cluster_params: dict = cluster_params.copy()
                    cluster_structure: list = working_cluster_params.pop('structure', [])

                    working_cluster_params = self._merge_element_params(
                        'cluster',
                        working_cluster_params,
                        dsl_full_scheme
                    )

                    clusters_count += 1

                    cluster_id: str

                    if parent_cluster_id:
                        cluster_id = f'{parent_cluster_id}_{clusters_count}'

                    else:
                        cluster_id = f'{clusters_count}'

                    if clusters_count == 1:
                        substructure_clusters['clusters'] = {}

                    substructure_clusters['clusters'].update(
                        {cluster_id: _get_substructure_clusters(cluster_structure, cluster_id)}
                    )

                    substructure_clusters['clusters'][cluster_id].update(working_cluster_params)

                elif node_params:
                    if parent_cluster_id:
                        node_id: str = node_params.get('id', '')

                        if node_id:
                            nodes_count += 1

                            if nodes_count == 1:
                                substructure_clusters['nodes'] = []

                            substructure_clusters['nodes'].append(node_id)

            return substructure_clusters

        return _get_substructure_clusters(dsl_full_scheme.get('structure', []))

    def _get_edges(self, dsl_full_scheme: dict) -> dict:
        edges: list = []

        item: dict
        for item in dsl_full_scheme.get('edges', []):
            edge_params: dict = self._merge_element_params('edge', item, dsl_full_scheme)
            edges.append(edge_params)

        return {'edges': edges}

    def _get_subgraphs(self, dsl_full_scheme: dict) -> dict:
        def _get_grid_based_nodes_groups() -> list:
            grid_based_nodes_groups: list = []
            rankdir: str = dsl_full_scheme.get('elements', {}).get('graph', {}).get('rankdir', 'TB')
            grid_lines: list = dsl_full_scheme.get('grid', '').split('\n')
            nodes_lines: dict = {}
            nodes_starts: dict = {}

            index: int
            grid_line: str
            for index, grid_line in enumerate(grid_lines):
                nodes_matches = re.finditer(r'\S+', grid_line)

                for node_match in nodes_matches:
                    node_start: int = node_match.start(0)
                    node_id: str = node_match.group(0)

                    if not nodes_lines.get(index, None):
                        nodes_lines[index] = []

                    if not nodes_starts.get(node_start, None):
                        nodes_starts[node_start] = []

                    if node_id != '-':
                        nodes_lines[index].append(node_id)
                        nodes_starts[node_start].append(node_id)

            if rankdir == 'TB' or rankdir == 'BT':
                grid_based_nodes_groups = list(nodes_lines.values())

            elif rankdir == 'LR' or rankdir == 'RL':
                grid_based_nodes_groups = list(nodes_starts.values())

            return grid_based_nodes_groups

        return {'subgraphs': dsl_full_scheme.get('groups', []) + _get_grid_based_nodes_groups()}

    def _get_dsl_to_gv_intermediate(self, dsl_full_scheme: dict) -> dict:
        dsl_to_gv_intermediate: dict = {}

        for element_type in ('graph', 'node', 'edge'):
            element_type_params: dict = dsl_full_scheme.get('elements', {}).get(element_type, {}).copy()

            if element_type_params:
                element_type_params.pop('classes', None)

                element_type_styles: list or str = element_type_params.pop('style', [])

                if element_type_styles:
                    element_type_params['style'] = self._list_to_csv(self._csv_to_list(element_type_styles))

                dsl_to_gv_intermediate[element_type] = element_type_params

        def _append_positions(nodes: OrderedDict) -> OrderedDict:
            grid_lines: list = dsl_full_scheme.get('grid', '').split('\n')
            nodes_starts: dict = {}

            index: int
            grid_line: str
            for index, grid_line in enumerate(grid_lines):
                nodes_matches = re.finditer(r'\S+', grid_line)

                for node_match in nodes_matches:
                    node_start: int = node_match.start(0)

                    if not nodes_starts.get(node_start, None):
                        nodes_starts[node_start] = []

                    nodes_starts[node_start].append({'line': index, 'id': node_match.group(0)})

            grid_params = dsl_full_scheme.get('elements', {}).get('grid', {})
            spacing_x = grid_params.get('spacing_x', 500)
            spacing_y = grid_params.get('spacing_y', 200)
            node_position_x: int or float = 0

            if dsl_full_scheme.get('engine', 'dot') == 'fdp':
                spacing_x /= 72
                spacing_y /= 72

            node_start: int
            for node_start in sorted(nodes_starts.keys()):
                node: dict
                for node in nodes_starts[node_start]:
                    node_position_y: int or float = -node['line'] * spacing_y

                    if nodes.get('nodes', {}).get(node['id'], None):
                        if not nodes['nodes'][node['id']].get('pos', None):
                            if isinstance(node_position_x, float):
                                node_position_x = float('{0:.2f}'.format(node_position_x))

                            if isinstance(node_position_y, float):
                                node_position_y = float('{0:.2f}'.format(node_position_y))

                            nodes['nodes'][node['id']]['pos'] = f'{node_position_x}, {node_position_y}!'

                node_position_x += spacing_x

            return nodes

        dsl_to_gv_intermediate.update (
            {
                **_append_positions(self._get_nodes(dsl_full_scheme)),
                **self._get_clusters(dsl_full_scheme),
                **self._get_edges(dsl_full_scheme),
                **self._get_subgraphs(dsl_full_scheme)
            }
        )

        return dsl_to_gv_intermediate

    def generate_graphviz_source(self, dsl_full_scheme: dict) -> str:
        def _serialize_clusters(clusters: dict) -> str:
            serialized_clusters: str = ''

            cluster_id: str
            for cluster_id in clusters.keys():
                serialized_clusters += f'subgraph cluster_{cluster_id}' + ' {\n'

                cluster_params: dict = clusters[cluster_id].copy()
                nodes: list = cluster_params.pop('nodes', [])
                nested_clusters: dict = cluster_params.pop('clusters', {})

                serialized_clusters += self._serialize_multiple_lines(cluster_params)

                node_id: str
                for node_id in nodes:
                    serialized_clusters += f'"{node_id}";' + '\n'

                serialized_clusters += _serialize_clusters(nested_clusters)

                serialized_clusters += '}\n'

            return serialized_clusters

        dsl_to_gv_intermediate: dict = self._get_dsl_to_gv_intermediate(dsl_full_scheme)
        gv_output: str = 'digraph {\n'

        key: str
        for key in dsl_to_gv_intermediate.keys():
            if key in ('graph', 'node', 'edge'):
                gv_output += self._serialize_single_line(key, dsl_to_gv_intermediate[key])

            elif key == 'nodes':
                node_id: str
                for node_id in dsl_to_gv_intermediate[key].keys():
                    gv_output += self._serialize_single_line(f'"{node_id}"', dsl_to_gv_intermediate[key][node_id])

            elif key == 'clusters':
                gv_output += _serialize_clusters(dsl_to_gv_intermediate[key])

            elif key == 'edges':
                item: dict
                for item in dsl_to_gv_intermediate[key]:
                    edge_params: dict = item.copy()

                    edge_nodes: str = f'"{edge_params.pop("tail", "")}" -> "{edge_params.pop("head", "")}"'

                    if edge_params:
                        def _serialize_edge_label(edge_label: str or dict) -> str:
                            serialized_edge_label: str = ''

                            if isinstance(edge_label, dict):
                                serialized_edge_label = '<'

                                label_protocol: str = edge_label.get('protocol', '')

                                if label_protocol:
                                    serialized_edge_label += f'<b>{label_protocol}</b>'

                                label_data: str = edge_label.get('data', '')

                                if label_data:
                                    if label_protocol:
                                        serialized_edge_label += '<br />'

                                    serialized_edge_label += label_data

                                serialized_edge_label += '>'

                            elif isinstance(edge_label, str):
                                serialized_edge_label = edge_label

                            return serialized_edge_label

                        edge_label = edge_params.pop('label', '')

                        if edge_label:
                            edge_params['label'] = _serialize_edge_label(edge_label)

                        edge_xlabel = edge_params.pop('xlabel', '')

                        if edge_xlabel:
                            edge_params['xlabel'] = _serialize_edge_label(edge_xlabel)

                        gv_output += self._serialize_single_line(edge_nodes, edge_params)

                    else:
                        gv_output += edge_nodes + ';\n'

            elif key == 'subgraphs':
                subgraph: list
                for subgraph in dsl_to_gv_intermediate[key]:
                    gv_output += 'subgraph {\nrank = "same";\n';

                    node_id: str
                    for node_id in subgraph:
                        gv_output += f'"{node_id}";' + '\n'

                    gv_output += '}\n'

        gv_output += '}\n'

        return gv_output
