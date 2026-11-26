# shadowrocket-rules

## DIRECT rules / 直连规则

- 唯一规则源：[direct.sgmodule](direct.sgmodule)（Shadowrocket）。
- 自动生成：[clash/direct.list](clash/direct.list)（Mihomo / Clash Verge，classical、text 格式）。
- 以后只修改 `direct.sgmodule` 中的 `[Rule]` 段，提交至 main 后 GitHub Actions 自动同步 Clash 文件。不要手动修改生成文件。
- 本地生成：`python3 sync_direct.py`；检查：`python3 sync_direct.py --check`。
- 当前转换支持 DOMAIN 和 DOMAIN-SUFFIX 的 DIRECT 规则；遇到不支持的语法会报错而不是静默丢弃。
- Clash 的 rule-provider 应使用 `behavior: classical`、`format: text`，并通过 `RULE-SET,<provider>,DIRECT` 指定策略。
- 原有订阅 URL 不变；客户端需刷新规则后生效。

AI ISP 模块 `ai-isp.sgmodule` 独立维护，不参与直连规则转换。
