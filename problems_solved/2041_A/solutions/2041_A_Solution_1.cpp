/*
 * Problem: 2041_A - Problem A
 * Generated: 2025-11-05 05:26:06
 * Model: GPT-4
 * Iteration: 1
 * Rating: 1300
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<int> restaurants(5, 0);
    for(int i = 0; i < 4; i++) {
        int x;
        cin >> x;
        restaurants[x-1] = 1;
    }
    for(int i = 0; i < 5; i++) {
        if(restaurants[i] == 0) {
            cout << i+1 << '\n';
            break;
        }
    }
    return 0;
}