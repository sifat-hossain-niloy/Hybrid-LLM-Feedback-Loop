/*
 * Problem: 2070_C
 * Generated: 2025-09-13 18:45:48
 * Model: GPT-4
 * Iteration: 1
 */

#include<bits/stdc++.h>
using namespace std;
#define ll long long
#define pb push_back
#define mp make_pair
#define pii pair<int,int>
#define pll pair<ll,ll>
#define F first
#define S second
#define all(x) x.begin(),x.end()
#define fastio ios_base::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL);
const int N=3e5+5;
const ll INF=1e18;
ll n,k,a[N],dp[N],sum[N];
string s;
bool check(ll mid)
{
    for(int i=0;i<=n;i++)
        dp[i]=INF,sum[i]=0;
    dp[0]=0;
    for(int i=1;i<=n;i++)
    {
        if(a[i-1]<=mid)
            dp[i]=min(dp[i],sum[i-1]);
        if(i>=k)
            dp[i]=min(dp[i],sum[i-k]);
        sum[i]=min(sum[i-1],dp[i]);
    }
    return dp[n]<=mid;
}
void solve()
{
    cin>>n>>k>>s;
    for(int i=0;i<n;i++)
        cin>>a[i];
    vector<int> v;
    for(int i=0;i<n;i++)
    {
        if(s[i]=='B')
            v.pb(a[i]);
    }
    sort(all(v));
    ll l=0,r=1e9+7,ans=1e9+7;
    while(l<=r)
    {
        ll mid=(l+r)/2;
        if(check(mid))
            ans=mid,r=mid-1;
        else
            l=mid+1;
    }
    cout<<ans<<"\n";
}
int main()
{
    fastio
    int t;
    cin>>t;
    while(t--)
        solve();
    return 0;
}