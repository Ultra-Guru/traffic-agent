# Traffic Agent — SPEC v2.0 参考实现

[![CI](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/ci.yml)
[![Mutation](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/mutate.yml/badge.svg)](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/mutate.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 移动端流量调试 Agent：以小黄鸟（HttpCanary / Reqable）的功能集为**基线**，
> 在 **MITM 解密深度、移动端原生改包、AI 辅助规则、差分回归、本地隐私闭环**
> 五个维度建立**代差**。本仓库是 SPEC v2.0 的 Python 参考实现（L1–L5 引擎层），
> Android 产品化路径见下方路线图。

---

## 架构

```
L1   traffic_agent.capture      抓包数据面（VpnService / root 多通道 + 协议解析）
  VpnService → TUN → L4 代理
                  ↓
L1.5 traffic_agent.transform    流量变换层
  规则引擎（重写/注入/屏蔽） · 断点引擎（拦截/编辑/放行）
  网络条件模拟器（延迟/丢包/限速/超时） · 脚本沙箱（白名单 API）
                  ↓
L2   traffic_agent.events       事件总线（TrafficEvent / TransformApplied / ...）
                  ↓
L3   traffic_agent.analysis     分析流水线（差分回归 · 二进制协议推断）
                  ↓
L4   traffic_agent.agent        Agent 控制面（19 个工具 + 风险门控 + 审计）
                  ↓
L5   traffic_agent.export       呈现与导出（HAR / PCAP / SSLKEYLOGFILE / 代码生成）
```

**所有变换产生 `TransformApplied` 事件（含前后 sha256）**，Agent 与审计系统可精确追溯
“这条响应被哪条规则改了什么”。

## 五个任务看板

本仓库按五大任务看板推进（每个 Issue = 一块看板，含验收清单与变异验证门槛）：

| 看板 | 模块 | 范围（SPEC v2.0） | Issue |
|---|---|---|---|
| **TB1** | `session` / `events` / `capture` | 五元组会话指纹、事件总线、HTTP/1.x、TLS SNI、DNS、WebSocket、QUIC Initial、HTTP/2、gRPC 解析、多通道引擎、root 能力探测、QUIC 旁路诚实报告（I9） | [#1](../../issues/1) |
| **TB2** | `transform` | 重写引擎（8 类 Action + ReDoS 防护）、移动端原生断点引擎、弱网模拟器、脚本沙箱（白名单 API + AST 校验） | [#2](../../issues/2) |
| **TB3** | `analysis` | 差分回归（I8：抓包即测试基线）、二进制协议推断（长度前缀 + 位置分类） | [#3](../../issues/3) |
| **TB4** | `agent` | 风险门控（LOW/MEDIUM/HIGH 分级 + HIGH 每次确认 + 审计）、19 个 Agent 工具（含 root 增量：`exec_root_shell` 默认禁用 + 命令白名单） | [#4](../../issues/4) |
| **TB5** | `export` | HAR 1.2（默认脱敏）、PCAP、SSLKEYLOGFILE、cURL/Python/JS/Go 代码生成、变异验证流水线 | [#5](../../issues/5) |

## 快速开始

```bash
pip install -e ".[dev]"
python -m pytest -q                # 单元测试（Python 3.10–3.12）
python scripts/mutation_score.py --board TB2 --paths traffic_agent/transform --min-score 55
```

### 抓包与诚实报告（L1）

```python
from traffic_agent.capture.engine import CaptureEngine, CaptureMode, probe_root
from traffic_agent.events import EventBus
from traffic_agent.session import ConnectionSession, Direction, SessionStore

bus, store = EventBus(), SessionStore()
engine = CaptureEngine(store, bus, mode=CaptureMode.VPN)
engine.start()
conn = store.add(ConnectionSession("10.0.0.2", 50000, "93.184.216.34", 443, "tcp"))
engine.ingest(conn, Direction.UPSTREAM, raw_bytes)   # 自动分类：dns / tls_client_hello / http1_request / quic_initial / raw
print(CaptureEngine.visibility_report(conn))          # I9：QUIC 旁路诚实标注
```

### 移动端原生断点（对 Reqable 移动端砍掉能力的直接超越）

```python
from traffic_agent.transform.breakpoint import BreakpointEngine
from traffic_agent.transform.rewrite import RuleMatcher

bps = BreakpointEngine(bus=bus)
bps.set_breakpoint(RuleMatcher(host="api.example.com", path="/pay"), direction="both")
hit = bps.intercept("up", request=request)   # 挂起
resolved = bps.resolve(hit.hit_id, "modify", modified_request=edited)  # 编辑后放行
```

### Agent 辅助规则生成（I7：说人话生成重写规则）

```python
from traffic_agent.agent.tools import ToolContext, build_registry
from traffic_agent.agent.gating import ToolGate

ctx = ToolContext(store=store, bus=bus, rewrite=rewrite_engine, ...)
registry = build_registry(ctx, ToolGate())
result = registry.invoke(
    "create_rewrite_rule",
    {"matcher": {"host": "api.example.com"},
     "action": {"kind": "replace_body", "search": '"vip":false', "replacement": '"vip":true'}},
    confirmed=True,   # MEDIUM 风险：首次确认后本会话免确认
)
print(result.data["impact"])   # I10：影响面预判（匹配数 / 涉及 Host / 敏感端点）
```

### 差分回归（I8：抓包即测试基线）

```python
from traffic_agent.analysis.diff import DiffEngine

report = DiffEngine().diff(baseline_sessions, candidate_sessions)
print(report.counts())      # {'added': 1, 'removed': 0, 'status_changed': 2, ...}
print(report.breaking())    # 破坏兼容性的变更（字段消失、新增 4xx/5xx）
```

### 风险门控原则（v2.0 §3）

| 风险 | 行为 | 示例工具 |
|---|---|---|
| LOW | 自动放行 | `query_connections` / `compare_sessions` / `check_root_capabilities` |
| MEDIUM | 首次确认后本会话免确认 | `create_rewrite_rule` / `set_breakpoint` / `export_sslkeylog` |
| HIGH | **每次调用都要确认** | `inject_script` / `replay_sequence` / `deploy_system_ca` / `set_stealth_mode` |
| HIGH+默认禁用 | 必须显式开启 + 命令白名单 | `exec_root_shell`（仅 `ps` / `id` / `getenforce` / `iptables -L`，禁止管道/重定向） |

## 变异验证（GitHub Actions）

- **`ci`**：push / PR 触发，Python 3.10–3.12 矩阵跑 `pytest`。
- **`mutation-verification`**：push 到 main / 手动触发，五个看板对应的模块**并行**运行
  [mutmut](https://mutmut.readthedocs.io/)，产出 `mutation-<BOARD>.json`（Artifact）
  并在分数低于阈值（55%）时失败。

```
MUTATION_RESULT board=TB2 killed=412 survived=63 timeout=7 ... score=0.871
```

计分口径：`(killed + timeout) / (killed + survived + timeout)`。

## 功能对等矩阵（节选）

| 小黄鸟能力 | 本实现 | 增强/超越 |
|---|---|---|
| HTTP/1.x、TLS(SNI)、DNS、TCP/UDP | `capture/parsers.py` | 同基线 |
| WebSocket | `decode_ws_frame` | 帧级编解码（可注入回放） |
| QUIC / HTTP/3 | `is_quic_initial_packet` | **旁路诚实标注**（I9），而非静默丢失 |
| 断点（旧版有 / Reqable 移动端砍掉） | `transform/breakpoint.py` | **移动端原生可用**，不依赖桌面协同 |
| 重写（Map Remote / Map Local / Mock） | `transform/rewrite.py` | 规则可由 Agent 从自然语言生成（I7）+ 影响面预判（I10） |
| 脚本引擎 | `transform/sandbox.py` | 白名单 API + AST 校验，脚本不能成为逃逸通道 |
| 弱网模拟 | `transform/netcond.py` | 与重写规则联动（命中 `/pay` 施加 5s 延迟） |
| HAR / PCAP / SSLKEYLOGFILE / cURL | `export/*` | 默认脱敏；代码生成支持 Python/JS/Go |
| 数据对比 | `analysis/diff.py` | **差分回归报告**（语义级归因 + 预期内标记） |
| Root 模式 | `capture/engine.py` + root 工具 | 多通道（AF_PACKET/NFQUEUE/TPROXY/eBPF）+ eBPF TLS 明文（R2）+ LSPosed/Frida profile 化（R3） |

## 路线图（M1–M10 + R1–R4）

| 阶段 | 交付 | 状态 |
|---|---|---|
| M1–M5 | 对等基线（抓得全、解得开、改得动、稳得住）——即本仓库 TB1–TB5 对应的引擎层 | ✅ 参考实现 |
| M6 | gRPC proto 推断 + HTTP/3 旁路检测 | 🟡 解析器就绪，推断待扩 |
| M7 | 差分回归 + Agent 辅助规则 + 影响面预判 | ✅ 引擎层 |
| M8 | 悬浮窗 / 全屏仪表盘 / 编辑器 UI | ⬜ Android 产品化 |
| M9 | TLS T2/T3 路径 + 提示注入网关 + 审计 UI | 🟡 工具与门控就绪 |
| M10 | 隐私技能包 + 性能优化 | ⬜ |
| R1–R4 | Root 增量（多通道数据面 / eBPF 明文 / pinning bypass / 受限 shell） | 🟡 引擎与工具层就绪 |

> **Android 产品化路径**：本仓库的 L1–L5 引擎以纯 Python 参考实现先行验证行为语义
> （协议解析、变换层、门控、导出格式均有测试与变异验证锚定），随后按层移植到
> Kotlin（VpnService + QuickJS 沙箱 + Ktor 代理内核），接口语义不变。

## 风险登记（v2.0 §7 摘要）

| 风险 | 缓解 |
|---|---|
| 脚本沙箱逃逸 | 白名单 API + 空 builtins + AST 静态校验（禁 import / dunder / 方法调用） |
| 重写规则导致 App 崩溃 | 影响面预判（I10）+ `disable_all()` 一键逃生门 |
| QUIC 旁路被误认为“抓全了” | I9 强制可见性声明 |
| root 工具被滥用 | HIGH 每次确认 + 审计 + 目标包名记录；`exec_root_shell` 默认禁用 + 白名单 |
| T3 APK 重打包被滥用 | 仅限授权测试 + 审计记录 + 默认关闭 |

## License

MIT © Ultra-Guru
