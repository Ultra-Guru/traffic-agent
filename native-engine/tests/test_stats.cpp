#include "traffic/stats.h"

#include <cmath>

#include "test_framework.hpp"

using namespace traffic;

// ---------------- RateWindow ----------------

TA_TEST(rate_window_counts_immediate_bucket) {
    RateWindow w(10, 1000);  // 10s window, 1s buckets
    w.add(500, 1);
    w.add(1500, 2);
    w.add(2500, 3);
    TA_CHECK_EQ(w.windowSum(), 6u);
    TA_CHECK_EQ(w.activeBuckets(), static_cast<size_t>(3));
    // 6 events over a 10s window = 0.6/s.
    TA_CHECK(std::fabs(w.ratePerSecond() - 0.6) < 1e-9);
}

TA_TEST(rate_window_evicts_old_buckets) {
    RateWindow w(4, 1000);  // 4s window
    w.add(100, 5);
    TA_CHECK_EQ(w.windowSum(), 5u);
    // 5 seconds later: the first sample slid out of the window.
    w.add(5100, 7);
    TA_CHECK_EQ(w.windowSum(), 7u);
    TA_CHECK_EQ(w.activeBuckets(), static_cast<size_t>(1));
}

TA_TEST(rate_window_full_slide_clears) {
    RateWindow w(4, 1000);
    w.add(100, 5);
    w.add(1200, 6);
    w.add(2400, 7);
    TA_CHECK_EQ(w.windowSum(), 18u);
    // A timestamp far in the future clears the whole window.
    w.add(100000, 1);
    TA_CHECK_EQ(w.windowSum(), 1u);
    TA_CHECK_EQ(w.activeBuckets(), static_cast<size_t>(1));
}

TA_TEST(rate_window_same_bucket_accumulates) {
    RateWindow w(10, 1000);
    w.add(100, 1);
    w.add(200, 2);
    w.add(900, 4);
    TA_CHECK_EQ(w.windowSum(), 7u);
    TA_CHECK_EQ(w.activeBuckets(), static_cast<size_t>(1));
}

TA_TEST(rate_window_out_of_order_dropped) {
    RateWindow w(4, 1000);
    w.add(5000, 9);
    // Older than the current head by more than the window: dropped.
    w.add(100, 5);
    TA_CHECK_EQ(w.windowSum(), 9u);
    // Within one window: kept.
    w.add(3000, 2);
    TA_CHECK_EQ(w.windowSum(), 11u);
}

// ---------------- PercentileAccumulator ----------------

TA_TEST(percentile_basic_nearest_rank) {
    PercentileAccumulator p;
    for (uint64_t v = 1; v <= 100; ++v) p.add(v);
    TA_CHECK_EQ(p.count(), 100u);
    TA_CHECK_EQ(p.min(), 1u);
    TA_CHECK_EQ(p.max(), 100u);
    TA_CHECK_EQ(p.percentile(50), 50u);
    TA_CHECK_EQ(p.percentile(90), 90u);
    TA_CHECK_EQ(p.percentile(99), 99u);
    TA_CHECK_EQ(p.percentile(0), 1u);
    TA_CHECK_EQ(p.percentile(100), 100u);
}

TA_TEST(percentile_empty_returns_zero) {
    PercentileAccumulator p;
    TA_CHECK_EQ(p.percentile(50), 0u);
    TA_CHECK_EQ(p.count(), 0u);
    TA_CHECK(std::fabs(p.mean()) < 1e-12);
}

TA_TEST(percentile_single_sample) {
    PercentileAccumulator p;
    p.add(42);
    TA_CHECK_EQ(p.percentile(10), 42u);
    TA_CHECK_EQ(p.percentile(95), 42u);
    TA_CHECK(std::fabs(p.mean() - 42.0) < 1e-12);
}

TA_TEST(percentile_clamps_bad_p) {
    PercentileAccumulator p;
    for (uint64_t v = 1; v <= 10; ++v) p.add(v);
    TA_CHECK_EQ(p.percentile(-5.0), 1u);
    TA_CHECK_EQ(p.percentile(500.0), 10u);
}

