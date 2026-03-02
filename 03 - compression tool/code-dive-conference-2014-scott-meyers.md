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

> This tells us thread memory management matters.

### Understanding CPU Caches

To understand why the above two examples behave differently, we need to understand CPU caches.

CPU cache is a small sized type of volatile computer memory that provides high-speed data access to a processor and stores frequently used computer programs, applications and data.

Three common levels of CPU cache:

- Data Cache (D-cache, D$) : Caches data being read/written by CPU.
- Instruction Cache (I-cache, I$) : Caches instructions being executed by CPU.
- Translation Lookaside Buffer (TLB) : Caches virtual to physical address translations.

Cache Hierarchy (multiple levels of cache) is common in modern CPUs. Eg. Intel Core i7-9xx processor:

- 32 KB L1 D-cache per core, 32 KB L1 I-cache per core - shared by 2 HW threads
- 256 KB L2 cache per core - shared by 2 HW threads, holds both instructions and data
- 8 MB L3 cache - shared by 4 cores (8 HW threads), holds both instructions and data

![](./images/04-%20intel%20i7%209xx%20caches%20picture.png)

**Cpu Cache Characteristics:**

- Assume 100MB program at runtime (code + data):
  - 8% fits in core i79xx's L3 cache - L3 cache shared by every running process
  - 0.25% fits in each L2 cache
  - 0.03% fits in each L1 cache

**Caches much faster than main memory**

- For core i7-9xx:
  - L1 cache latency: ~4 cycles
  - L2 cache latency: ~12 cycles
  - L3 cache latency: ~39 cycles
  - Main memory latency: ~107 cycles : 27 times slower than L1 cache!, 100% CPU utilization -> 99% CPU idle time

Main memory is orders of magnitude slower than CPU caches. Thus, we want to maximize cache hits and minimize cache misses. It fells like Main memory is not even there. Thus, effective memory = CPU Cache Memory.

**Effective Memory = CPU Cache Memory**

**Small is fast**

- No time/space tradeoff at hardware level.
- Compact, well-localized code that fits in cache is fastest
- Compact data structures that fit in cache are fastest
- Data structure traversals touching only cached data are fastest

> time/space tradeoff is a software level concept. At hardware level, small is always fast. time/space tradeoff means we can use more space/memory to save time ( or improve speed) or vice versa. But at hardware level, smaller data means it fits in cache and is always faster.

### Cache Lines and Spatial Locality

When we access memory, CPU does not load just the requested byte/word. It loads a block of contiguous memory called cache line. What it means is when CPU requests a byte from memory address X, it loads a block of memory starting from address X to X + (cache line size - 1) into cache.

- Cache consists of _lines_ (typically 64 bytes each), each holding a contiguous block of memory.
- When CPU requests a byte from memory, the entire line containing that byte is loaded into cache.
- Subsequent accesses to other bytes in that line hit the cache (fast!).
- Accesses to bytes outside that line miss the cache (slow!).
- when we write to memory, the entire cache line is written back to main memory.

> This explains why row major traversal is faster than column major traversal. In row major traversal, we access contiguous memory locations in a row. Thus, when we access the first element of the row, the entire cache line containing that element is loaded into cache. Subsequent accesses to other elements in the same row hit the cache and are fast.

![](./images/05%20-%20cache%20line%20row%20vs%20column%20traversal.png)

### Cache Misses and Performance

When CPU accesses memory, it checks if the requested data is in cache. If it is, it's a cache hit and data is accessed quickly. If not, it's a cache miss and data has to be fetched from main memory, which is slow.

- Cache Hit: Requested data is in cache -> fast access
- Cache Miss: Requested data is not in cache -> slow access (fetch from main memory)

### Cache Line Prefetching

To mitigate the performance impact of cache misses, modern CPUs employ a technique called cache line prefetching. When a CPU detects a pattern of memory access, it anticipates future requests and preloads the corresponding cache lines into the cache before they are explicitly requested.

**Example:**

