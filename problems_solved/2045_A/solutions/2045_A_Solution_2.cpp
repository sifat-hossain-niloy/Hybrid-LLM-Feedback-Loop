/*
 * Problem: 2045_A - Problem A
 * Generated: 2025-10-26 04:20:55
 * Model: GPT-4
 * Iteration: 2
 * Rating: 1700
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    vector<int> count(26, 0);
    int y = 0;
    for(char c: s) {
        if(c == 'Y')
            y++;
        else if(c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U')
            count[26]++;
        else
            count[c - 'A']++;
    }
    int ng = min(count['N' - 'A'], count['G' - 'A']);
    count['N' - 'A'] -= ng;
    count['G' - 'A'] -= ng;
    int vowels = count[26];
    count[26] = 0;
    int consonants = accumulate(count.begin(), count.end(), 0) + ng;
    int syllables = min({consonants, vowels, (consonants + vowels + y) / 3});
    cout << syllables * 3 << "\n";
    return 0;
}