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

**TODO, not ready yet.**

## Examples

### 1. Foliant Architecture, Simple, Drawn With Neato

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/01_foliant_architecture_simple/target/architecture.png)

### 2. Foliant Architecture, Pretty, Drawn With Neato

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/02_foliant_architecture_pretty/target/architecture.png)

### 3. Foliant Architecture, With A Cluster, Drawn With Fdp

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/03_foliant_architecture_with_cluster/target/architecture.png)

### 4. Foliant Architecture, With More Clusters, Drawn With Fdp

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/04_foliant_architecture_more_clusters/target/architecture.png)

### 5. Foliant Architecture, With Many Nested Clusters, Drawn With Dot

![](https://raw.githubusercontent.com/foliant-docs/archeme/master/examples/05_foliant_architecture_many_nested_clusters/target/architecture.png)

### 6. Digital Television System, Two Subsystems, Two Styles, Drawn With Dot

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
