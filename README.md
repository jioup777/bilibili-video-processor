# 视频学习笔记自动生成器

> 🎬 一键将 B 站/YouTube 视频转化为结构化学习笔记，自动上传到飞书文档

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

---

## ✨ 功能特性

- **支持多平台**：B 站 + YouTube 视频
- **智能字幕获取**：
  - YouTube：优先使用官方字幕（更快）
  - B 站：使用 Whisper 语音转录（无官方字幕）
- **智能笔记生成**：使用 GLM-4-Flash 生成结构化学习笔记
- **自动上传飞书**：将笔记自动上传到飞书文档指定节点
- **支持无字幕视频**：即使没有官方字幕也能处理

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 虚拟环境（用于 Whisper）
- B 站 Cookies（用于下载音频）
- GLM API Key（智谱 AI）
- 飞书文档权限

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/bilibili-video-processor.git
cd bilibili-video-processor
```

2. **创建虚拟环境并安装 Whisper**
```bash
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper
```

3. **安装 Python 依赖**
```bash
pip install -r requirements.txt
```

4. **配置 API Key**
```bash
cp config/glm-config.example.json config/glm-config.json
# 编辑 config/glm-config.json，填入你的 GLM API Key
```

5. **配置 B 站 Cookies**
```bash
# 将 cookies.txt 放到项目根目录或 ~/.openclaw/workspace/skills/bilibili-study/cookies.txt
# Cookies 获取方法见 docs/cookies.md
```

### 使用方式

#### 方式 1：命令行使用

```bash
# 处理 B 站视频
python src/main.py --url "https://www.bilibili.com/video/BVxxxxx"

# 处理 YouTube 视频
python src/youtube_processor.py "https://www.youtube.com/watch?v=xxxxx"

# 处理视频并指定飞书节点
python src/main.py --url "https://www.bilibili.com/video/BVxxxxx" \
  --feishu-parent-token "I1GtwmgL4iok6WkfOghcR1uwnld" \
  --feishu-space-id "7566441763399581724"
```

#### 方式 2：作为 OpenClaw Skill 使用

在 OpenClaw 中直接说：
```
帮我分析这个 B 站视频：https://www.bilibili.com/video/BVxxxxx
```

系统会自动完成所有步骤。

#### 方式 3：Python 代码调用

```python
from src.processor import BilibiliVideoProcessor

processor = BilibiliVideoProcessor(
    glm_api_key="your_api_key",
    cookies_path="path/to/cookies.txt"
)

# 处理视频
result = processor.process(
    video_url="https://www.bilibili.com/video/BVxxxxx",
    upload_to_feishu=True,
    feishu_parent_token="I1GtwmgL4iok6WkfOghcR1uwnld"
)

print(f"笔记已生成：{result['feishu_url']}")
```

---

## 📁 项目结构

```
bilibili-video-processor/
├── README.md                 # 项目说明
├── requirements.txt          # Python 依赖
├── SKILL.md                  # OpenClaw Skill 定义
├── LICENSE                   # 开源协议
├── config/
│   ├── glm-config.example.json  # GLM 配置示例
│   └── feishu-config.example.json # 飞书配置示例
├── src/
│   ├── main.py               # 主入口
│   ├── downloader.py         # 音频下载
│   ├── transcriber.py        # Whisper 转录
│   ├── summarizer.py         # GLM 笔记生成
│   └── uploader.py           # 飞书上传
├── docs/
│   ├── cookies.md            # Cookies 获取指南
│   ├── api-setup.md          # API 配置指南
│   └── feishu-setup.md       # 飞书配置指南
├── examples/
│   └── example-notebook.md   # 示例笔记
└── tests/
    └── test_processor.py     # 测试用例
```

---

## 🔧 配置说明

### GLM API 配置

编辑 `config/glm-config.json`：
```json
{
  "api_key": "your_glm_api_key",
  "model": "glm-4-Flash",
  "enabled": true
}
```

获取 API Key：https://open.bigmodel.cn/

### 飞书文档配置

编辑 `config/feishu-config.json`：
```json
{
  "space_id": "7566441763399581724",
  "parent_node_token": "I1GtwmgL4iok6WkfOghcR1uwnld",
  "enabled": true
}
```

### B 站 Cookies

将 cookies.txt 放在项目根目录或指定路径。

获取方法见 [docs/cookies.md](docs/cookies.md)

---

## 📊 性能数据

| 视频时长 | 下载 | 转录 | 生成 | 上传 | 总计 |
|---------|------|------|------|------|------|
| 3 分钟 | 10s | 60s | 5s | 3s | ~80s |
| 12 分钟 | 30s | 180s | 10s | 5s | ~230s |

**Token 消耗**：
- 3 分钟视频：~3000 tokens（约 0.003 元）
- 12 分钟视频：~10000 tokens（约 0.01 元）

---

## 🎯 使用场景

1. **学习笔记**：将教程视频转化为结构化笔记
2. **内容整理**：快速提取视频核心内容
3. **知识管理**：自动归档到飞书知识库
4. **内容创作**：基于视频内容生成文章素材

---

## ⚠️ 注意事项

1. **必须使用虚拟环境**：Whisper 需要特定的 Python 环境
2. **Cookies 有效期**：B 站 Cookies 会过期，需定期更新
3. **API 额度**：GLM API 有免费额度，超出后需付费
4. **网络环境**：需要能访问 B 站和智谱 AI API

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 更新日志

### v1.0.0 (2026-03-08)
- ✨ 初始版本发布
- ✅ 支持 B 站视频音频下载
- ✅ 支持 Whisper 语音转录
- ✅ 支持 GLM-4-Flash 笔记生成
- ✅ 支持飞书文档自动上传

---

## 📄 开源协议

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - AI 助手框架
- [Whisper](https://github.com/openai/whisper) - 语音识别模型
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载工具
- [智谱 AI](https://open.bigmodel.cn/) - GLM 模型提供方

---

## 📮 联系方式

- 项目地址：https://github.com/yourusername/bilibili-video-processor
- 问题反馈：https://github.com/yourusername/bilibili-video-processor/issues
- OpenClaw 社区：https://discord.com/invite/clawd

---

*Made with ❤️ by OpenClaw Community*
