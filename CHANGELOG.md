# Changelog

All notable changes to traffic-agent are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project ships
CalVer-ish `0.MINOR.PATCH` versions.

## [Unreleased]

### Added (PR feat/engine-deep — engine deep dive)
- HTTP/2 stream-level capture: per-stream HEADERS/DATA reassembly, request/response
  pairing into `HttpExchangeRecord`s (protocol `HTTP2`), gRPC framing split
  (5-byte length-prefixed messages) with text/hex previews.
- WebSocket end-to-end capture: the RFC 6455 assembler is now wired into the
  analysis engine after a 101 upgrade; both directions emit `ws` events with
  opcode, direction and payload preview.
- pcapng writer (SHB/IDB/EPB with `if_tsresol`) next to the classic pcap writer,
  selectable from Settings; pcap/pcapng file import that replays packets
  through the native engine and lands exchanges in the live session list.
- Rule engine productization: request-phase short-circuit fixed (Block/Mock/
  Abort no longer reach the origin), real `RuleMatch.overlaps()` conflict
  analysis, JSON rulepack persistence (`.tarule.json`), new `ReplaceQueryParam`
  and `MapRemote` actions, per-rule hit counters surfaced in the UI.
- MITM origin connection pool with keep-alive reuse (bounded idle TTL,
  stale-socket retry) and full-duplex WebSocket relay after `101` on both
  serve modes.

### Added (PR feat/app-experience — app experience)
- Dashboard tab: protocol-mix donut, top-hosts bars, throughput sparkline and
  status distribution drawn with plain Compose Canvas (no chart dependencies).
- Unified filter experience: the full core-analysis filter DSL is now the only
  filter path, with a help sheet and persisted saved filters.
- Body viewer suite: JSON tree (collapsible), hex dump (16 bytes/row with ASCII
  column), image preview, urlencoded/multipart form rendering, and payload
  search — binary bodies are preserved end-to-end now.
- Repeater: edit method/URL/headers/body, replay over HttpURLConnection with
  trust-all option, response diff against the original capture, replay history.
- App unit tests (hex formatting, JSON tree, saved filters, stats aggregation),
  README/architecture docs refresh and this changelog.

## [0.4.0] — App data plane end-to-end

### Added
- Transparent-TLS MITM (`ServeMode.TRANSPARENT_TLS`) with SNI-driven leaf
  certificates; two-serve-mode layout (8843 TLS / 8808 AUTO).
- `VpnOrchestrator`: TUN -> user-space stack -> protected upstream sockets,
  DNS retargeting, sweep loop and live stats.
- `PcapSessionFile` classic-pcap recording; HAR/Postman/CSV/Markdown exports
  wired into the capture screen; CA export + install guide in Settings.
- Live rule hot-reload through `LiveRuleInterceptor` + `RuleStore` snapshots.

## [0.3.1] — Two-way forwarding data plane

### Added
- User-space TCP forwarding stack (`ForwardStack`): SYN/SYN-ACK, out-of-order
  parking, window throttling, FIN/RST, idle sweep.
- Session persistence (JSONL) and MITM relay plumbing.

## [0.3.0] — Analysis engine breadth

### Added
- TLS ClientHello deep parse (SNI, ALPN, JA3/JA3-MD5), HTTP/1 flow parser with
  chunked/trailers, HPACK full decode, DNS response parsing, QUIC detection.
- Python agent sidecar with sandboxed scriptlets, risk gate and audit log.

## [0.2.0] — Core module split

### Added
- Gradle multi-module layout (core-capture/analysis/transform/mitm/agent/
  exports), native-engine CMake project with 100+ unit tests.

## [0.1.0] — First runnable prototype

### Added
- VpnService TUN capture skeleton, classic pcap reader, HAR export.
