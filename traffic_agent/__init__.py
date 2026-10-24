"""Traffic Agent — SPEC v2.0 参考实现。

移动端流量调试 Agent 的 Python 参考实现：以小黄鸟（HttpCanary / Reqable）的
功能集为基线，并在 MITM 解密深度、移动端原生改包、AI 辅助规则、差分回归、
本地隐私闭环五个维度建立代差（见 README）。

分层架构（对应 SPEC v2.0 第 2 章）::

    L1    traffic_agent.capture     抓包数据面（多通道 + 协议解析）
    L1.5  traffic_agent.transform   流量变换层（重写/断点/弱网/脚本沙箱）
    L2    traffic_agent.events      事件总线（TrafficEvent / TransformApplied ...）
    L3    traffic_agent.analysis    分析流水线（差分回归 / 二进制协议推断）
    L4    traffic_agent.agent       Agent 控制面（工具注册表 + 风险门控）
    L5    traffic_agent.export      呈现与导出（HAR / PCAP / SSLKEYLOGFILE / 代码生成）
"""

__version__ = "2.0.0"
