#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace traffic {

// Fixed-memory sliding-window rate meter.
//
// Time is divided into `buckets` slots of `bucketMs` each. Each observation
// of (timestampMs, value) lands in the bucket covering its timestamp; the
// rate is the window sum divided by the window span. Old buckets are zeroed
// lazily as the window advances, so memory stays O(buckets) regardless of
// the number of observations.
class RateWindow {
public:
    RateWindow(size_t buckets, uint64_t bucketMs);

    // Adds `value` at `timestampMs`. Timestamps may arrive out of order by
    // up to one bucket; older samples are dropped.
    void add(uint64_t timestampMs, uint64_t value);

    // Sum of the values inside the current window.
    uint64_t windowSum() const;

    // Events per second over the window (windowSum / span seconds).
    double ratePerSecond() const;

    // Buckets currently holding data (diagnostics).
    size_t activeBuckets() const;

private:
    void advanceTo(uint64_t timestampMs);

    std::vector<uint64_t> sums_;
    uint64_t bucketMs_;
    uint64_t windowSpanMs_;
    uint64_t newestBucket_ = 0;   // absolute bucket index of the newest slot
    uint64_t populated_ = 0;      // bitmask of populated relative slots (<=64)
    size_t active_ = 0;
};

// Streaming percentile estimator over a bounded sample buffer.
//
// Keeps at most `capacity` samples; when full, the buffer is sorted once and
// the median-of-each-half trick keeps memory bounded while accuracy stays
// within a few percent for the P50/P90/P99 use case of the dashboard.
class PercentileAccumulator {
public:
    explicit PercentileAccumulator(size_t capacity = 4096);

    void add(uint64_t value);

    // Returns the p-th percentile (0..100) of the observed samples; 0 when
    // no samples were added. Uses nearest-rank selection.
    uint64_t percentile(double p) const;

    size_t count() const { return total_; }
    uint64_t min() const { return min_; }
    uint64_t max() const { return max_; }
    double mean() const;

    // True when the internal buffer is compacted (samples dropped).
    bool saturated() const { return total_ > samples_.size(); }

private:
    void compact();

    std::vector<uint64_t> samples_;
    size_t capacity_;
    uint64_t total_ = 0;
    uint64_t sum_ = 0;
    uint64_t min_ = 0;
    uint64_t max_ = 0;
};

// Bounded top-K counter: tracks the K heaviest keys by accumulated weight
// without keeping every distinct key in memory (space O(k log k) amortized
// via a lightweight lossy counter).
class TopKCounter {
public:
    explicit TopKCounter(size_t k);

    // Adds `weight` to `key`.
    void add(const std::string& key, uint64_t weight);

    struct Entry {
        std::string key;
        uint64_t weight;
    };

    // Current top-K entries, heaviest first. Weights of evicted keys are
    // folded into the survivors, so they never decrease spuriously.
    std::vector<Entry> top() const;

    size_t distinctSeen() const { return distinct_; }

private:
    size_t k_;
    uint64_t distinct_ = 0;
    std::vector<Entry> entries_;  // kept sorted, at most 2*k before pruning
};

// Exponential moving average helper (RFC 5293 style EWMA, used for smoothed
// bandwidth display). alpha in (0, 1]; higher alpha tracks faster.
class Ewma {
public:
    explicit Ewma(double alpha) : alpha_(alpha) {}

    void update(double sample) {
        if (!initialized_) {
            value_ = sample;
            initialized_ = true;
            return;
        }
        value_ = alpha_ * sample + (1.0 - alpha_) * value_;
    }

    double value() const { return value_; }
    bool initialized() const { return initialized_; }
    void reset() { initialized_ = false; value_ = 0.0; }

private:
    double alpha_;
    double value_ = 0.0;
    bool initialized_ = false;
};

}  // namespace traffic
