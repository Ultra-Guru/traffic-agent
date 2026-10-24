#include <cstdio>

#include "test_framework.hpp"
#include "builders.hpp"

int main() {
    int failed = 0;
    for (const auto& t : taRegistry()) {
        int before = taFailures();
        std::printf("[ RUN ] %s\n", t.name);
        t.fn();
        bool ok = taFailures() == before;
        if (!ok) ++failed;
        std::printf("[%s] %s\n", ok ? " OK " : "FAIL", t.name);
    }
    std::printf("\n%d test(s), %d failed, %d checks, %d failed checks\n",
                static_cast<int>(taRegistry().size()), failed, taRuns(), taFailures());
    return (failed == 0 && taFailures() == 0) ? 0 : 1;
}
