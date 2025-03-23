import random
import re
import string
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


def generate_random_string(size: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=size))


class EChartsBlockProcessor(BlockProcessor):
    RE_FENCE_START = re.compile(r"^\s*[+]{3}echarts\s*")
    RE_FENCE_END = re.compile(r"\s*[+]{3}\s*$")

    in_block = False
    block = ""

    def test(self, parent, block):
        return self.in_block or re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        self.in_block = True
        while blocks:
            self.block += "\n" + blocks.pop(0).strip()
            if self.RE_FENCE_END.search(self.block):
                self.in_block = False

                self.block = self.RE_FENCE_START.sub("", self.block)
                self.block = self.RE_FENCE_END.sub("", self.block)
                # keep only the js object
                self.block = self.block[
                    self.block.index("{") : (self.block.rindex("}") + 1)
                ]

                div_id = generate_random_string(6)
                div = etree.SubElement(parent, "div")
                div.set("id", div_id)
                div.set("class", "echarts")
                div.set("style", "width:100%;height:400px;")

                script = etree.SubElement(parent, "script")
                script.set("type", "text/javascript")
                script.set("defer", "true")

                script.text = f"""
                const target{div_id} = document.getElementById('{div_id}');
                const chart{div_id} = echarts.init(target{div_id}, 'shadcn', {{ renderer: 'canvas' }});
                chart{div_id}.setOption({self.block});
                window.addEventListener('resize', function() {{ chart{div_id}.resize(); }});
                const observer{div_id} = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            console.log("Target is visible!");
                            chart{div_id}.resize();
                            observer.disconnect(); // Stop observing if you want a one-time trigger
                        }}
                    }});
                }});

                observer{div_id}.observe(target{div_id});
                """

                self.block = ""


class EChartsExtension(Extension):
    """Custom extension to register the ECharts BlockProcessor"""

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            EChartsBlockProcessor(md.parser),
            "echarts.beta",
            20.0,
        )


# Register the extension in Python-Markdown
def makeExtension(**kwargs):
    return EChartsExtension(**kwargs)
