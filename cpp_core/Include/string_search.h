// string_search.h
// KMP and Boyer-Moore (bad-character) search utilities
#pragma once

#include <string>

// Return true if `pattern` is found in `text` using KMP
bool kmp_contains(const std::string &text, const std::string &pattern);

// Return true if `pattern` is found in `text` using Boyer-Moore bad-character heuristic
bool bm_contains(const std::string &text, const std::string &pattern);