- Forward traversal through cache line n prefetches cache line n+1.
  - When accessing elements in a forward sequential manner, the CPU predicts that the next cache line will be needed soon and preloads it into the cache.
- Backward traversal through cache line n prefetches cache line n-1.
  - When accessing elements in a backward sequential manner, the CPU predicts that the previous cache line will be needed soon and preloads it into the cache.

> However, for unpredictable access patterns (like column-major traversal), prefetching may not be effective.

> Going linearly through memory allows CPU to prefetch cache lines effectively, reducing cache misses and improving performance.

#### Implications for Software Developers

- Locality counts: Reads/writes at address A -> contents near A already caches on same cache line or nearby cache lines that was prefetched. Thus, accessing data that is close together in memory is faster.

- Predictive access patterns count: Predictive patterns like linear forward or linear backward allow prefetching to work well. Unpredictable patterns (like random access) do not benefit from prefetching.

- Linear array traversals are very cache friendly : This provides excellent locality, predictive traversal patterns. Linear search arrays can beat tree structures for small to medium sized data sets that fit in cache. Big O wins for large n, so when data does not fit in cache, tree structures are better.

## Cache Coherency

Lets talk about when we have same copy of data in multiple caches. Eg. In multi core processors, each core has its own cache. If two cores are working on same data, they will have their own copy of data in their respective caches.

When one core modifies its copy of data, other cores need to be made aware of this change to maintain consistency. This is where cache coherency protocols come into play.

For an i7-9xx processor,

![](./images/06%20-%20cache%20coherency%20i7.png)

Assume both cores have caches the value at (virtual) address A.

- Whether in L1 or L2 makes no difference

Consider :

- Core 0 writes A.
- Core 1 reads A.

What value does core 1 read ?

Hardware invalidates core 1's cache line containing A when core 0 writes A. It then puts new value in Core 1's cache(s).

This happens automatically via cache coherency protocols implemented in hardware.

> Software Developer does not need worry about it. Bit it takes.

While programming multiple threads, we must avoid races.

> Races happen when two threads access same memory location concurrently and at least one of the accesses is a write.

> Try avoid data races

> **Rule of the Game**: As long as you synchronize access to shared data, use atomic machine instructions, something to make sure that there is a way to prevent individual threads from simultaneously accessing machine memory where one of them is a writer, hardware takes care of cache coherency for you.

But its not free. Hardware has to do the work to make sure we see a coherent picture of memory. This can impact performance. _So, we should always try to avoid sharing data between threads._

#### False Sharing

When two threads on different cores modify variables that reside on the same cache line, it causes performance degradation due to cache coherency traffic. This is known as false sharing.

![](./images/07%20-%20false%20sharing.png)

**Herb Sutter's issue**

```c++
int result[P];

// Each of P parallel workers processes 1/P-th of the data
for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
        result[p] = 0; // Potential false sharing here
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
}
```

and his solution

```c++
int result[P];

// Each of P parallel workers processes 1/P-th of the data
for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
        int count = 0; // No false sharing here
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
        // we have to write back the result but its only once
        // whereas in previous code we were writing to result[p] multiple times
        // in different threads
        result[p] = count;
    }
}
```

In the first code, multiple threads are writing to different elements of the `result` array. If these elements reside on the same cache line, it causes false sharing. Each thread's write invalidates the cache line in other threads' caches, leading to performance degradation.

In the second code, each thread uses a local variable `count` to accumulate its result. This variable is stored in the thread's own stack, avoiding false sharing. Only after the computation is done, the thread writes its result to the `result` array, which minimizes cache coherency traffic.

![](./images/08%20-%20false%20sharing.png)

Problems arise only when **all** are true:

- Independent values/variables fall on one cache line.
- Different cores concurrently access that line
- Frequently
- At least one is writer.

All types of data are susceptible:

