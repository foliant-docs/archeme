import re
from yaml import dump, load, Loader
from pathlib import Path


class MergeMultipleSchemes(object):
    def _update_grid_nodes(self, grid: str, module_id: str, nodes_to_exclude: list) -> str:
        grid_lines: list = grid.split('\n')
        nodes_lines: dict = {}
        nodes_starts: dict = {}

        index: int
        grid_line: str
        for index, grid_line in enumerate(grid_lines):
            nodes_matches = re.finditer(r'\S+', grid_line)

            for node_match in nodes_matches:
                position: int = node_match.start(0)
                node_id: str = node_match.group(0)

                if not nodes_lines.get(index, None):
                    nodes_lines[index]: list = []

                if not nodes_starts.get(position, None):
                    nodes_starts[position]: list = []

                nodes_lines[index].append(node_id)
                nodes_starts[position].append(node_id)

        updated_nodes_lines: dict = {}

        line_number: int
        for line_number in nodes_lines.keys():
            updated_nodes: list = []

            node_id: str
            for node_id in nodes_lines[line_number]:
                if node_id == '-':
                    if not node_id in updated_nodes:
                        updated_nodes.append(node_id)

                elif node_id not in nodes_to_exclude:
                    updated_nodes.append(f'{module_id}.{node_id}')

            updated_nodes_lines[line_number] = updated_nodes

        updated_nodes_starts: dict = {}
        module_id_length = len(module_id)

        index: int
        position: int
        for index, position in enumerate(sorted(nodes_starts.keys())):
            updated_nodes: list = []

            node_id: str
            for node_id in nodes_starts[position]:
                if node_id == '-':
                    if not node_id in updated_nodes:
                        updated_nodes.append(node_id)

                elif node_id not in nodes_to_exclude:
                    updated_nodes.append(f'{module_id}.{node_id}')

            updated_nodes_starts[position + index*module_id_length] = updated_nodes

        updated_grid: str = ''

        line_number: int
        for line_number in sorted(nodes_lines.keys()):
            updated_grid_line: str = ''

            position: int
            for position in sorted(updated_nodes_starts.keys()):
                updated_node_id: str = ''

                node_id: str
                for node_id in updated_nodes_lines[line_number]:
                    if node_id != '-' and node_id in updated_nodes_starts[position]:
                        updated_node_id = node_id
                        break

                if not updated_node_id:
                    updated_node_id = '-'

                updated_grid_line += ' ' * (position - len(updated_grid_line)) + updated_node_id

            updated_grid += updated_grid_line + '\n'

        return updated_grid

    def _update_module(self, module_id: str, module: dict, nodes_to_exclude: list) -> dict:
        def _update_structure(structure: list) -> list:
            updated_structure: list = []

            item: dict
            for item in structure:
                node_params: dict = item.pop('node', {})
                cluster_params: dict = item.pop('cluster', {})

                if node_params:
                    node_id: str = node_params.pop('id', '')

                    if node_id:
                        if node_id in nodes_to_exclude:
                            continue

                        node_params['id'] = f'{module_id}.{node_id}'

                    updated_structure.append({'node': node_params})

                elif cluster_params:
                    cluster_structure: list = _update_structure(cluster_params.pop('structure', []))

                    if cluster_structure:
                        cluster_params['structure'] = cluster_structure
                        updated_structure.append({'cluster': cluster_params})

            return updated_structure

        structure: list = module.pop('structure', [])

        if structure:
            module['structure'] = _update_structure(structure)

        edges: list = module.pop('edges', [])

        if edges:
            updated_edges: list = []

            edge_params: dict
            for edge_params in edges:
                tail: str = edge_params.pop('tail', '')
                head: str = edge_params.pop('head', '')

                if tail:
                    if tail in nodes_to_exclude:
                        continue

                    edge_params['tail'] = f'{module_id}.{tail}'

                if head:
                    if head in nodes_to_exclude:
                        continue

                    edge_params['head'] = f'{module_id}.{head}'

                updated_edges.append(edge_params)

            module['edges'] = updated_edges

        groups: list = module.pop('groups', [])

        if groups:
            updated_groups: list = []

            group: list
            for group in groups:
                updated_group: list = []

                node_id: str
                for node_id in group:
                    if node_id not in nodes_to_exclude:
                        updated_group.append(f'{module_id}.{node_id}')

                if updated_group:
                    updated_groups.append(updated_group)

            module['groups'] = updated_groups

        grid: str = module.pop('grid', '')

        if grid:
            module['grid'] = self._update_grid_nodes(grid, module_id, nodes_to_exclude)

        return module

    def _merge_grids(self, scheme_grid: str, modules_grids: dict) -> str:
        # Get line numbers and starts of scheme grid elements

        scheme_grid_lines: list = scheme_grid.split('\n')

        if not scheme_grid_lines[-1]:
            scheme_grid_lines.pop()

        scheme_elements_lines: dict = {}
        scheme_elements_starts: dict = {}

        index: int
        scheme_grid_line: str
        for index, scheme_grid_line in enumerate(scheme_grid_lines):
            scheme_elements_matches = re.finditer(r'\S+', scheme_grid_line)

            for scheme_element_match in scheme_elements_matches:
                scheme_element_position: int = scheme_element_match.start(0)
                scheme_element_id: str = scheme_element_match.group(0)

                if not scheme_elements_lines.get(index, None):
                    scheme_elements_lines[index] = []

                if not scheme_elements_starts.get(scheme_element_position, None):
                    scheme_elements_starts[scheme_element_position] = []

                scheme_elements_lines[index].append(scheme_element_id)
                scheme_elements_starts[scheme_element_position].append(scheme_element_id)

        # Get modules properties

        modules_properties = {}
        modules_properties['max_rank']: int = 0
        modules_properties['max_node_id_length']: int = 0

        module_id: str
        for module_id in modules_grids.keys():
            module_grid_lines: list = modules_grids[module_id].split('\n')

            if not module_grid_lines[-1]:
                module_grid_lines.pop()

            modules_properties[module_id]: dict = {}
            modules_properties[module_id]['lines']: dict = {}
            modules_properties[module_id]['starts']: dict = {}
            modules_properties[module_id]['lines_count']: int = len(module_grid_lines)

            index: int
            module_grid_line: str
            for index, module_grid_line in enumerate(module_grid_lines):
                module_nodes_matches = re.finditer(r'\S+', module_grid_line)

                for module_node_match in module_nodes_matches:
                    module_node_position: int = module_node_match.start(0)
                    module_node_id: str = module_node_match.group(0)

                    if len(module_node_id) > modules_properties['max_node_id_length']:
                        modules_properties['max_node_id_length'] = len(module_node_id)

                    if not modules_properties[module_id]['lines'].get(index, None):
                        modules_properties[module_id]['lines'][index]: list = []

                    if not modules_properties[module_id]['starts'].get(module_node_position, None):
                        modules_properties[module_id]['starts'][module_node_position] = []

                    modules_properties[module_id]['lines'][index].append(module_node_id)
                    modules_properties[module_id]['starts'][module_node_position].append(module_node_id)

                    if len(modules_properties[module_id]['starts']) > modules_properties['max_rank']:
                        modules_properties['max_rank'] = len(modules_properties[module_id]['starts'])

        # Update scheme grid

        intermediate_scheme_elements_lines: dict = {}
        intermediate_scheme_elements_starts: dict = {}

        scheme_column_position: int
        for scheme_column_position in sorted(scheme_elements_starts.keys(), reverse=True):
            modules_in_column: set = set(
                scheme_elements_starts[scheme_column_position]
            ).intersection(modules_grids.keys())

            if modules_in_column:
                position_to_update: int
                for position_to_update in sorted(scheme_elements_starts.keys(), reverse=True):
                    if position_to_update == scheme_column_position:
                        intermediate_scheme_elements_starts[
                            position_to_update
                        ] = scheme_elements_starts[position_to_update]

                        scheme_line_number: int
                        for scheme_line_number in sorted(scheme_elements_lines.keys(), reverse=True):
                            module_id: str = ''
                            possible_module_id: set = modules_in_column.intersection(
                                scheme_elements_lines[scheme_line_number]
                            )

                            if possible_module_id:
                                module_id = (list(possible_module_id))[0]

                            if module_id in intermediate_scheme_elements_starts[position_to_update]:
                                intermediate_scheme_elements_starts[position_to_update].remove(module_id)

                                index: int
                                module_nodes_position: int
                                for index, module_nodes_position in enumerate(
                                    sorted(modules_properties[module_id]['starts'])
                                ):
                                    updated_position: int = position_to_update + index*(
                                        modules_properties['max_node_id_length'] + 4
                                    )

                                    if intermediate_scheme_elements_starts.get(updated_position, []):
                                        intermediate_scheme_elements_starts.get(updated_position, []).extend(
                                            modules_properties[module_id]['starts'][module_nodes_position]
                                        )

                                    else:
                                        intermediate_scheme_elements_starts[
                                            updated_position
                                        ] = modules_properties[module_id]['starts'][module_nodes_position]

                            if module_id in scheme_elements_lines[scheme_line_number]:
                                line_number_to_update: int
                                for line_number_to_update in sorted(scheme_elements_lines.keys(), reverse=True):
                                    if line_number_to_update == scheme_line_number:
                                        intermediate_scheme_elements_lines[
                                            line_number_to_update
                                        ] = scheme_elements_lines[line_number_to_update]

                                        intermediate_scheme_elements_lines[line_number_to_update].remove(module_id)

                                        index: int
                                        module_line_number: int
                                        for index, module_line_number in enumerate(
                                            sorted(modules_properties[module_id]['lines'].keys())
                                        ):
                                            if index == 0:
                                                intermediate_scheme_elements_lines[line_number_to_update].extend(
                                                    modules_properties[module_id]['lines'][module_line_number]
                                                )

                                            else:
                                                intermediate_scheme_elements_lines[
                                                    line_number_to_update + index
                                                ] = modules_properties[module_id]['lines'][module_line_number]

                                    elif line_number_to_update > scheme_line_number:
                                        intermediate_scheme_elements_lines[
                                            line_number_to_update + modules_properties[module_id]['lines_count'] - 1
                                        ] = scheme_elements_lines[line_number_to_update]

                                    else:
                                        intermediate_scheme_elements_lines[
                                            line_number_to_update
                                        ] = scheme_elements_lines[line_number_to_update]

                                scheme_elements_lines = intermediate_scheme_elements_lines

                    elif position_to_update > scheme_column_position:
                        intermediate_scheme_elements_starts[
                            position_to_update + modules_properties['max_rank']*(
                                modules_properties['max_node_id_length'] + 4
                            )
                        ] = scheme_elements_starts[position_to_update]

                    else:
                        intermediate_scheme_elements_starts[
                            position_to_update
                        ] = scheme_elements_starts[position_to_update]

                scheme_elements_starts = intermediate_scheme_elements_starts

        # Generate updated scheme grid as string

        updated_scheme_grid: str = ''

        updated_scheme_line_number: int
        for updated_scheme_line_number in sorted(scheme_elements_lines.keys()):
            updated_scheme_grid_line: str = ''

            position: int
            for position in sorted(scheme_elements_starts.keys()):
                updated_node_id: str = ''

                node_id: str
                for node_id in scheme_elements_lines[updated_scheme_line_number]:
                    if node_id != '-' and node_id in scheme_elements_starts[position]:
                        updated_node_id = node_id
                        break

                if not updated_node_id:
                    updated_node_id = '-'

                updated_scheme_grid_line += ' ' * (position - len(updated_scheme_grid_line)) + updated_node_id

            updated_scheme_grid += updated_scheme_grid_line + '\n'

        return updated_scheme_grid

    def _merge_modules(self, scheme: dict) -> dict:
        modules_grids: dict = {}

        structure: list = scheme.pop('structure', [])
        merged_structure: list = []

        item: dict
        for item in structure:
            module_params: dict = item.get('module', {})

            if module_params:
                module_id: str = module_params.get('id', '')

                if module_id:
                    module: dict = module_params.get('description', {})

                    if not module:
                        module_file_path_str: str = module_params.get('file', '')

                        if module_file_path_str:
                            module_file_path: Path = Path(module_file_path_str).resolve()

                            with open(module_file_path) as module_file:
                                module = load(module_file, Loader)

                    module = self._update_module(module_id, module, module_params.get('exclude', []))

                    module_grid: str = module.pop('grid', '')

                    if module_grid:
                        modules_grids[module_id] = module_grid

                    module_structure: list = module.pop('structure', [])
                    merged_structure.extend(module_structure)

                    for key, value in {**scheme, **module}.items():
                        if key in scheme and key in module:
                            if isinstance(value, dict):
                                scheme[key].update(module[key])

                            elif isinstance(value, list):
                                scheme[key].extend(module[key])

                            else:
                                scheme[key] = module[key]

                        elif key in module:
                            scheme[key] = module[key]

            else:
                merged_structure.append(item)

        scheme.update({'structure': merged_structure})

        grid: str = scheme.get('grid', '')

        if grid and modules_grids:
            scheme['grid'] = self._merge_grids(grid, modules_grids)

        return scheme

    def merge_multiple_schemes(self, scheme: dict) -> str:
        return str(
            dump(
                self._merge_modules(scheme),
                allow_unicode=True,
                encoding='utf-8',
                default_flow_style=False,
                indent=4,
                width=1024,
            ),
            encoding='utf-8'
        )
