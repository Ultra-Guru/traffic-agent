# Traffic Agent

[![CI](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Ultra-Guru/traffic-agent/actions/workflows/ci.yml)
[![Kotlin](https://img.shields.io/badge/Kotlin-2.0.20-7F52FF)](https://kotlinlang.org)
[![C++](https://img.shields.io/badge/C%2B%2B-17-00599C)](https://en.cppreference.com/w/cpp/17)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](https://www.python.org)
[![Material 3](https://img.shields.io/badge/Material%203-Compose-00696D)](https://m3.material.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Android 抓包 Agent**：以小黄鸟（HttpCanary）/ Reqable 的功能集为基线，叠加 Agent 工具链与 Root 增量能力的现代化流量分析工具。Material Design 3 界面，Kotlin + C++ + Python 三语言架构，全栈变异测试验证。

> 本仓库是 SPEC v2.1 的 Android 产品化实现（v2.0 纯 Python 参考实现已归档至 [`python-prototype`](https://github.com/Ultra-Guru/traffic-agent/tree/python-prototype) 分支）。

---

## 特性

### 全功能覆盖（对标 HttpCanary / Reqable）

| 能力 | 状态 | 实现层 |
|------|------|--------|
| **App 数据面全链路接通（TUN → ForwardStack → 上游 socket/MITM → UI 实时列表）** | **v0.4 新增** | `app` `TrafficVpnService` + `core-capture` `VpnOrchestrator` + `session/CaptureSession` |
| **透明 TLS MITM（VPN 重定向 443 流量，SNI 动态签发叶子证书）** | **v0.4 新增** | `core-mitm` `ServeMode.TRANSPARENT_TLS` + `CaManager`（PKCS12 持久化跨重启） |
| **DNS 劫持转发（UDP/53 重写到指定解析器）** | **v0.4 新增** | `core-capture` `VpnOrchestrator`（`dnsForward`） |
| **PCAP 导出（经典 pcap，Wireshark/tcpdump 直开）** | **v0.4 新增** | C++ `native-engine` `PcapWriter` + JNI `PcapWriterBridge` + `PcapFileReader` 回读闭环 |
| **VPN 旁路分析（SNI/JA3/DNS/明文 HTTP 双通道捕获）** | **v0.4 新增** | C++ `export_lines.cpp` + JNI `nativeTakeEvents`/`nativeTakeExchanges` + `VpnAnalysisTap` |
| **实时规则热更新（Rules 屏改动即时作用于在捕流量）** | **v0.4 新增** | `session/RuleStore`（写时复制快照）+ `LiveRuleInterceptor` |
| **CA 证书导出/安装引导 + 前台服务通知 + VPN 权限流** | **v0.4 新增** | `app` `SettingsScreen`/`TrafficVpnService`/`MainActivity` |
| **用户态 TCP 转发栈（SYN 应答/去重/乱序修复/窗口节流/FIN/RST）** | v0.3.1 | C++ `native-engine` `ForwardStack`（`stack.cpp`/`packet_build.cpp`）+ JNI `TcpStackBridge` |
| **QUIC 阻断降级 + MITM 重定向（443→本地 TLS 代理）** | **v0.3.1 新增** | `ForwardStack`（浏览器回退到可拦截的 TCP TLS） |
| **会话持久化（JSONL 环形 + 滚动轮转 + 重启恢复）** | **v0.3.1 新增** | `core-capture` `SessionCodec` + `core-analysis` `SessionStore` |
| **MITM 中继 HTTP/1.x 交换（chunked 解码后重框架 + 捕获）** | **v0.3.1 新增** | `core-mitm` `HttpRelay`（本地回环 E2E 测试） |
| **HTTPS MITM 解密（CA 动态签发 + SNI 感知）** | **v0.3 新增** | `core-mitm`（纯 JDK TLS 终止，E2E 测试） |
| 协议解析：TLS ClientHello 全量 + **JA3 指纹** | **v0.3 新增** | C++ `native-engine` `tls.cpp` |
| **HTTP/2 HPACK 完整解码（静态/动态表 + Huffman）** | **v0.3 新增** | C++ `native-engine` `hpack.cpp`（RFC 7541 向量验证） |
| **响应体解压（gzip/deflate）+ MIME 嗅探 + chunked** | **v0.3 新增** | C++ `native-engine` `body.cpp` |
| **multipart/form-data 解析** | **v0.3 新增** | C++ `native-engine` `multipart.cpp` |
| **pcapng 导入（大小端 + ns/us 精度）** | **v0.3 新增** | C++ `native-engine` `pcapng.cpp` |
| **DNS 应答解析（压缩指针 + A/AAAA/CNAME/MX/TXT/SOA）** | **v0.3 新增** | C++ `native-engine` `dns.cpp` |
| **WebSocket 消息重组（掩码解码 + 分片拼装）** | **v0.3 新增** | C++ `native-engine` `ws.cpp` |
| **流级 HTTP 交换配对（请求/响应体捕获）** | **v0.3 新增** | C++ `native-engine` `Http1FlowParser` + `HttpExchangeRecord` |
| HTTPS 抓包（VPN/TUN 模式） | 数据面就绪 | C++ `native-engine` + `core-capture` `PacketPump`/`TunFileSource` |
| Root 增量：iptables 透明代理 | 命令构建就绪 | `core-capture` `RootCommandBuilder` |
| Root 增量：tcpdump pcap 回放 | 解析就绪 | `core-capture` `PcapFileReader`（大小端 + 纳秒魔数） |
| **请求重放（改写 URL/方法/头/体）** | **v0.3 新增** | `core-capture` `ReplayEngine` |
| 请求重写 / 断点 / 规则优先级 | 就绪 | `core-transform` |
| **Mock / Block / Abort 短路动作** | **v0.3 新增** | `core-transform` `RuleAction` |
| **弱网模拟（延迟/抖动/丢包/双向上下带宽令牌桶）** | **v0.3 新增** | `core-transform` `WeakNetworkSimulator` |
| **过滤 DSL（host:/status:4xx/size>/time>/proto:/error:）** | **v0.3 新增** | `core-analysis` `FilterEngine` |
| 流量统计 / 时间线 / 域名 Top-N / 状态类分布 | 就绪 | `core-analysis`（`TrafficStats` + `CaptureRepository`） |
| HAR / cURL / CSV / Markdown / **Postman Collection / 原始 HTTP 文本** 导出 | 就绪 | `core-exports` |

### 代差创新

- **Agent 工具链**（`core-agent` + `python/`）：15 个工具调用接口，可编程操作抓包数据。
- **风险门控**：四级风险（SAFE / CAUTION / DANGEROUS / CRITICAL），审批流 + 审计日志，Kotlin 与 Python 双侧镜像执行。
- **脚本沙箱**：AST 检查禁导入 + 受限 builtins + 超时熔断的脚本引擎（`sandbox/executor.py`）。
- **差分回归引擎**（`core-analysis` `DiffEngine`）：两次抓包的结构化 diff（新增 / 删除 / 变更字段），用于回归锁定。
- **JA3 TLS 指纹**（C++ `tls.cpp`）：ClientHello 全字段解析 + MD5 指纹——小黄鸟/Reqable 均未内置的检测能力。
- **Postman Collection 一键导出**（`core-exports`）：抓包直接变接口集合，导入即可调试。

---

## 架构

```
┌───────────────────────────────────────────────────────────┐
│                  Material 3 Compose App                     │
│   捕获列表 · 请求详情 · 重写规则 · Agent 控制台 · 设置        │
├───────────────────────────────────────────────────────────┤
│  core-capture      core-analysis      core-transform        │
│  pcap/Root/重放/TUN  事件总线/统计/差分/过滤  重写/断点/弱网/Mock │
│  core-mitm          core-agent        core-exports           │
│  HTTPS 解密代理       风险门控 + 桥客户端    HAR/cURL/CSV/MD/Postman │
├──────────────────────────┬────────────────────────────────┤
│   C++ native-engine      │        Python sidecar            │
│   L1/L2 抓包与解析        │   工具注册表 · 风险门控            │
│   用户态 TCP 转发栈       │   审计 · 脚本沙箱                 │
│   (JNI: libtraffic_      │   (stdio 行协议桥)                │
│    engine_jni.so)        │                                  │
└──────────────────────────┴────────────────────────────────┘
```

**三语言分工**

| 语言 | 模块 | 职责 |
|------|------|------|
| Kotlin | `app/` + `core-*` | Android UI（Compose M3）、捕获编排、分析、变换、导出、风险门控镜像、MITM 解密、重放、弱网 |
| C++ | `native-engine/` | 高性能抓包数据面：**用户态 TCP 转发栈（ForwardStack）**、TCP 重组、HTTP/1 交换配对（含 body）、HPACK、TLS 全解析+JA3、gzip/chunked/multipart、pcapng、WS 重组、DNS 应答，经 JNI 供 App 调用 |
| Python | `python/traffic_agent/` | Agent 控制面：工具注册表、风险门控执行点、审计日志、脚本沙箱、stdio 桥 |

## 模块地图

| 路径 | 语言 | 测试 | 变异工具 |
|------|------|------|----------|
| `native-engine/` | C++17 | ctest（174 用例，含 ForwardStack 10 例、PCAP 写出 7 例、导出行 6 例） | `scripts/native_mutate.py`（源码注解式，135 个变异点） |
| `python/` | Python 3 | pytest（88 用例） | mutmut 3.8 |
| `core-capture` | Kotlin | JUnit5（含 ReplayEngine E2E） | PIT (pitest) |
| `core-mitm` | Kotlin | JUnit5（HTTPS MITM E2E 21 例） | PIT (pitest) |
| `core-analysis` | Kotlin | JUnit5 | PIT |
| `core-transform` | Kotlin | JUnit5 | PIT |
| `core-agent` | Kotlin | JUnit5 | PIT |
| `core-exports` | Kotlin | JUnit5 | PIT |
| `app/` | Kotlin | — | 构建验证（assembleDebug） |

## 快速开始

```bash
git clone https://github.com/Ultra-Guru/traffic-agent.git
cd traffic-agent

# C++ 引擎：构建 + 测试 + 变异验证
cmake -S native-engine -B native-engine/build -DCMAKE_BUILD_TYPE=Release
cmake --build native-engine/build -j"$(nproc)"
ctest --test-dir native-engine/build --output-on-failure
python3 scripts/native_mutate.py --min-score 90

# Python Agent 层：测试 + 变异验证
cd python && python -m pytest tests -q && mutmut run && cd ..
python3 scripts/mutmut_gate.py --min-score 70

# Kotlin 核心模块（无需 Android SDK）
./gradlew -Pta.skipAndroid allUnitTests
./gradlew -Pta.skipAndroid allPitest
python3 scripts/pitest_gate.py --min-score 65

# Android APK（需要 Android SDK + NDK）
./gradlew :app:assembleDebug
```

> 国内网络被 Maven Central 限流（429）时，`export TA_USE_CN_MIRRORS=1` 走阿里云镜像。

## 变异验证（CI 强制门控）

每个推送在 GitHub Actions 上跑四条流水线，变异分数低于门槛即失败：

| 流水线 | 内容 | 分数门槛 |
|--------|------|----------|
| Native engine | ctest + 45 个源码注解变异点逐一注入、重编译、断言测试杀死 | 90% |
| Python agent | pytest + mutmut 3.8 全量变异 | 70% |
| Kotlin core | JUnit5 + PIT（DEFAULTS 变异集，642 个变异体） | 65% |
| Android app | assembleDebug（Compose M3 + NDK 交叉编译 native 引擎） | 构建通过 |

本地当前分数：**C++ 100%**（135/137，2 个标记不匹配跳过）· **Python 75.5%**（760/1006）· **Kotlin 65.2%**（1168/1792，门槛 65%）。C++ 测试规模 174 用例 / 1343 断言（v0.4 起）。

## 看板（TB1–TB5）

| 看板 | 范围 | 状态 |
|------|------|------|
| [TB1](https://github.com/Ultra-Guru/traffic-agent/issues/6) | 原生抓包引擎 + 协议解析（C++/Kotlin） | 已完成 |
| [TB2](https://github.com/Ultra-Guru/traffic-agent/issues/7) | 事件总线 / 流量统计 / 时间线 / 差分回归 | 已完成 |
| [TB3](https://github.com/Ultra-Guru/traffic-agent/issues/8) | 重写规则 / 断点状态机 / 沙箱策略 | 已完成 |
| [TB4](https://github.com/Ultra-Guru/traffic-agent/issues/9) | Agent 工具链 + 风险门控（Python/Kotlin） | 已完成 |
| [TB5](https://github.com/Ultra-Guru/traffic-agent/issues/10) | Android M3 应用 + 导出 + CI 变异验证 | 已完成 |

## 路线图

- ~~**v0.2**：真机 VpnService 数据面接通（TUN fd → `nativeFeedPacket`），应用分流量（per-uid）~~ ✅ `PacketPump`/`TunFileSource` 已交付（真机联调待 NDK 构建）
- ~~**v0.3**：MITM 解密（SSLKEYLOGFILE + 用户 CA 信任），HTTP2 完整头部解码（HPACK）~~ ✅ `core-mitm` 全量 + HPACK 解码器已交付
- ~~**v0.3.1**：双向转发数据面（用户态 TCP 栈 + 会话持久化 + 中继捕获）~~ ✅ `ForwardStack`/`SessionStore`/`HttpRelay` 已交付
- ~~**v1.0 弱网模拟（延迟/丢包/限速）**~~ ✅ `WeakNetworkSimulator` 已交付（延迟/抖动/丢包/双向令牌桶限速）
- ~~**v0.4**：App 数据面接通 + 透明 MITM + PCAP 导出 + 规则热更新~~ ✅ `TrafficVpnService`/`VpnOrchestrator`/`PcapWriter`/`RuleStore` 已交付（真机联调待 NDK APK 安装）
- **v0.4.1**：Root 模式实机验证（iptables REDIRECT + tcpdump 导入）
- **v0.5**：Python sidecar 混入 APK（Chaquopy 集成），Agent 工具链实机运行
- **v1.0**：gRPC 检测、QUIC 采样解密、Google Play 内测发布

## 许可证

[MIT](LICENSE)
