import os

out_dir = r'd:\AntigravityAbout\GCW\assets\readme'
os.makedirs(out_dir, exist_ok=True)

def make_section(name, title, desc, bg_color, text_color, desc_color, accent_color, number):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="140" viewBox="0 0 1200 140" role="img">
  <!-- Solid vibrant background -->
  <rect width="1200" height="140" rx="16" fill="{bg_color}"/>
  
  <!-- Contrasting left accent bar -->
  <rect x="0" y="20" width="8" height="100" fill="{accent_color}"/>
  
  <text x="60" y="65" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="36" font-weight="900" fill="{text_color}">{title}</text>
  <text x="60" y="100" font-family="-apple-system, sans-serif" font-size="18" font-weight="500" fill="{desc_color}">{desc}</text>
  
  <!-- Faint giant number -->
  <text x="1160" y="145" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="160" font-weight="900" fill="{text_color}" opacity="0.1" text-anchor="end" letter-spacing="-5">0{number}</text>
  
  <!-- Decorative dots on the far right using the accent color (two concentric circles) -->
  <g transform="translate(1100, 50)">
    <circle cx="20" cy="20" r="14" fill="{accent_color}" opacity="0.25"/>
    <circle cx="20" cy="20" r="6" fill="{accent_color}" opacity="1"/>
  </g>
</svg>'''

sections = [
    ('section-orchestration.svg', 'Evidence orchestration', 'The core difference of GCW framework.', '#605CDB', '#FFFFFF', '#E0E7FF', '#60E0BA', '1'),
    ('section-quickstart.svg', 'Quick start', 'Install and begin reconstructing sites.', '#60E0BA', '#0F172A', '#1E293B', '#605CDB', '2'),
    ('section-how-it-works.svg', 'How it works', 'The TEARDOWN to CREATIVE pipeline.', '#3B82F6', '#FFFFFF', '#DBEAFE', '#FBBF24', '3'),
    ('section-docs.svg', 'Documentation', 'Reference guides and QA scenarios.', '#FF705E', '#0F172A', '#1E293B', '#FDF8F0', '4'),
    
    ('section-orchestration-zh.svg', '证据编排', 'GCW 框架的核心差异。', '#605CDB', '#FFFFFF', '#E0E7FF', '#60E0BA', '1'),
    ('section-quickstart-zh.svg', '快速开始', '安装并开始重构网站。', '#60E0BA', '#0F172A', '#1E293B', '#605CDB', '2'),
    ('section-how-it-works-zh.svg', 'GCW 怎样工作', '从 TEARDOWN 到 CREATIVE 的流水线。', '#3B82F6', '#FFFFFF', '#DBEAFE', '#FBBF24', '3'),
    ('section-docs-zh.svg', '文档入口', '参考指南、手册与 QA 场景。', '#FF705E', '#0F172A', '#1E293B', '#FDF8F0', '4')
]

for name, title, desc, bg_color, text_color, desc_color, accent_color, number in sections:
    with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f:
        f.write(make_section(name, title, desc, bg_color, text_color, desc_color, accent_color, number))

print('Created SVG assets.')
