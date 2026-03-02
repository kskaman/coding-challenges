import sys
from collections import Counter
import heapq
from typing import Dict, Optional, Tuple, List

# ---------- Step 1: Calculate frequencies ----------
def calculate_frequencies(filename: str) -> Counter:
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    return Counter(text)

# ---------- Step 2: Huffman Tree ----------
class HuffmanNode:
    def __init__(self, character: Optional[str], frequency: int):
        self.character = character
        self.frequency = frequency
        self.leftChild: Optional["HuffmanNode"] = None
        self.rightChild: Optional["HuffmanNode"] = None

    def __lt__(self, other: "HuffmanNode"):
        return self.frequency < other.frequency

def build_huffman_tree(freq_items: List[Tuple[str, int]]) -> HuffmanNode:
    min_heap = [HuffmanNode(ch, fr) for ch, fr in freq_items]
    heapq.heapify(min_heap)

    # edge case: file has only one unique char
    if len(min_heap) == 1:
        root = HuffmanNode(None, min_heap[0].frequency)
        root.leftChild = min_heap[0]
        return root

    while len(min_heap) > 1:
        left = heapq.heappop(min_heap)
        right = heapq.heappop(min_heap)

        parent = HuffmanNode(None, left.frequency + right.frequency)
        parent.leftChild = left
        parent.rightChild = right
        heapq.heappush(min_heap, parent)

    return min_heap[0]

# ---------- Step 3: Build code table ----------
def build_code_table(root: HuffmanNode) -> Dict[str, str]:
    codes: Dict[str, str] = {}

    def dfs(node: Optional[HuffmanNode], path: str):
        if node is None:
            return
        if node.character is not None:
            # If there's only one char, give it a valid code
            codes[node.character] = path if path else "0"
            return
        dfs(node.leftChild, path + "0")
        dfs(node.rightChild, path + "1")

    dfs(root, "")
    return codes

# ---------- Step 4: Write header ----------
def write_header_to_file(output_filename: str, frequencies: Dict[str, int]):
    with open(output_filename, "wb") as out_file:
        num_characters = len(frequencies)
        out_file.write(num_characters.to_bytes(4, "big"))
        for ch, fr in frequencies.items():
            encoded_ch = ch.encode("utf-8")
            out_file.write(len(encoded_ch).to_bytes(1, "big")) # Write length of encoded char
            out_file.write(encoded_ch)
            out_file.write(fr.to_bytes(4, "big"))

        out_file.write(b"\0")  # header end marker
    

# ---------- Updated Step 5: Encode + write content ----------
def encode_and_write_content(input_filename: str, output_filename: str, code_table: Dict[str, str]):
    try:
        with open(input_filename, "r", encoding="utf-8") as in_file, open(output_filename, "ab") as out_file:
            buffer = 0
            buffer_length = 0

            while (char := in_file.read(1)):
                code = code_table[char]
                for bit in code:
                    # bit is a string '0' or '1'
                    buffer = (buffer << 1) | int(bit)  # Add the bit to the buffer
                    buffer_length += 1

                    if buffer_length == 8:  # Write full byte to file
                        out_file.write(bytes([buffer]))
                        buffer = 0
                        buffer_length = 0

            # Write any remaining bits in the buffer
            if buffer_length > 0:
                buffer = buffer << (8 - buffer_length)  # Pad remaining bits with 0
                out_file.write(bytes([buffer]))

        print(f"Compressed content written to {output_filename}")
    except Exception as e:
        print(f"Error encoding and writing content: {e}")

# ---------- Step 6: Read header (and return frequencies + where data starts) ----------
def read_header(input_filename: str) -> Tuple[Dict[str, int], int]:
    try:
        with open(input_filename, "rb") as f:
            num_characters = int.from_bytes(f.read(4), "big")

            if num_characters <= 0:
                raise ValueError("Invalid header: No characters found.")

            freqs: Dict[str, int] = {}
            for _ in range(num_characters):
                char_len_bytes = f.read(1)
                if not char_len_bytes:
                    raise ValueError("Unexpected end of file while reading character length.")
                char_len = int.from_bytes(char_len_bytes, "big")

                char_bytes = f.read(char_len)
                if len(char_bytes) < char_len:
                    raise ValueError("Unexpected end of file while reading character.")
                ch = char_bytes.decode("utf-8")  # Decode character

                freq_bytes = f.read(4)
                if len(freq_bytes) < 4:
                    raise ValueError("Unexpected end of file while reading frequency.")
                fr = int.from_bytes(freq_bytes, "big")

                freqs[ch] = fr

            # Consume the header-end marker
            marker = f.read(1)
            if marker != b"\0":
                raise ValueError("Header end marker not found or file format mismatch.")

            data_start = f.tell()
            return freqs, data_start
    except Exception as e:
        print(f"Error reading header: {e}")
        sys.exit(1)

# ---------- Step 7: Decode using the tree ----------
def decode_file(input_filename: str, output_filename: str):
    try:
        freqs, data_start = read_header(input_filename)
        root = build_huffman_tree(list(freqs.items()))
        total_chars = sum(freqs.values())  # VERY IMPORTANT: tells us when to stop

        with open(input_filename, "rb") as in_file:
            in_file.seek(data_start)
            compressed_data = in_file.read()

        with open(output_filename, "w", encoding="utf-8") as out_file:
            node = root
            written = 0

            for byte in compressed_data:
                bits = f"{byte:08b}"
                for bit in bits:
                    node = node.leftChild if bit == "0" else node.rightChild

                    if node and node.character is not None:
                        out_file.write(node.character)
                        written += 1
                        if written == total_chars:
                            print(f"Decoded content written to {output_filename}")
                            return  # Stop exactly at original size
                        node = root

        print("Decompression completed successfully.")
    except Exception as e:
        print(f"Error decoding file: {e}")
        sys.exit(1)

# ---------- MAIN ----------
def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python file-compressor.py compress <input.txt> <output.huf>")
        print("  python file-compressor.py decompress <input.huf> <output.txt>")
        sys.exit(1)
    
    mode, input_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]

    if mode == "compress":
        freqs = calculate_frequencies(input_file)
        if not freqs:
            print("Input file is empty. Nothing to compress.")
            sys.exit(1)

        root = build_huffman_tree(list(freqs.items()))
        codes = build_code_table(root)

        write_header_to_file(output_file, dict(freqs))
        encode_and_write_content(input_file, output_file, codes)
        print(f"Compressed -> {output_file}")

    elif mode == "decompress":
        decode_file(input_file, output_file)
        print(f"Decompressed -> {output_file}")

    else:
        print("Invalid mode. Use 'compress' or 'decompress'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
