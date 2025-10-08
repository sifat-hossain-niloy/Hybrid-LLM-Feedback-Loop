/*
 * Problem: 2045_A
 * Generated: 2025-09-20 20:49:01
 * Model: GPT-4
 * Iteration: 3
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    int n = s.size();
    vector<int> cnt(26);
    for (int i = 0; i < n; i++) {
        cnt[s[i] - 'A']++;
    }
    int vowels = cnt['A' - 'A'] + cnt['E' - 'A'] + cnt['I' - 'A'] + cnt['O' - 'A'] + cnt['U' - 'A'] + cnt['Y' - 'A'];
    int consonants = n - vowels;
    int ng = min(cnt['N' - 'A'], cnt['G' - 'A']);
    consonants += ng;
    int syllables = min(vowels, consonants / 2);
    cout << syllables * 6 << endl;
    return 0;
}