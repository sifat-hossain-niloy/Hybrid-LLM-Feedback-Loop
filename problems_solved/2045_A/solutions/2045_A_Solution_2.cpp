/*
 * Problem: 2045_A - Problem A
 * Generated: 2025-10-07 19:35:49
 * Model: GPT-4
 * Iteration: 2
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
    int vowels = cnt['A' - 'A'] + cnt['E' - 'A'] + cnt['I' - 'A'] + cnt['O' - 'A'] + cnt['U' - 'A'] + min(cnt['Y' - 'A'], 1);
    int consonants = s.size() - vowels;
    int ng = min(cnt['N' - 'A'], cnt['G' - 'A']);
    consonants += ng;
    int syllables = min(vowels, consonants);
    if (syllables == 0) {
        cout << 0 << endl;
    } else {
        cout << syllables * 3 << endl;
    }
    return 0;
}