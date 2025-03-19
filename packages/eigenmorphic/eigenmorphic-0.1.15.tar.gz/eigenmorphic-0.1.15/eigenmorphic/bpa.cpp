#include <stdlib.h>
#include "bpa.h"
#include <unordered_map>
#include <stack>
#include <cstring>

using namespace std;

Substitution s;
Matrix ms;
Matrix V;

ulong *pos; // temporary variable used to decompose a balanced pair into irreducible balanced pairs

// compute length after applying s, from abelian vector
long slength(long *v)
{
  uint8_t i;
  long res = 0;
  for (i=0;i<s.n;i++)
  {
    res += s.w[i].n*v[i];
  }
  return res;
}

class BP2
{
public:
    char *a; // first word
    char *b; // second word
    ulong n; // common length
    long *v; // abelian vector
    
    BP2(ulong n);
    ~BP2();
    long hash () const;
    bool equal_to (const BP2&) const;
};

BP2::BP2(ulong n)
{
  this->n = n;
  a = (char *)malloc(sizeof(char)*n);
  b = (char *)malloc(sizeof(char)*n);
  v = (long *)malloc(sizeof(long)*s.n);
}

BP2::~BP2()
{
  free(a);
  free(b);
  free(v);
}

long BP2::hash() const
{
  unsigned int B    = 378551;
  unsigned int A    = 63689;
  unsigned int hash = 0;
  for(std::size_t i = 0; i < n; i++)
  {
      hash = hash * A + a[i] + b[i]*A;
      A    = A * B;
  }
  return hash;
}

bool BP2::equal_to (const BP2& other) const
{
  if (other.n != n)
    return false;
  int i;
  for (i=0;i<n;i++)
  {
    if (a[i] != other.a[i] || b[i] != other.b[i])
      return false;
  }
  return true;
}

struct BP2Hasher
{
    size_t operator()(const BP2& a) const
    {
        return a.hash();
    }
};

struct BP2Equals
{
    bool operator()(const BP2& a, const BP2& b) const
    {
        return a.equal_to(b);
    }
};

// apply ms to vector
void apply (const long *v, long *res)
{
  int i, j;
  for (i=0;i<s.n;i++)
  {
    res[i] = 0;
    for (j=0;j<s.n;j++)
    {
      res[i] += ms.e[i][j] * v[j];
    }
  }
}

// apply s to the balanced pair
BP2 apply (BP2 bp)
{
  int i, j;
  int ia = 0, ib = 0;
  BP2 r(slength(bp.v));
  for (i=0;i<bp.n;i++)
  {
    for (j=0;j<s.w[bp.a[i]].n;j++)
    {
      r.a[ia] = s.w[bp.a[i]].l[j];
      ia++;
    }
    for (j=0;j<s.w[bp.b[i]].n;j++)
    {
      r.b[ib] = s.w[bp.b[i]].l[j];
      ib++;
    }
    // abelian vector
    apply(bp.v, r.v);
  }
  return r;
}

long *new_vec()
{
  return (long *)malloc(sizeof(long)*s.n);
}

void set_zero(long *v)
{
  uint8_t j;
  for (j=0;j<s.n;j++)
  {
    v[j] = 0;
  }
}

// test if two vectors are equal
bool equals (long *a, long *b)
{
  uint8_t i;
  for (i=0;i<s.n;i++)
  {
    if (a[i] != b[i])
      return false;
  }
  return true;
}

void BaPA(Substitution s1, Matrix m, BP *I, int n, int verb)
{
  s = s1;
  V = m;
  printf("Substitution sur %d lettres.", s.n);
  // convert to BP2
  BP2 *I2 = (BP2 *)malloc(sizeof(BP2*)*n);
  int i,j;
  for (i=0;i<n;i++)
  {
    I2[i].a = I[i].a.l;
    I2[i].b = I[i].b.l;
    I2[i].n = I[i].a.n;
    // abelian vector
    I2[i].v = new_vec();
    set_zero(I2[i].v);
    for (j=0;j<I2[i].n;j++)
    {
      I2[i].v[I2[i].a[j]]++;
    }
  }
  // compute Matrix of s
  ms.nr = s.n;
  ms.nc = s.n;
  ms.e = (int **)malloc(sizeof(int *)*s.n);
  for (i=0;i<s.n;i++)
  {
    m.e[i] = (int *)malloc(sizeof(int)*s.n);
    for (j=0;j<s.n;j++)
    {
      m.e[i][j] = 0;
    }
  }
  for (i=0;i<s.n;i++)
  {
    for (j=0;j<s.w[i].n;j++)
    {
      m.e[s.w[i].l[j]][i]++;
    }
  }

  stack<BP2> pile;

  unordered_map<BP2, int, BP2Hasher, BP2Equals> lBP; // list of balanced pair already seen
  lBP.reserve(n*4);
  
  for (i=0;i<n;i++)
  {
    lBP[I2[i]] = 1; // indicate as seen for the first time
    pile.push(I2[i]); // put on the stack
  }
  
  auto va = new_vec();
  auto vb = new_vec();
  int ri;
  int ml = 0; // max length seen
  
  while (!pile.empty())
  {
    BP2 bp = pile.top();
    pile.pop();
    BP2 bp2 = apply(bp);
    set_zero(va);
    set_zero(vb);
    ri = 0;
    if (bp2.n > ml)
      ml = bp2.n;
    // decompose into irreducible pairs
    for (i=0;i<bp2.n;i++)
    {
      va[bp2.a[i]]++;
      vb[bp2.b[i]]++;
      if (equals(va, vb))
      {
        BP2 bpi(i - ri);
        memcpy(bpi.a, bp2.a + ri, sizeof(bp2.a[ri])*(i-ri));
        memcpy(bpi.b, bp2.b + ri, sizeof(bp2.b[ri])*(i-ri));
        memcpy(bpi.v, va, sizeof(va[0])*s.n);
        
        if (lBP.count(bpi) == 0)
        { // element not in the hash table
          lBP[bpi] = 1; // indicates as seen for the first time
          pile.push(bpi); // add to the stack
        }
        
        set_zero(va);
        set_zero(vb);
      }
    }
    lBP[bp2] = 2; // indicates as seen for the last time 
  }
  
  printf("Algo terminated with %ld balanced pairs, max length %d\n", lBP.size(), ml);
}

