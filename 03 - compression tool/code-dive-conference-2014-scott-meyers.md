## code::dive Conference 2014 - Scott Meyers - CPU Caches and why you care

- ![Video Link](https://www.youtube.com/watch?v=WDIkqP4JbkE)

These are notes made listening to video. All photos , screenshots, diagrams are taken from the video. I recommend watching the video for full context.
I have added some additional explanations, for myself, where I felt it was necessary. I take no credit for the original content.
This is for personal use and study only. Please do not distribute.

### Problem: Transverse a Matrix

Consider we have a matrix and we want to transverse every single element. It can be for many reasons like finding number of non zero elements, summing all elements, etc.

We can transverse the matrix in two ways:

- we can go **row by row**
- we can go **column by column**

Both methods will visit every single element of the matrix exactly once. Both take the same amount of work but transverse in different order.

```c++
void sumMatrix(const Matrix<int>& m, long long& sum, TransversalOrder order) {
    sum = 0;

    if (order == RowMajor) {
        for (unsigned i = 0; i < m.numRows(); ++i) {
            for (unsigned j = 0; j < m.numCols(); ++j) {
                sum += m[i][j];
            }
        }
    } else { // ColumnMajor
        for (unsigned j = 0; j < m.numCols(); ++j) {
            for (unsigned i = 0; i < m.numRows(); ++i) {
                sum += m[i][j];
            }
        }
    }
}
```

Conceptually both methods are the same. But in practice, one method is significantly faster than the other. The resulting performance

![](./images/01%20-%20performance%20row%20vs%20column%20matrix%20transversal.png)

Performance is measured in transversal time (lower is better). The transversal has been done using two different compilers (gcc and msvc).

This shows row major traversal is significantly faster than column major traversal. This behavior is independent of compiler used. Thus, **transversal order matters**.

Before we understand why this happens, lets look at counting the number of odd elements in a matrix.

### A Scalability Story

Herb Sutter's scalability issue in counting odd matrix elements. Consider a square matrix of dimension `DIM` with memory in array matrix.

```c++
// Pseudocode
int odds = 0;
for (int i = 0; i < DIM; ++i) {
    for (int j = 0; j < DIM; ++j) {
        if (matrix[i*DIM + j] % 2 != 0) {
            ++odds;
        }
    }
}
```

We can parallelize the above code using multiple threads. Each thread will work on a part of the matrix and count number of odd elements in that part. Finally we will sum up the counts from all threads to get the final count.

```c++
int result[P];

// Each of P parallel workers processes 1/P-th of the data
// the p-th worker records its partial count in result[p]
for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
        result[p] = 0;
        int chunkSize = DIM/P + 1;
        int myStart = p * chunkSize;
        int myEnd = min(myStart + chunkSize, DIM);
        for (int i = myStart; i < myEnd; ++i) {
            for (int j = 0; j < DIM; ++j) {
                if (matrix[i*DIM + j] % 2 != 0) {
                    ++result[p];
                }
            }
        }
    }
    pool.join();
    odds = 0;
    for (int p = 0; p < P; ++p) {
        odds += result[p];
    }
}
```

![](./images/02%20-%20threads%20speed%20up%20example%201.png)

The above computation results are from a 24 hardware threads . The graph shows that as we increase number of threads, the speedup is not linear. From 2nd thread, speed drops significantly. It increase in a non linear fashion till 20 threads. Significant improvement from using 1 thread. After that, adding more threads does not help at all. The speedup starts to drop till 24 threads. This is not ideal scalability.

Let us make a small change to the code.

```c++
int result[P];

// Each of P parallel workers processes 1/P-th of the data
// the p-th worker records its partial count in result[p]
for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
        int count = 0;
        int chunkSize = DIM/P + 1;
        int myStart = p * chunkSize;
        int myEnd = min(myStart + chunkSize, DIM);
        for (int i = myStart; i < myEnd; ++i) {
            for (int j = 0; j < DIM; ++j) {
                if (matrix[i*DIM + j] % 2 != 0) {
                    ++count;
                }
            }
        }
        result[p] = count;
    }
    pool.join();
    odds = 0;
    for (int p = 0; p < P; ++p) {
        odds += result[p];
    }
}
```

Instead of updating `result[p]` inside the inner loop, we use a local variable `count` to count number of odd elements in the chunk assigned to the thread. After processing the chunk, we update `result[p]` with the value of `count`.

Everything about this code says its performance should be worse than previous code since we doing an extra declaration and assignment. But the results are surprising.

![](./images/03%20-%20threads%20speed%20up%20example%202.png)

We get a near perfect linear speedup as we increase number of threads. This is a significant improvement over previous code and is counter intuitive.