TA_TEST(percentile_compaction_keeps_shape) {
    // Small capacity forces compaction; the distribution must stay sane.
    // Values arrive in LCG-shuffled order (duration samples are never
    // monotonic in real captures).
    PercentileAccumulator p(8);
    for (uint64_t i = 0; i < 1000; ++i) {
        p.add((i * 1103515245u + 12345u) % 1000 + 1);
    }
    TA_CHECK(p.saturated());
    TA_CHECK_EQ(p.count(), 1000u);
    TA_CHECK_EQ(p.min(), 1u);
    TA_CHECK_EQ(p.max(), 996u);  // LCG values are ≡1 (mod 5): max is 996
    const uint64_t p50 = p.percentile(50);
    const uint64_t p90 = p.percentile(90);
    // Order preserved and near the honest values (true p50=500, p90=900).
    TA_CHECK(p50 >= 300 && p50 <= 700);  // MUT:||
    TA_CHECK(p90 > p50);
    TA_CHECK(p90 <= 1000);
}

// ---------------- TopKCounter ----------------

TA_TEST(topk_orders_by_weight) {
    TopKCounter c(3);
    c.add("a", 10);
    c.add("b", 30);
    c.add("c", 20);
    c.add("d", 5);
    auto top = c.top();
    TA_CHECK_EQ(top.size(), static_cast<size_t>(3));
    TA_CHECK_ST(top[0].key, "b");
    TA_CHECK_ST(top[1].key, "c");
    TA_CHECK_ST(top[2].key, "a");
    TA_CHECK_EQ(top[0].weight, 30u);
}

TA_TEST(topk_accumulates_same_key) {
    TopKCounter c(3);
    c.add("x", 5);
    c.add("x", 5);
    c.add("x", 5);
    c.add("y", 12);
    auto top = c.top();
    TA_CHECK_ST(top[0].key, "x");
    TA_CHECK_EQ(top[0].weight, 15u);
    TA_CHECK_ST(top[1].key, "y");
}

TA_TEST(topk_prunes_when_grown) {
    TopKCounter c(2);
    for (int i = 0; i < 20; ++i) {
        c.add("key" + std::to_string(i), static_cast<uint64_t>(i));
    }
    // key19 (19) > key18 (18) > ...: the two heaviest survive.
    auto top = c.top();
    TA_CHECK_EQ(top.size(), static_cast<size_t>(2));
    TA_CHECK_ST(top[0].key, "key19");
    TA_CHECK_ST(top[1].key, "key18");
    TA_CHECK_EQ(c.distinctSeen(), 20u);
}

TA_TEST(topk_prune_keeps_heaviest_honest) {
    TopKCounter c(1);
    c.add("keep", 100);
    for (int i = 0; i < 10; ++i) {
        c.add("small" + std::to_string(i), 1);
    }
    // The single survivor keeps exactly its own weight (no folding).
    auto top = c.top();
    TA_CHECK_EQ(top.size(), static_cast<size_t>(1));
    TA_CHECK_ST(top[0].key, "keep");
    TA_CHECK_EQ(top[0].weight, 100u);
}

TA_TEST(topk_empty_returns_empty) {
    TopKCounter c(5);
    TA_CHECK(c.top().empty());
    TA_CHECK_EQ(c.distinctSeen(), 0u);
}

// ---------------- Ewma ----------------

TA_TEST(ewma_tracks_first_sample_directly) {
    Ewma e(0.5);
    e.update(10.0);
    TA_CHECK(std::fabs(e.value() - 10.0) < 1e-12);
    TA_CHECK(e.initialized());
}

TA_TEST(ewma_converges_toward_constant) {
    Ewma e(0.3);
    for (int i = 0; i < 100; ++i) e.update(50.0);
    TA_CHECK(std::fabs(e.value() - 50.0) < 1e-6);
}

TA_TEST(ewma_smoothing_factor) {
    Ewma e(0.5);
    e.update(0.0);
    e.update(10.0);
    // 0.5*10 + 0.5*0 = 5
    TA_CHECK(std::fabs(e.value() - 5.0) < 1e-12);
}

TA_TEST(ewma_reset_clears_state) {
    Ewma e(0.5);
    e.update(100.0);
    e.reset();
    TA_CHECK(!e.initialized());
    e.update(7.0);
    TA_CHECK(std::fabs(e.value() - 7.0) < 1e-12);
}
