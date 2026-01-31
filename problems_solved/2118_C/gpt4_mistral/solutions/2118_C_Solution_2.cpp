/*
 * Problem: 2118_C
 * Generated: 2025-11-24T21:50:00
 * Workflow: gpt4_mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 2
 * Rating: 1300
 */

#include<bits/stdc++.h>
using namespace std;

long long crossSum(vector<long long>& a, int l, int m, int r){{
    long long leftSum = LLONG_MIN, rightSum = LLONG_MIN;
    long long sum = 0;
    for(int i=m; i>=l; i--){{
        sum += a[i];
        leftSum = max(leftSum, sum);
    }}
    sum = 0;
    for(int i=m+1; i<=r; i++){{
        sum += a[i];
        rightSum = max(rightSum, sum);
    }}
    return leftSum + rightSum;
}}

long long maxSubArray(vector<long long>& a, int l, int r){{
    if(l == r) return a[l];
    int m = (l + r) / 2;
    return max({{maxSubArray(a, l, m), maxSubArray(a, m+1, r), crossSum(a, l, m, r)}});
}}

int main(){{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int t;
    cin >> t;
    while(t--){{
        int n;
        cin >> n;
        vector<long long> a(n);
        for(int i=0;i<n;i++) cin >> a[i];
        cout << maxSubArray(a, 0, n-1) << "\n";
    }}
    return 0;
}}
