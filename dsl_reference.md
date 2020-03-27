# Archeme DSL Quick Reference

Unlike the main documentation, this quick reference is intended for people who already have experience working with Archeme, and need to quickly refresh one or another Archeme DSL construction in their memory.

Code snippets shown here are **not** strong and valid YAML. They use the following patterns:

* `|` between parameters or values means “or”;
* `...` means an arbitrary number of lines of code;
* words enclosed in `<` and `>` are not used unchanged, but only indicate types of parameters or values;
* all parameters are optional unless otherwise is noted in a comment.

## Common Settings

```yaml
engine: dot|neato|fdp                             # `dot` is default
elements:
    graph:
        <graph_attribute>: <value>
        ...
    node:
        <node_attribute>: <value>
        ...
        classes:
            <class_name>:                         # required if `classes` are specified, similarly below
                <node_attribute>: <value>         # required if `class_name` is specified, similarly below
                ...
            ...
    edge:
        <edge_attribute>: <value>
        ...
        classes:
            <class_name>:
                <edge_attribute>: <value>
                ...
            ...
    cluster:
        <cluster_attribute>: <value>
        ...
        classes:
            <class_name>:
                <cluster_attribute>: <value>
                ...
            ...
    grid:
        spacing_x: 500                            # default value, in points
        spacing_y: 200                            # default value, in points
```

### Single Scheme Description

```yaml
structure:
    - node:
        id: <node_id>                             # required for a node
        <node_attribute>: <value>
        ...
        class:
            - <class_name>
            ...
    ...
    - cluster:
        structure:                                # each cluster must have nested structure
            ...
        <cluster_attribute>: <value>
        ...
        class:
            - <class_name>
            ...
    ...
edges:
    -   tail: <node_id>                           # required for an edge
        head: <node_id>                           # required for an edge
        <edge_attribute>: <value>
        ...
        label|xlabel:                             # here the extended syntax is shown
            protocol: <protocol_name>
            data: <data_description>
        class:
            - <class_name>
            ...
                                                  # grid is needed if the `neato` or `fdp` engine is used
                                                  # `|` after `grid: ` means a multiline value
                                                  # use `-` to skip one grid step
grid: |
    <node_id>    -    ...
    ...
groups:                                           # supported only if the `dot` engine is used
    -   - <node_id>
        - <node_id>
        ...
    ...
```

### Combining Multiple Schemes

```yaml
structure:
    - module:
        id: <module_id>                           # required for a module
        description: {...} | file: <path>         # if both are specified, only `description` is used
        exclude:
            - <node_id>
            ...
    ...
edges:
    ...
grid:
    ...
groups:
    ...
```
