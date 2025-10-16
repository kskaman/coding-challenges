#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cctype>
#include <cstdint>
#include <iomanip>

#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif

using std::cerr;
using std::cout;
using std::ifstream;
using std::istream;
using std::string;
using u64 = std::uint64_t;

struct Counts
{
    u64 lines = 0; // -l
    u64 words = 0; // -w
    u64 bytes = 0; // -c
    u64 chars = 0; // -m (UTF-8 code points)
};

struct Sel
{
    bool l = false, w = false, c = false, m = false;
    bool any() const { return l || w || c || m; }
};

static void usage()
{
    std::cerr << "ccwc — word, line, character, and byte count\n"
                 "\n"
                 "USAGE\n"
                 "  ccwc [-c|-l|-w|-m|-(any combo like -lw, -lwmc)] <filename>\n"
                 "  ccwc <filename>                 (defaults to -l -w -c)\n"
                 "  ccwc [-c|-l|-w|-m|-(combos)]    (read from standard input)\n"
                 "\n"
                 "OPTIONS\n"
                 "  -c   byte count\n"
                 "  -l   line count (counts '\\n')\n"
                 "  -w   word count (runs of non-whitespace)\n"
                 "  -m   character count (UTF-8 code points)\n"
                 "\n"
                 "DEFAULTS\n"
                 "  • No option given  -> prints -l -w -c\n"
                 "  • No filename      -> reads from standard input\n"
                 "\n";
}

// Parse flags like "-lwmc". Returns Sel with bits toggled; empty if not a flag.
static Sel parse_flags(const string &s)
{
    Sel sel;
    if (s.size() >= 2 && s[0] == '-')
    {
        for (size_t i = 1; i < s.size(); ++i)
        {
            switch (s[i])
            {
            case 'l':
                sel.l = true;
                break;
            case 'w':
                sel.w = true;
                break;
            case 'c':
                sel.c = true;
                break;
            case 'm':
                sel.m = true;
                break;
            default:
                return Sel{}; // invalid -> not a flags string
            }
        }
    }
    return sel;
}

// If no flags were provided, default to -l -w -c (challenge spec).
static Sel default_sel_if_empty(Sel sel)
{
    if (!sel.any())
    {
        sel.l = sel.w = sel.c = true;
    }
    return sel;
}

// Single-pass counter. Buffer is vector<char>. We cast to unsigned char only where needed.
static bool count_stream(istream &in, const Sel &sel, Counts &out)
{
    const size_t BUF = 64 * 1024;
    std::vector<char> buf(BUF);
    bool in_word = false;

    while (true)
    {
        in.read(buf.data(), static_cast<std::streamsize>(buf.size()));
        std::streamsize got = in.gcount();
        if (got <= 0)
            break;

        if (sel.c)
            out.bytes += static_cast<u64>(got);

        for (std::streamsize i = 0; i < got; ++i)
        {
            char ch = buf[static_cast<size_t>(i)];

            // -l: lines
            if (sel.l && ch == '\n')
            {
                out.lines++;
            }

            // -w: word transitions (use unsigned char for ctype)
            if (sel.w)
            {
                unsigned char uch = static_cast<unsigned char>(ch);
                bool is_space = (std::isspace(uch) != 0);
                if (is_space)
                {
                    in_word = false;
                }
                else if (!in_word)
                {
                    out.words++;
                    in_word = true;
                }
            }

            // -m: UTF-8 code points — count non-continuation bytes
            if (sel.m)
            {
                unsigned char uch = static_cast<unsigned char>(ch);
                if ((uch & 0xC0) != 0x80)
                {
                    out.chars++;
                }
            }
        }

        if (!in && !in.eof())
        {
            // real read error
            return false;
        }
    }
    return true;
}

static bool count_file(const string &path, const Sel &sel, Counts &out)
{
    std::ifstream in(path, std::ios::binary);
    if (!in)
        return false;
    return count_stream(in, sel, out);
}

static void print_selected(const Sel &sel, const Counts &c, const string *fname = nullptr)
{
    // Canonical wc order: l, w, c, m
    if (sel.l)
        cout << std::setw(8) << c.lines;
    if (sel.w)
        cout << std::setw(8) << c.words;
    if (sel.c)
        cout << std::setw(8) << c.bytes;
    if (sel.m)
        cout << std::setw(8) << c.chars;
    if (fname)
        cout << " " << *fname;
    cout << "\n";
}

int main(int argc, char *argv[])
{
    std::ios::sync_with_stdio(false);

#ifdef _WIN32
    // If we'll read stdin (no filename provided), switch stdin to binary so -c is exact.
    if (argc == 1 || (argc == 2 && parse_flags(argv[1]).any()))
    {
        _setmode(_fileno(stdin), _O_BINARY);
    }
#endif

    // Case 1: no args -> stdin with default (-l -w -c)
    if (argc == 1)
    {
        Sel sel = default_sel_if_empty(Sel{});
        Counts c;
        if (!count_stream(std::cin, sel, c))
        {
            cerr << "ccwc: failed to read from stdin\n";
            return 1;
        }
        print_selected(sel, c);
        return 0;
    }

    // Case 2: one arg -> either flags (stdin) OR filename (default)
    if (argc == 2)
    {
        string a1 = argv[1];
        Sel sel = parse_flags(a1);
        if (sel.any())
        {
            Counts c;
            if (!count_stream(std::cin, sel, c))
            {
                cerr << "ccwc: failed to read from stdin\n";
                return 1;
            }
            print_selected(sel, c);
            return 0;
        }
        else
        {
            // treat as filename with default selection
            Sel def = default_sel_if_empty(Sel{});
            Counts c;
            if (!count_file(a1, def, c))
            {
                cerr << "ccwc: cannot open file: " << a1 << "\n";
                return 1;
            }
            print_selected(def, c, &a1);
            return 0;
        }
    }

    // Case 3: two args -> flags + filename
    if (argc == 3)
    {
        string flags = argv[1];
        string path = argv[2];
        Sel sel = parse_flags(flags);
        if (!sel.any())
        {
            usage();
            return 1;
        }

        Counts c;
        if (!count_file(path, sel, c))
        {
            cerr << "ccwc: cannot open file: " << path << "\n";
            return 1;
        }
        print_selected(sel, c, &path);
        return 0;
    }

    usage();
    return 1;
}