---
title: Apache ECharts
summary: An Open Source JavaScript Visualization Library
---

[Reference](https://echarts.apache.org/en/index.html){: .reference }

The theme provides an alpha version of an `echarts` plugin. From a `js` config it basically plots charts through the Apache ECharts library. Here is the basic syntax:

```md
+++echarts
{ 
  // echarts config 
}
+++
```

Currently, the plugin does not support dark mode.


!!! warning "Important"
    The `js` config is passed to the `.setOption` method. The plugin crops the input so that it keeps the outtermost curly braces (`{` and `}`) and removes what is outside. You can look at the library [API](https://echarts.apache.org/en/option.html).

!!! info "Tip"
    You can either inline all the config within the block or insert snippets from file thanks to the [`pymdownx.snippets` plugin](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/).


    <div class="codehilite"><pre><span></span><code>+++echarts
      &ndash;&ndash;8<-- "example.js"
    +++
    </code></pre></div>


    

## Line


/// tab | Output

+++echarts
--8<-- "docs/assets/echarts/line.js"
+++

///


/// tab | Code

~~~md
+++echarts
--8<-- "docs/assets/echarts/line.js"
+++
~~~

///


## Bars

/// tab | Output

+++echarts
--8<-- "docs/assets/echarts/bars.js"
+++

///


/// tab | Code

~~~md
+++echarts
--8<-- "docs/assets/echarts/bars.js"
+++
~~~

///


## Pie

/// tab | Output

+++echarts
--8<-- "docs/assets/echarts/pie.js"
+++

///


/// tab | Code

~~~md
+++echarts
--8<-- "docs/assets/echarts/pie.js"
+++
~~~

///


## Scatter

/// tab | Output

+++echarts
--8<-- "docs/assets/echarts/scatter.js"
+++

///


/// tab | Code

~~~md
+++echarts
--8<-- "docs/assets/echarts/scatter.js"
+++
~~~

///

## Radar

/// tab | Output

+++echarts
--8<-- "docs/assets/echarts/radar.js"
+++

///


/// tab | Code

~~~md
+++echarts
--8<-- "docs/assets/echarts/radar.js"
+++
~~~

///



