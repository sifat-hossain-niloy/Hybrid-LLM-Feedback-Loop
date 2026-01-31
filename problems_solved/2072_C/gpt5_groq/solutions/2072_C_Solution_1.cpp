/*
 * Problem: 2072_C
 * Generated: 2025-11-28T19:36:16
 * Workflow: gpt5_groq
 * Solution Model: gpt-5
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 1
 * Rating: 1200
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
