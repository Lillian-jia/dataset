#!/bin/bash

if [[ -e ./fuzz-output ]]; then
	cd ./fuzz-output
	rm -rf default && mkdir default default/corpus

	cd ..
fi

/root/Mul_test/afl-api-main/afl-clang++ ./11/*.cpp  -o exe-binary -I/root/Projects/arrow-nanoarrow-afl/src/nanoarrow -L/root/Projects/arrow-nanoarrow-afl/build -lnanoarrow -lpthread


LD_LIBRARY_PATH=/root/Projects/arrow-nanoarrow-afl/build /root/Mul_test/afl-api-main/afl-fuzz -a -i ./input -o ./fuzz-output ./exe-binary @@
