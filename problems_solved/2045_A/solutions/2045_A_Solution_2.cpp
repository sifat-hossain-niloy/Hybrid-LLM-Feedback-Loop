/*
 * Problem: 2045_A - Problem A
 * Generated: 2025-10-31 05:45:12
 * Model: GPT-4
 * Iteration: 2
 * Rating: 1700
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    int cnt[128] = {};
    for (char c : s) {
        cnt[c]++;
    }
    int vowels = cnt['A'] + cnt['E'] + cnt['I'] + cnt['O'] + cnt['U'];
    int y = cnt['Y'];
    int ng = min(cnt['N'], cnt['G']);
    int consonants = s.size() - vowels - y - ng;
    int syllables = min({vowels + min(y, consonants), consonants + ng, s.size() / 3});
    cout << syllables * 3 << "\n";
    return 0;
}