/*
 * Problem: 2045_A - Problem A
 * Generated: 2025-10-07 19:36:00
 * Model: GPT-4
 * Iteration: 3
 * Rating: 1700
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    vector<int> cnt(26);
    for (char c : s) {
        cnt[c - 'A']++;
    }
    int vowels = cnt['A' - 'A'] + cnt['E' - 'A'] + cnt['I' - 'A'] + cnt['O' - 'A'] + cnt['U' - 'A'];
    int y = cnt['Y' - 'A'];
    int ng = min(cnt['N' - 'A'], cnt['G' - 'A']);
    int consonants = s.size() - vowels - y - 2*ng;
    int syllables = min(vowels + min(y, 1), consonants + ng + min(y, 1));
    if (syllables == 0) {
        cout << 0 << endl;
    } else {
        cout << syllables * 3 << endl;
    }
    return 0;
}