- globals/statics : They are allocated in a fixed memory location. If multiple threads access global/static variables that fall on the same cache line, it can lead to false sharing.
- heap allocated : When multiple threads allocate memory from the heap, the memory allocator may return memory blocks that are close together in memory. If these blocks fall on the same cache line and are accessed concurrently by different threads, it can lead to false sharing.
- automatics and thread-locals : Automatic variables (local variables) and thread-local storage are allocated on the stack. If multiple threads have local variables that fall on the same cache line and access them concurrently, it can lead to false sharing.

> ## Guidance

- **For data**:

  - _where practical, employ linear array traversals_: Go through data in order like reading a book page by page.
    Example:

  ```c++
    // GOOD: Go through array in order (fast)
    for (int i = 0; i < 1000; i++) {
        process(array[i]);
    }

    // BAD: Jump around randomly (slow)
    for (int i = 0; i < 1000; i++) {
        process(array[random_index]);
    }
  ```

  Think of your computer's memory like a library. When you ask for one book, the librarian brings you that book plus several books from the same shelf (cache line). If you read books in order, you use all the books the librarian brought. If you jump around randomly, you waste the librarian's effort.

  - _structure data to minimize cache line sharing between threads_: Don't let multiple threads work on data that resides on the same cache line.
    Example:

    ```c++
    // BAD: Potential false sharing
    struct SharedData {
        int value1; // Thread 1 works on this
        int value2; // Thread 2 works on this
    };

    // GOOD: No false sharing
    struct PaddedData {
        int value1; // Thread 1 works on this
        char padding[60]; // Padding to ensure value2 is on a different cache line
        int value2; // Thread 2 works on this
    };
    ```

    Imagine two people trying to write on the same piece of paper at the same time - they'll interfere with each other. Give each person their own paper!

  - _be alert for false sharing: unexpected performance degradation in multithreaded code may be due to false sharing_: Look out for sudden slowdowns when multiple threads are involved; it might be because they're stepping on each other's toes in the cache.

  ```c++
  // SLOW: Multiple threads writing to result[0], result[1], result[2]...
  // These might be on the same "cache line" causing interference
  for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
        for (...) {
            ++result[p];  // Each thread keeps writing here
        }
    }
  }

  // FAST: Each thread uses its own local variable

  for (int p = 0; p < P; ++p) {
    pool.run[&, p] {
    int count = 0; // Private to this thread
    for (...) {
      ++count; // No interference
    }
    result[p] = count; // Write once at the end
    }
  }

  ```

- **For code**:
- _strive for compact, well-localized code that fits in cache_

  ```c++
  // GOOD: Short, focused function that fits in cache
  int addNumbers(int a, int b) {
      return a + b;
  }

  // BAD: Huge function with lots of code
  int massiveFunction() {
      // 500 lines of code...
      // Won't fit in instruction cache
      // CPU has to keep loading new parts
  }
  ```

- _consider inlining small, frequently called functions to improve locality_: For tiny functions you use a lot, copy-paste the code directly instead of making a function call.

  ```c++
  // Normal function call
  int square(int x) { return x * x; }
  for (int i = 0; i < 1000000; i++) {
      result += square(i);  // Lots of function call overhead
  }

  // Inlined version (compiler does this automatically with 'inline')
  for (int i = 0; i < 1000000; i++) {
      result += i * i;  // No function call overhead
  }
  ```

  Think of it like this: if you have a tiny recipe you use all the time, it's faster to memorize it than to look it up in a big cookbook every time.

- _take advantage of PGO (Profile Guided Optimization) and WPO (Whole Program Optimization) features of modern compilers to help the compiler generate better-optimized code that fits in cache_: Use special compiler features that make your code faster by learning from how it actually runs.

  ```c++
  // Profile Guided Optimization (PGO)
  // Step 1: Compile with profiling
  g++ -fprofile-generate mycode.cpp -o myprogram

  // Step 2: Run your program with typical data
  ./myprogram typical_input.txt

  // Step 3: Recompile using the profile data
  g++ -fprofile-use mycode.cpp -o myprogram_optimized
  ```

  The compiler learns which parts of your code run most often and optimizes those parts more aggressively.
