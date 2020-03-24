# Archeme

**This document is not ready yet, work is in progress.**

Archeme is a tool to describe and visualize schemes and diagrams. It’s designed primarily for architectural schemes.

Archeme may be used as a stand-alone command-line tool, or as a Python package.

To describe schemes and diagrams, Archeme provides YAML-based DSL (domain-specific language).

To draw them, Archeme uses [Graphviz](https://www.graphviz.org/). The engines `dot`, `neato`, and `fdp` are supported.

In fact, Archeme provides some new abstraction level over Graphviz. Unlike PlantUML, Archeme almost doesn’t limit your ability to use the flexible functionality of Graphviz. However, Archeme provides more convenient means to describe elements of the same type using classes, to specify the relative positions of elements, etc. Using YAML as the base of DSL makes it possible to work with diagram descriptions as with data structures—in Archeme itself and in applications integrated with it. So, Archeme can easily combine several scheme descriptions into one.

By using SVG as an output format, you may assign hyperlinks to scheme elements and thereby organize relationships between schemes—for example, in accordance with the [C4 methodology](https://c4model.com/).

## Installation

To install Archeme, run the command:

```bash
$ pip install archeme
```

After installation, the command `archeme` will be available in your system.

## CLI Usage

Currently Archeme provides 2 actions (commands):

* `generate`—to generate graph description to draw with Graphviz from YAML-based DSL source;
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

If the `-d`/`--draw` argument is given, Archeme will try to call Graphviz to draw an image from generated graph description, and the Graphviz calling command will be displayed. By default, Archeme doesn’t call Graphviz to visualize generated graph descriptions. The `-d`/`--draw` argument may take any value allowed by Graphviz (`png`, `svg`, etc.). By default, the `dot` engine is used. You may specify the necessary engine explicitly in DSL, see below.

### The `merge` Command Syntax

Generalized syntax of the `merge` command is more simple:

```bash
$ archeme merge -i|--input <input_file> -o|--output <output_file>
```

The command takes 2 mandatory arguments: `-i`/`--input` for input YAML-based DSL file, `-o`/`--output` for output YAML-based DSL file. Output files of the `merge` command should be used as input files of the `generate` command. YAML-based DSL is described below.

## YAML-Based DSL

To describe schemes and diagrams, YAML-based DSL is provided.

DSL, same as Graphviz, operates the graph theory terms: so, *graph* is the whole drawing; *node* is a functional component of a scheme or a diagram; *cluster* is a group of nodes; *edge* is a line that represents a relation between two nodes.

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

You may read about the difference between engines in the [Graphviz documentation](https://www.graphviz.org/about/). In relation to architectural schemes:

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

Archeme allows to specify parameters with lists of values in different ways. The constructions `style: [filled, rounded]`, `style: filled, rounded`, `style: [filled]`, `style: filled` are valid.

Note that if a node, cluster, or edge has some custom `style` or another parameter with a list of values, it will **fully** override the default `style` or whatever. This is how it works in Graphviz, and Archeme doesn’t change this behavior.

For example, if the default `style` for nodes is `[filled, rounded]`, and the custom `style` of some node is `dashed`, only `dashed` will be applied to this node.

##### Classes Definition

To control the settings of elements more flexible, classes are provided.

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

To control the relative positions of elements, Archeme provides the ability to describe nodes arrangement as a text  grid. In the `elements` section of common settings you may define the horizontal and vertical intervals of the grid step. Code example:

```yaml
elements:
    grid:
        spacing_x: 400
        spacing_y: 250
```

The `spacing_x` parameter sets the horizontal interval and defaults to `500`; the `spacing_y` parameter sets the vertical interval and defaults to `200`. Grid spacing units are *points*; 1 point equals to 1/72 inch.

Note that `neato` and `fdp` engines use different units for the `pos` attribute: points and inches respectively. Archeme takes it into account. If you specify `engine: neato`, do not try to draw the resulting graph description with `fdp`, and vice versa. The `dot` engine doesn’t support positioning at all.

### Scheme Description

**TODO**

### Combining Multiple Schemes

**TODO**

## Examples

Archeme repository includes [some examples](https://github.com/foliant-docs/archeme/tree/master/examples) of architectural schemes.

Each example is located in its own folder that has the following structure:

* `source/*`—YAML-based DSL sources;
* `target/*`—generated graph descriptions for Graphviz, resulting PNG images;
* `draw.sh`—shell script that executes the commands which create target files.

PNG images are shown below.

### 1. Foliant Architecture, Simple, Drawn With `neato`

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/01_foliant_architecture_simple/target/architecture.png)

### 2. Foliant Architecture, Pretty, Drawn With `neato`

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/02_foliant_architecture_pretty/target/architecture.png)

### 3. Foliant Architecture, With A Cluster, Drawn With `fdp`

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/03_foliant_architecture_with_cluster/target/architecture.png)

### 4. Foliant Architecture, With More Clusters, Drawn With `fdp`

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/04_foliant_architecture_more_clusters/target/architecture.png)

### 5. Foliant Architecture, With Many Nested Clusters, Drawn With `dot`

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/05_foliant_architecture_many_nested_clusters/target/architecture.png)

### 6. Digital Television System, Two Subsystems, Two Styles, Drawn With `dot`

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
