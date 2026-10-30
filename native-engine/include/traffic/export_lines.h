#pragma once

// Line serialization of Engine analysis records (VPN 旁路捕获出舱口).
//
// In VPN mode the ForwardStack forwards traffic, but the analysis Engine is
// still fed as a passive tap: plain-HTTP exchanges and protocol metadata
// (SNI / JA3 / DNS answers / HTTP/2 header blocks) keep flowing. These two
// functions render that output as text lines crossing the JNI boundary:
//
//   * engineEventToLine  -> "kind\ttsMs\tsrcIp:port\tdstIp:port\ttext\tnumeric"
//   * exchangeToJsonLine -> SessionCodec-compatible JSONL (parsed back by
//     core-capture's SessionCodec.decode into CapturedRequest)

#include <cstdint>
#include <string>

#include "engine.h"

namespace traffic {

std::string engineEventToLine(const EngineEvent& ev);

std::string exchangeToJsonLine(const HttpExchangeRecord& rec, uint64_t id);

}  // namespace traffic
