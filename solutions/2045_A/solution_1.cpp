/*
 * Problem: 2045_A
 * Generated: 2025-09-13 18:42:10
 * Model: GPT-4
 * Iteration: 1
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    int n = s.size();
    int vowels = 0, consonants = 0, ng = 0;
    for (int i = 0; i < n; i++) {
        if (s[i] == 'A' || s[i] == 'E' || s[i] == 'I' || s[i] == 'O' || s[i] == 'U') {
            vowels++;
        } else if (s[i] == 'Y') {
            vowels++;
            consonants++;
        } else if (s[i] == 'N' && i < n - 1 && s[i + 1] == 'G') {
            ng++;
            i++;
        } else {
            consonants++;
        }
    }
    int syllables = min(vowels, min(consonants, ng + (consonants - ng) / 2));
    cout << syllables * 66 << endl;
    return 0;
}