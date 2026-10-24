# Traffic Agent — SPEC v2.1（Android 产品化）

> v2.0（纯 Python 参考实现）见 `python-prototype` 分支。v2.1 将架构落地为
> Kotlin + C++ + Python 三语言 Android 产品，本文档记录目标、分层与验收标准。

## 1. 定位

以小黄鸟（HttpCanary）/ Reqable 的功能集为**基线**，在四个维度建立**代差**：

1. **Agent 工具链** — 流量数据以工具调用形式暴露给自动化与 AI Agent；
2. **风险门控** — 所有变更操作经四级风险评估与审计，审批流闭环；
3. **差分回归** — 两次抓包的结构化 diff，回归测试可编程；
4. **本地隐私闭环** — 全部解析在设备端完成，无云端依赖。

## 2. 分层

```
L1   native-engine (C++)        抓包数据面：IPv4/TCP/UDP 解析、流重组、
                                 SNI/HTTP1/HTTP2/WS/DNS/QUIC 检测
L1.5 core-transform (Kotlin)     变换层：重写规则、断点、沙箱策略、脚本钩子
L2   core-analysis (Kotlin)      事件总线、流量统计、时间线、差分回归
L3   core-agent + python/       Agent 控制面：工具注册表、风险门控、审计
L4   core-exports (Kotlin)       HAR / cURL / CSV / Markdown 导出
L5   app (Kotlin, Compose M3)   产品界面
```

## 3. 关键决策

| 决策 | 理由 |
|------|------|
| C++ 实现解析数据面 | 抓包路径的性能与内存确定性；纯标准 C++17，桌面（ctest）与 NDK 双构建 |
| Kotlin 纯 JVM 模块承载业务逻辑 | 桌面 JUnit/PIT 可测，Android 直接复用 |
| Python 作为 sidecar 而非嵌入 | 工具链/沙箱迭代独立于 APK 发布；桥协议（stdio 行协议）保持窄接口 |
| 桥协议用 query-string 行而非 JSON | 免三方依赖、易审计、端到端可用单测覆盖；结构化数据仍在 payload 中以 JSON 携带 |
| 风险门控双侧镜像 | Kotlin 侧 gate-before-wire（UI 徽章 + 预检），Python 侧强制执行（工具真实生效点） |
| 变异验证三件套 | mutmut（Python）/ PIT（Kotlin）/ 源码注解式自研变异器（C++），CI 分数门控 |

## 4. 看板与验收

| 看板 | 交付物 | 验收 |
|------|--------|------|
| TB1 | native-engine + core-capture | ctest 全绿；变异 ≥ 90%；JUnit 全绿 |
| TB2 | core-analysis | JUnit 全绿；PIT 达标 |
| TB3 | core-transform | JUnit 全绿；PIT 达标 |
| TB4 | python/ + core-agent | pytest 全绿；mutmut ≥ 70%；桥协议端到端测试 |
| TB5 | core-exports + app + CI | 导出器单测；assembleDebug 通过；四条 CI 流水线全绿 |

## 5. 路线图（产品化）

见 README「路线图」小节。核心原则：数据面先行（v0.2），解密其次（v0.3），
工具链混包最后（v0.5）——保证每一步都有可验证的用户价值。
