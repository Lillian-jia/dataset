#!/bin/bash

cd ./fuzz-output
rm -rf default && mkdir default default/corpus

cd ..

/root/Mul_test/afl-api-main/afl-clang++ ./11/*.cpp  -o exe-binary -I/root/Projects/apr-afl/include -L/root/Projects/apr-afl/.libs -lapr-2 -lpthread


LD_LIBRARY_PATH=/root/Projects/apr-afl/.libs /root/Mul_test/afl-api-main/afl-fuzz -a -i ./input -o ./fuzz-output ./exe-binary @@
