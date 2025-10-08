/*
 * Problem: 2051_D
 * Generated: 2025-09-13 18:45:05
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
#define MOD 1000000007
#define fast ios_base::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL);

ll a[200005],pre[200005],suf[200005];

int main()
{
    fast;
    int t;
    cin>>t;
    while(t--)
    {
        ll n,x,y;
        cin>>n>>x>>y;
        for(int i=1;i<=n;i++)
        {
            cin>>a[i];
        }
        pre[0]=0;
        for(int i=1;i<=n;i++)
        {
            pre[i]=pre[i-1]+a[i];
        }
        suf[n+1]=0;
        for(int i=n;i>=1;i--)
        {
            suf[i]=suf[i+1]+a[i];
        }
        ll ans=0;
        for(int i=1;i<n;i++)
        {
            ll l=i+1,r=n;
            while(l<r)
            {
                ll mid=(l+r+1)/2;
                if(pre[i]+suf[mid]<=y)
                {
                    l=mid;
                }
                else
                {
                    r=mid-1;
                }
            }
            if(pre[i]+suf[l]>=x&&pre[i]+suf[l]<=y)
            {
                ans+=l-i;
            }
        }
        cout<<ans<<endl;
    }
    return 0;
}