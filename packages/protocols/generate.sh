cd definitions
protoc --python_out=pyi_out:../generated/python/ *.proto
cd ..

