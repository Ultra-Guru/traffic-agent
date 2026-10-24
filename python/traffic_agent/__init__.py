"""Traffic Agent - on-device agent toolchain (Python layer).

Provides the agent control plane described in SPEC v2.1 L4: a tool
registry operating on a capture store, a risk gate, an audit log and a
sandboxed scriptlet executor, exposed to the Kotlin app through a
line-based bridge.
"""

__version__ = "0.1.0"
