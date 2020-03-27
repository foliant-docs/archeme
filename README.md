# Archeme

Archeme is a tool to describe and visualize schemes and diagrams. It’s designed primarily for architectural schemes.

Archeme may be used as a stand-alone command-line tool, or as a Python package.

To describe schemes and diagrams, Archeme provides YAML-based DSL (domain-specific language).

To draw them, Archeme uses [Graphviz](https://www.graphviz.org/). The engines `dot`, `neato`, and `fdp` are supported.

In fact, Archeme provides some new abstraction level over Graphviz. Unlike PlantUML, Archeme almost doesn’t limit your ability to use the flexible functionality of Graphviz. However, Archeme provides more convenient means to describe elements of the same types using classes, to specify the relative positions of elements, etc. Using YAML as the base of DSL makes it possible to work with diagram descriptions as with data structures—in Archeme itself and in applications integrated with it. So, Archeme can easily combine several scheme descriptions into one.

By using SVG as an output format, you may assign hyperlinks to scheme elements and thereby organize relationships between schemes—for example, in accordance with the [C4 methodology](https://c4model.com/).

## Installation

To install Archeme, run the command:

```bash
$ pip install archeme
```

After installation, the command `archeme` will be available in your system.

## CLI Usage

Currently Archeme provides 2 actions (commands):

* `generate`—to generate graph description that can be drawn with Graphviz from YAML-based DSL source;
* `merge`—to merge (combine, join) multiple DSL sources into a single DSL source.

### The `generate` Command Syntax

Generalized syntax of the `generate` command is the following:

```bash
$ archeme generate [-c|--config <config_file>] -i|--input <input_file> -o|--output <output_file> [-d|--draw <format>]
```

The `-i`/`--input` and `-o`/`--output` arguments are required, other arguments are optional.

The `-i`/`--input` parameter is used to specify YAML-based DSL source.

The `-o`/`--output` parameter points to the output file—graph description for Graphviz.

You may specify an optional config file by using the `-c`/`--config` argument. Both config and scheme description files use the same YAML-based DSL. It’s recommended to use a separate config file to specify some common settings that may be reused in multiple scheme descriptions of the same style. If both config file and scheme description set the parameter of the same name, the value specified in scheme description will override the value specified in config.

If the `-d`/`--draw` argument is given, Archeme will try to call Graphviz to draw an image from generated graph description, and the Graphviz calling command will be displayed. By default, Archeme doesn’t call Graphviz to visualize generated graph descriptions. The `-d`/`--draw` argument may take any output format value allowed by Graphviz (`png`, `svg`, etc.). By default, the `dot` engine is used. You may specify the necessary engine explicitly in DSL, see below.

### The `merge` Command Syntax

Generalized syntax of the `merge` command is more simple:

```bash
$ archeme merge -i|--input <input_file> -o|--output <output_file>
```

The command takes 2 mandatory arguments: `-i`/`--input` for input YAML-based DSL file, and `-o`/`--output` for output YAML-based DSL file. Output files of the `merge` command should be used as input files for the `generate` command. YAML-based DSL is described below.

## YAML-Based DSL

* See also: [Archeme DSL Quick Reference](https://github.com/foliant-docs/archeme/blob/master/dsl_reference.md)

To describe schemes and diagrams, YAML-based DSL is provided.

DSL, same as Graphviz, operates the graph theory terms: so, *graph* is the whole drawing; *node* is a functional component of a scheme or a diagram; *cluster* is a group of nodes that is usually highlighted visually; *edge* is a line that represents a relation between two nodes.

DSL may be used to:

* specify common settings of multiple elements;
* define scheme structure and relations between elements;
* describe each separate element—node, cluster, edge;
* set relative positions of elements;
* describe how it’s needed to combine multiple scheme descriptions into a single one.

### Common Setting

Common settings for multiple elements usually should be specified in the config file.

#### Graphviz Engine

The `engine` parameter sets the certain Graphviz engine to draw images. Archeme supports the `dot`, `neato`, and `fdp` engines. The default engine is `dot`.

Code example:

```yaml
engine: neato
```

You may read about the difference between engines in the [Graphviz documentation](https://www.graphviz.org/about/).

In relation to architectural schemes:

* `dot` is suitable for models with hierarchical relations; using `dot`, you can’t strictly control relative positions of elements—the positions depend of ranks of elements; `dot` supports clusters;
* `neato` allows to set strict fixed positions to each node; it doesn’t support clusters;
* `fdp` is similar to `neato` but it supports clusters; however, if clusters are used, `fdp` re-calculates the positions of nodes, they can’t be strictly fixed.

#### Settings Of Elements

In `elements` section, you may specify common settings of the element of different types—graph, node, cluster, edge. In the simplest case, DSL maps to Graphviz syntax. DSL code example:

```yaml
elements:
    graph:
        newrank: true
        rankdir: TB
    node:
        shape: box
        fixedsize: true
        width: 4
        height: 1
        style:
            - filled
            - rounded
    edge:
        dir: both
        arrowtail: dot
```

This example will be converted into the following description for Graphviz:

```
graph [newrank = "true", rankdir: "TB"]
node [shape = "box", fixedsize = "true", width = "4", height = "1", style = "filled, rounded"]
edge [dir = "both", arrowtail = "dot"]
```

All available parameters for graphs, nodes, edges are described in the [Graphviz documentation](https://www.graphviz.org/doc/info/attrs.html).

In addition to `graph`, `node`, and `edge` parameters, Archeme supports the analogous `cluster` parameter that allows to specify default settings for clusters. Code example:

```yaml
elements:
    cluster:
        labelloc: b
        labeljust: l
        shape: box
```

Note that you may reduce the number of lines of YAML-based DSL code. So, node settings from the example above may look like this:

```yaml
node {shape: box, fixedsize: true, width: 4, height: 1, style: [filled, rounded]}
```

Archeme allows to specify parameters that take lists of values, in different ways. The constructions `style: [filled, rounded]`, `style: filled, rounded`, `style: [filled]`, `style: filled` are valid.

Note that if a node, cluster, or edge has some custom `style` or another parameter with a list of values, it will **fully** override the default `style` or whatever. This is how it works in Graphviz, and Archeme doesn’t change this behavior for compatibility reasons.

For example, if the default `style` for nodes is `[filled, rounded]`, and the custom `style` of some node is `dashed`, only `dashed` will be applied to this node.

To control the settings of elements more flexible, classes are provided.

##### Classes Definition

You may define one or more classes for each type of elements (`node`, `cluster`, `edge`), and then assign any combination of defined classes to any separate element. Code example:

```yaml
elements:
    node:
        fixedsize: true
        penwidth: 3
        classes:
            generic:
                shape: box
                width: 4
                height: 1
                style: rounded
            database:
                shape: cylinder
                width: 3
                height: 3
            external_network:
                shape: circle
                width: 2.5
                height: 2.5
                style: filled
                fillcolor: '#f0f0f0'
```

In this example, 3 classes of nodes with the names `generic`, `database`, and `external_network` are defined. Note that using of classes doesn’t disallow to use global default settings.

##### Grid Settings

To control the relative positions of elements, Archeme provides the ability to describe nodes arrangement as a text grid. In the `elements` section of common settings you may define the horizontal and vertical intervals of the grid step. Code example:

```yaml
elements:
    grid:
        spacing_x: 400
        spacing_y: 250
```

The `spacing_x` parameter sets the horizontal interval and defaults to `500`; the `spacing_y` parameter sets the vertical interval and defaults to `200`. Grid spacing units are *points*; 1 point equals to 1/72 inch.

Note that `neato` and `fdp` engines use different units for the `pos` attribute: points and inches respectively. Archeme takes it into account. If you specify `engine: neato`, do not try to draw the resulting graph description with `fdp`, and vice versa. The `dot` engine doesn’t support positioning at all.

### Scheme Description

To describe a scheme or a diagram, it’s needed to:

* specify scheme structure—define nodes and clusters;
* specify relations between nodes—define edges;
* control the relative positions of nodes:
    * define a text grid, if the `neato` or `fdp` engine is used;
    * specify which nodes should have the same rank, if the `dot` engine is used.

#### Structure

To define nodes and clusters, Archeme DSL provides the `structure` section. You may assign Graphviz attributes and Archeme classes to any node and any cluster. For nodes, the `id` parameter is only required. All other parameters are optional. The `id` parameter is used to assign a text identifier to a certain node.

Simple code example:

```yaml
structure:
    - node:
        id: first
    - node:
        id: second
```

In this example, 2 nodes with the identifiers `first` and `second` are defined.

Note that the value of the `structure` parameter must be a list. If the `dot` engine is used, the order of nodes matters for their positioning. If the `neato` or `fdp` engine is used, the order of nodes doesn’t matter.

Clusters should be specified at the same level as nodes. Each cluster has nested `structure` that may include nodes and nested clusters. Code example:

```yaml
structure:
    - node:
        id: first
    - node:
        id: second
    - cluster:
        structure:
            - node:
                id: third
            - node:
                id: fourth
```

The following code example shows how it’s possible to assign Graphviz attributes and Archeme classes to nodes and clusters:

```yaml
structure:
    - node:
        id: first
        label: The First Node
        class:
            - amazing
            - awesome
    - cluster:
        label: The Wonderful Cluster
        style: filled
        fillcolor: '#cccccc'
        class: wonderful
        structure:
            ...
```

Single class name may be specified as a string; multiple class names should be specified as a list.

Archeme merges attributes of classes. Suppose 2 classes are defined as the following:

```yaml
classes:
    amazing:
        shape: box
        width: 4
        height: 1
        style:
            - rounded
            - filled
    awesome:
        height: 2
        style:
            - dashed
        fillcolor: '#99ccff'
```

If both styles are assigned to some node in the order: `[amazing, awesome]`, the resulting attributes assigned to the node will be:

```yaml
shape: box
width: 4
height: 2
style:
    - rounded
    - filled
    - dashed
fillcolor: '#99ccff'
```

So, the `style` attributes will be combined. Contradicting values of the attributes of the same names will be taken from the last class in the sequence (like `height` in this example).

#### Relations

To show relations between nodes, edges are used. To define a list of edges, use the `edges` section. Simple code example:

```yaml
edges:
    -   tail: first
        head: second
    -   tail: second
        head: third
```

In this example, 2 edges are defined. These edges specify relations between 3 nodes with the identifiers `first`, `second`, and `third`.

Archeme uses directed graphs only. So each edge should have a tail (“source,” “beginning”) and a head (“target,” “ending”). For example, if an edge represents interaction between a client and a server, it will be alright if a tail will be assigned to a client, and a head—to a server. However, client requests and server responses may be shown as two different counter-directed edges.

You may assign Graphviz attributes and classes to edges like in case with nodes and clusters. Example:

```yaml
edges:
    -   tail: first
        head: second
        label: HTTP API
        class: two_arrows
```

Archeme provides extended syntax for the `label` and `xlabel` attributes of edges. You may specify protocol and describe transferred data:

```yaml
    -   tail: first
        head: second
        label:
            protocol: HTTP
            data: Admin API
```

This code will be transformed into the following construction in a graph description:

```
"first" -> "second" [label = <<b>HTTP</b><br />Admin API>];
```

#### Positioning

Archeme implements a powerful concept to control relative positions of scheme elements. Positioning may be described as a multiline text grid. Suppose you have 10 nodes with the identifiers from `first` to `tenth`. Feel free to set their positions in this visual way:

```yaml
grid: |
    -        -    second    sixth
    first         third
                  fourth               eighth
                                       ninth
                  fifth     seventh
                                       -
                                       tenth
```

If the engine `neato` or `fdp` is used, the nodes will be strictly positioned with the `pos` attribute. Positions will be calculated using the values of the `elements.grid.spacing_x` and `elements.grid.spacing_y` parameters. A hyphen (`-`) means skipped step if it’s necessary not to place any nodes to the respective horizontal or vertical coordinate.

Grid steps are defined by start positions of node identifiers. So, the nodes `second`, `third`, `fourth`, and `fifth` from the example will be placed to the third horizontal step of the grid.

The `dot` engine ignores the `pos` attribute, but it allows to place nodes with the same rank to the same hierarchy level of the resulting layout. If the `dot` engine is used, Archeme analyzes a grid and defines groups (subgraphs) of nodes with the same ranks. For the example above and the `elements.graph.rankdir` attribute set to `LR` (left to right), Archeme will generate the following groups:

* `second`, `third`, `fourth`, `fifth`;
* `sixth`, `seventh`;
* `eighth`, `ninth`, `tenth`.

If the `elements.graph.rankdir` attribute is set to `TB` (top to bottom, default in Graphviz), for the example above Archeme will make the following groups:

* `second`, `sixth`;
* `first`, `third`;
* `fourth`, `eighth`;
* `fifth`, `seventh`.

If you don’t plan to use the engines `neato` and `fdp` to draw a certain scheme, and use only `dot`, you don’t need to describe grids. For `dot`, instead of using grids, you may define groups of nodes of the same ranks explicitly. Example of code that represents the last described case:

```yaml
groups:
    -   - second
        - sixth
    -   - first
        - third
    -   - fourth
        - eighth
    -   - fifth
        - seventh
```

### Combining Multiple Schemes

To combine multiple schemes or diagrams into a single one, the `merge` Archeme command is used. Archeme merges multiple scheme descriptions using the concept of modules.

A module is a scheme description that is used as a part of the structure of the resulting combined scheme description. Optionally some nodes of a certain module may be excluded from the resulting combined scheme description.

Each module should have an identifier. To avoid conflicts when some nodes have the same identifiers in different modules, node identifiers are combined with module identifiers in the resulting scheme description. For example, the node `api` from the module `backend` will get the identifier `backend.api` in the resulting combined scheme description.

Archeme works with modules that are described in separate files. To include some module into the resulting scheme structure, you should specify module identifier and module description file. Code example:

```yaml
structure:
    - module:
        id: backend
        file: path/to/backend.yml
    - module:
        id: frontend
        file: path/to/frontend.yml
```

It seems most convenient to describe modules in separate files, if Archeme is used as a stand-alone command-line tool. However, Archeme allows to specify a module description directly as a value of the `description` parameter that should be used instead of the `file` parameter. This way may be preferred when Archeme is used as a Python package in a third-party application.

In this example, 2 modules with the identifiers `backend` and `frontend` are added to the resulting structure.

If you need not to include some module nodes into the resulting structure, use the optional `exclude` parameter:

```yaml
structure:
    - module:
        id: frontend
        file: path/to/frontend.yml
        exclude:
            - client_device
            - cdn
```

In this example, the nodes with the identifiers `client_device` and `cdn` of the module `frontend` will not be taken into account in the resulting combined scheme description.

Feel free to add nodes, clusters, and edges to the resulting scheme description in the usual way:

```yaml
structure:
    - module:
        id: backend
        file: path/to/backend.yml
    - module:
        id: frontend
        file: path/to/frontend.yml
    - node:
        id: middleware
edges:
    -   tail: frontend.application
        head: middleware
    -   tail: middleware
        head: backend.api
```

Archeme provides smart merging of grids. Suppose you need to combine 4 modules with the identifiers `one`, `two`, `three`, and `four`. You may describe a grid that should be used in the resulting scheme description:

```yaml
grid: |
    one      two
    three    four
```

Archeme will generate the resulting grid in which, for example, the leftmost nodes of the module `two` will be placed at the same horizontal position as the leftmost nodes of the module `four`.

When merging modules, Archeme deeply processes the `structure`, `edges`, `grid`, and `groups` parameters of each module. Common parameters for multiple elements such as `engine` and `elements` will be merged using the simplest algorithm. It’s best to specify them in a separate config file that will not be involved in the merge process.

## Examples

Archeme repository includes [some examples](https://github.com/foliant-docs/archeme/tree/master/examples/) of architectural schemes.

Each example is located in its own folder that has the following structure:

* `source/*`—YAML-based DSL sources;
* `target/*`—generated graph descriptions for Graphviz, and resulting PNG images;
* `draw.sh`—shell script that executes the commands which create target files.

PNG images drawn with Graphviz are shown below.

### 1. Foliant Architecture, Simple, Drawn With `neato`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/01_foliant_architecture_simple/)

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/01_foliant_architecture_simple/target/architecture.png)

### 2. Foliant Architecture, Pretty, Drawn With `neato`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/02_foliant_architecture_pretty/)

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/02_foliant_architecture_pretty/target/architecture.png)

### 3. Foliant Architecture, With A Cluster, Drawn With `fdp`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/03_foliant_architecture_with_cluster/)

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/03_foliant_architecture_with_cluster/target/architecture.png)

### 4. Foliant Architecture, With More Clusters, Drawn With `fdp`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/04_foliant_architecture_more_clusters/)

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/04_foliant_architecture_more_clusters/target/architecture.png)

### 5. Foliant Architecture, With Many Nested Clusters, Drawn With `dot`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/05_foliant_architecture_many_nested_clusters/)

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/05_foliant_architecture_many_nested_clusters/target/architecture.png)

### 6. Digital Television System, Two Subsystems, Two Styles, Drawn With `dot`

* [Directory with the example files](https://github.com/foliant-docs/archeme/tree/master/examples/06_digital_tv_architecture/)

#### Style 1

##### Subsystem 1

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_1/ott_dvr_subsystem.png)

##### Subsystem 2

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_1/service_backend.png)

##### Whole System, Reuses Subsystems Descriptions

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_1/combined.png)

#### Style 2

##### Subsystem 1

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_2/ott_dvr_subsystem.png)

##### Subsystem 2

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_2/service_backend.png)

##### Whole System, Reuses Subsystems Descriptions

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/06_digital_tv_architecture/target/style_2/combined.png)

Clouds and client devices icons are made by [iconixar](https://www.flaticon.com/authors/iconixar/).
