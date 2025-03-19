#include <stdint.h>
#include <stdio.h>

struct Word
{
    long n;
    char *l;
};
typedef struct Word Word;

struct Substitution
{
    int n;
    Word *w;
};
typedef struct Substitution Substitution;

struct BP
{
    Word a,b;
};
typedef struct BP BP;

struct Matrix
{
    int nr, nc;
    int **e;
};
typedef struct Matrix Matrix;

void BaPA(Substitution s1, Matrix m, BP *I, int n, int8_t verb);

