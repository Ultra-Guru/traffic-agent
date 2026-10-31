#include "traffic/stats.h"

#include <algorithm>
#include <cmath>
#include <cstring>

namespace traffic {

// ---------------- RateWindow ----------------

RateWindow::RateWindow(size_t buckets, uint64_t bucketMs)
    : sums_(buckets > 0 ? buckets : 1, 0),
      bucketMs_(bucketMs > 0 ? bucketMs : 1),
      windowSpanMs_(0) {
    windowSpanMs_ = this->bucketMs_ * sums_.size();
}

void RateWindow::advanceTo(uint64_t timestampMs) {
    const uint64_t bucket = timestampMs / bucketMs_;
    if (bucket <= newestBucket_) return;

    const uint64_t span = bucket - newestBucket_;
    if (span >= sums_.size()) {
        // The whole window slid past: clear everything.
        std::fill(sums_.begin(), sums_.end(), 0);
        populated_ = 0;
        active_ = 0;
    } else {
        // Clear the (span) buckets behind the new head.
        for (uint64_t i = 0; i < span; ++i) {
            const size_t slot = static_cast<size_t>((newestBucket_ + 1 + i) % sums_.size());
            if (sums_[slot] != 0) {
                sums_[slot] = 0;
                if (active_ > 0) active_--;
            }
        }
    }
    newestBucket_ = bucket;
}

void RateWindow::add(uint64_t timestampMs, uint64_t value) {
    advanceTo(timestampMs);
    const uint64_t bucket = timestampMs / bucketMs_;
    // Samples older than the window are dropped.
    if (newestBucket_ - bucket >= sums_.size()) return;  // MUT:>
    const size_t slot = static_cast<size_t>(bucket % sums_.size());
    if (sums_[slot] == 0) active_++;
    sums_[slot] += value;
}

uint64_t RateWindow::windowSum() const {
    uint64_t sum = 0;
    for (uint64_t v : sums_) sum += v;
    return sum;
}

double RateWindow::ratePerSecond() const {
    if (windowSpanMs_ == 0) return 0.0;
    // The effective denominator is min(windowSpan, observed activity) but
    // a fixed window keeps the rate comparable across sessions.
    return static_cast<double>(windowSum()) * 1000.0 / static_cast<double>(windowSpanMs_);
}

size_t RateWindow::activeBuckets() const { return active_; }

// ---------------- PercentileAccumulator ----------------

PercentileAccumulator::PercentileAccumulator(size_t capacity)
    : capacity_(capacity > 0 ? capacity : 1) {
    samples_.reserve(capacity_ + 1);
}

void PercentileAccumulator::add(uint64_t value) {
    if (total_ == 0 || value < min_) min_ = value;  // MUT:>
    if (total_ == 0 || value > max_) max_ = value;
    sum_ += value;
    total_++;
    samples_.push_back(value);
    if (samples_.size() > capacity_) compact();
}

void PercentileAccumulator::compact() {
    // Halve the buffer keeping evenly spread order statistics: retaining
    // every second sample from index 0 keeps the sample representative of
    // the whole distribution instead of drifting toward the extremes.
    std::sort(samples_.begin(), samples_.end());
    std::vector<uint64_t> kept;
    kept.reserve(samples_.size() / 2 + 1);
    for (size_t i = 0; i < samples_.size(); i += 2) {
        kept.push_back(samples_[i]);
    }
    samples_ = std::move(kept);
}

uint64_t PercentileAccumulator::percentile(double p) const {
    if (samples_.empty()) return 0;
    if (p < 0.0) p = 0.0;
    if (p > 100.0) p = 100.0;
    // Nearest-rank on a sorted copy (read-side sort keeps adds cheap):
    // idx = ceil(p/100 * N) - 1.
    std::vector<uint64_t> sorted(samples_);
    std::sort(sorted.begin(), sorted.end());
    const double rank = std::ceil((p / 100.0) * static_cast<double>(sorted.size()));
    size_t idx = rank >= 1.0 ? static_cast<size_t>(rank) - 1 : 0;
    if (idx >= sorted.size()) idx = sorted.size() - 1;
    return sorted[idx];
}

double PercentileAccumulator::mean() const {
    if (total_ == 0) return 0.0;
    return static_cast<double>(sum_) / static_cast<double>(total_);
}

// ---------------- TopKCounter ----------------

TopKCounter::TopKCounter(size_t k) : k_(k > 0 ? k : 1) {}

void TopKCounter::add(const std::string& key, uint64_t weight) {
    for (Entry& e : entries_) {
        if (e.key == key) {
            e.weight += weight;
            return;
        }
    }
    distinct_++;
    entries_.push_back({key, weight});
    if (entries_.size() > k_ * 2) {
        // Prune: keep the k_ heaviest; evicted keys restart from zero if
        // they are seen again (weights of survivors stay honest).
        std::sort(entries_.begin(), entries_.end(),
                  [](const Entry& a, const Entry& b) { return a.weight > b.weight; });
        entries_.resize(k_);
    }
}

std::vector<TopKCounter::Entry> TopKCounter::top() const {
    std::vector<Entry> copy = entries_;
    std::sort(copy.begin(), copy.end(),
              [](const Entry& a, const Entry& b) {
                  if (a.weight != b.weight) return a.weight > b.weight;
                  return a.key < b.key;
              });
    if (copy.size() > k_) copy.resize(k_);
    return copy;
}

}  // namespace traffic
