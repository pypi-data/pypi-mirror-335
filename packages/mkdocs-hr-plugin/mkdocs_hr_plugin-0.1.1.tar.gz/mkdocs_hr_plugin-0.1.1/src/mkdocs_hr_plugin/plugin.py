import os
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options

class HRPlugin(BasePlugin):
    def on_post_page(self, output, page, config):
        """在页面渲染后注入我们的 JS 和 CSS"""
        # 获取资源文件的路径
        plugin_dir = os.path.dirname(os.path.realpath(__file__))
        js_path = os.path.join(plugin_dir, 'assets', 'extra.js')
        css_path = os.path.join(plugin_dir, 'assets', 'extra.css')

        # 读取 JS 和 CSS 文件内容
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # 在 </head> 标签前注入 CSS
        if '</head>' in output:
            css_inject = f'<style>{css_content}</style></head>'
            output = output.replace('</head>', css_inject)

        # 在 </body> 标签前注入 JS
        if '</body>' in output:
            js_inject = f'<script>{js_content}</script></body>'
            output = output.replace('</body>', js_inject)

        return output