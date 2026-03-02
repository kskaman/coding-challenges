# Compression Tool

This repository contains a simple file compression and decompression tool implemented in both C++ and Python using Huffman coding. The tool reads an input text file, compresses it into a binary format, and can also decompress the binary file back into the original text format.

## Implementation Notes

A Compression Tool typically involves the following steps:

1. **Calculate Character Frequencies**: Read the input file and calculate the frequency of each character.
2. **Build Huffman Tree**: Build the Huffman tree based on character frequencies.
3. **Generate Codes**: Traverse the Huffman tree to generate binary codes for each character
4. **Encode the File**: Replace each character in the input file with its corresponding binary code and write the encoded data to a binary file.
5. **Decode the File**: Read the binary file, reconstruct the Huffman tree, and decode the binary data back into the original text.

## References used

- Chapter 14: Huffman Codes - Algorithms Illuminated by Tim Roughgarden
