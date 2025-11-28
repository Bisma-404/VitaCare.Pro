#include "../Include/string_search.h"
#include <cstring>

// KMP prefix computation (uses dynamic array to avoid std::vector)
static int* compute_prefix(const std::string &pat) {
    int m = (int)pat.size();
    int *pi = new int[m];
    if (m == 0) return pi;
    pi[0] = 0;
    int k = 0;
    for (int q = 1; q < m; ++q) {
        while (k > 0 && pat[k] != pat[q]) k = pi[k-1];
        if (pat[k] == pat[q]) ++k;
        pi[q] = k;
    }
    return pi;
}

bool kmp_contains(const std::string &text, const std::string &pattern) {
    int n = (int)text.size();
    int m = (int)pattern.size();
    if (m == 0) return true;
    if (n < m) return false;
    int *pi = compute_prefix(pattern);
    int q = 0;
    for (int i = 0; i < n; ++i) {
        while (q > 0 && pattern[q] != text[i]) q = pi[q-1];
        if (pattern[q] == text[i]) ++q;
        if (q == m) {
            delete[] pi;
            return true;
        }
    }
    delete[] pi;
    return false;
}

// Boyer-Moore bad-character heuristic (simple ASCII mapping)
bool bm_contains(const std::string &text, const std::string &pattern) {
    int n = (int)text.size();
    int m = (int)pattern.size();
    if (m == 0) return true;
    if (n < m) return false;

    const int ALPH = 256;
    int bad[ALPH];
    for (int i = 0; i < ALPH; ++i) bad[i] = -1;
    for (int i = 0; i < m; ++i) bad[(unsigned char)pattern[i]] = i;

    int s = 0; // shift of the pattern w.r.t text
    while (s <= n - m) {
        int j = m - 1;
        while (j >= 0 && pattern[j] == text[s + j]) --j;
        if (j < 0) {
            return true;
        } else {
            int bcIndex = (unsigned char)text[s + j];
            int last = bad[bcIndex];
            int shift = j - last;
            if (shift < 1) shift = 1;
            s += shift;
        }
    }
    return false;
}
