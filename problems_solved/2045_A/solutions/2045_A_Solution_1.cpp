/*
 * Problem: 2045_A - Problem A
 * Generated: 2025-10-31 05:44:45
 * Model: GPT-4
 * Iteration: 1
 * Rating: 1700
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    int a[128] = {}, vowels = 0, y = 0, ng = 0, others = 0;
    for (char c : s) a[c]++;
    vowels = a['A'] + a['E'] + a['I'] + a['O'] + a['U'];
    y = a['Y'];
    ng = min(a['N'], a['G']);
    others = s.size() - vowels - y - 2 * ng;
    if (vowels + y + min(y, others) < 2 || others + 2 * ng < 1) {
        cout << 0 << endl;
    } else {
        int t = min(vowels + y + min(others, y) - 1, others + 2 * ng);
        cout << t / 2 * 3 << endl;
    }
    return 0;
}