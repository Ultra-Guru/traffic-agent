#pragma once

// Minimal registration-based test framework (no external dependencies).

#include <cstdio>
#include <string>
#include <vector>

struct TestCase {
    const char* name;
    void (*fn)();
};

inline std::vector<TestCase>& taRegistry() {
    static std::vector<TestCase> r;
    return r;
}

inline int& taFailures() {
    static int c = 0;
    return c;
}

inline int& taRuns() {
    static int c = 0;
    return c;
}

#define TA_TEST(name)                                                                          \
    static void ta_test_##name();                                                              \
    static bool ta_reg_##name =                                                               \
        (taRegistry().push_back({#name, ta_test_##name}), true);                               \
    static void ta_test_##name()

#define TA_CHECK(cond)                                                                        \
    do {                                                                                      \
        ++taRuns();                                                                           \
        if (!(cond)) {                                                                        \
            ++taFailures();                                                                   \
            std::printf("    FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond);                   \
        }                                                                                     \
    } while (0)

#define TA_CHECK_EQ(a, b)                                                                     \
    do {                                                                                      \
        ++taRuns();                                                                           \
        if (!((a) == (b))) {                                                                  \
            ++taFailures();                                                                   \
            std::printf("    FAIL %s:%d  %s == %s  (%lld vs %lld)\n", __FILE__, __LINE__,     \
                        #a, #b, static_cast<long long>(a), static_cast<long long>(b));       \
        }                                                                                     \
    } while (0)

#define TA_CHECK_ST(a, b)                                                                     \
    do {                                                                                      \
        ++taRuns();                                                                           \
        std::string ta_s1_(a), ta_s2_(b);                                                     \
        if (ta_s1_ != ta_s2_) {                                                               \
            ++taFailures();                                                                   \
            std::printf("    FAIL %s:%d  \"%s\" != \"%s\"\n", __FILE__, __LINE__,             \
                        ta_s1_.c_str(), ta_s2_.c_str());                                       \
        }                                                                                     \
    } while (0)
