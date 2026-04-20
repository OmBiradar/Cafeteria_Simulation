.PHONY: all configure build run test clean

all: run

# Generates the CMake build system (only needs to run if CMakeLists.txt changes, 
# but safe to run every time)
configure:
	cmake -B build

# Compiles the actual C++ code
build: configure
	cmake --build build

# Runs the compiled executable
run: build
	./build/cafeteria_sim

# Compiles and runs the tests using CTest
test: build
	cd build && ctest --output-on-failure

# Wipes the build directory completely
clean:
	rm -rf build results