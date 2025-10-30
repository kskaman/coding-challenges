#include "json_parser.hpp"
#include <iostream>
#include <stdexcept>
#include <sstream>
#include <cctype>
#include <iomanip>

// Lexer implementation
Lexer::Lexer(const std::string &input) : text(input), pos(0), line(1), column(1)
{
    currentChar = pos < text.length() ? text[pos] : '\0';
}

void Lexer::advance()
{
    if (currentChar == '\n')
    {
        line++;
        column = 1;
    }
    else
    {
        column++;
    }

    pos++;
    currentChar = pos < text.length() ? text[pos] : '\0';
}

void Lexer::skipWhitespace()
{
    while (currentChar != '\0' && std::isspace(currentChar))
    {
        advance();
    }
}

std::string Lexer::parseString()
{
    std::string result = "";
    advance(); // Skip opening quote

    while (currentChar != '\0' && currentChar != '"')
    {
        if (currentChar == '\\')
        {
            advance(); // Skip backslash
            if (currentChar == '\0')
            {
                error("Unterminated string escape");
            }

            // Handle escape sequences
            switch (currentChar)
            {
            case '"':
                result += '"';
                break;
            case '\\':
                result += '\\';
                break;
            case '/':
                result += '/';
                break;
            case 'b':
                result += '\b';
                break;
            case 'f':
                result += '\f';
                break;
            case 'n':
                result += '\n';
                break;
            case 'r':
                result += '\r';
                break;
            case 't':
                result += '\t';
                break;
            case 'u':            // Unicode escape - simplified
                result += "\\u"; // Keep as-is for simplicity
                break;
            default:
                error("Invalid escape sequence");
            }
        }
        else
        {
            // Check for control characters
            if (currentChar < 32 && currentChar != '\t')
            {
                error("Control character in string");
            }
            result += currentChar;
        }
        advance();
    }

    if (currentChar != '"')
    {
        error("Unterminated string");
    }

    advance(); // Skip closing quote
    return result;
}

std::string Lexer::parseNumber()
{
    std::string result = "";

    // Handle negative sign
    if (currentChar == '-')
    {
        result += currentChar;
        advance();
    }

    // Integer part
    if (currentChar == '0')
    {
        result += currentChar;
        advance();
        // After 0, can't have more digits unless it's a decimal
        if (std::isdigit(currentChar))
        {
            error("Leading zeros not allowed");
        }
    }
    else if (std::isdigit(currentChar))
    {
        while (std::isdigit(currentChar))
        {
            result += currentChar;
            advance();
        }
    }
    else
    {
        error("Invalid number");
    }

    // Decimal part
    if (currentChar == '.')
    {
        result += currentChar;
        advance();

        if (!std::isdigit(currentChar))
        {
            error("Digit expected after decimal point");
        }

        while (std::isdigit(currentChar))
        {
            result += currentChar;
            advance();
        }
    }

    // Exponent part
    if (currentChar == 'e' || currentChar == 'E')
    {
        result += currentChar;
        advance();

        if (currentChar == '+' || currentChar == '-')
        {
            result += currentChar;
            advance();
        }

        if (!std::isdigit(currentChar))
        {
            error("Digit expected in exponent");
        }

        while (std::isdigit(currentChar))
        {
            result += currentChar;
            advance();
        }
    }

    return result;
}

std::string Lexer::parseKeyword()
{
    std::string result = "";

    while (std::isalpha(currentChar))
    {
        result += currentChar;
        advance();
    }

    return result;
}

void Lexer::error(const std::string &msg)
{
    std::ostringstream oss;
    oss << "Lexer error at line " << line << ", column " << column << ": " << msg;
    throw std::runtime_error(oss.str());
}

Token Lexer::getNextToken()
{
    while (currentChar != '\0')
    {
        if (std::isspace(currentChar))
        {
            skipWhitespace();
            continue;
        }

        switch (currentChar)
        {
        case '{':
            advance();
            return Token(TokenType::LBRACE, "{");
        case '}':
            advance();
            return Token(TokenType::RBRACE, "}");
        case '[':
            advance();
            return Token(TokenType::LBRACKET, "[");
        case ']':
            advance();
            return Token(TokenType::RBRACKET, "]");
        case ',':
            advance();
            return Token(TokenType::COMMA, ",");
        case ':':
            advance();
            return Token(TokenType::COLON, ":");
        case '"':
        {
            std::string str = parseString();
            return Token(TokenType::STRING, str);
        }
        case '-':
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
        {
            std::string num = parseNumber();
            return Token(TokenType::NUMBER, num);
        }
        case 't':
        case 'f':
        case 'n':
        {
            std::string keyword = parseKeyword();
            if (keyword == "true")
            {
                return Token(TokenType::TRUE, "true");
            }
            else if (keyword == "false")
            {
                return Token(TokenType::FALSE, "false");
            }
            else if (keyword == "null")
            {
                return Token(TokenType::NULL_TOKEN, "null");
            }
            else
            {
                error("Invalid keyword: " + keyword);
            }
            break;
        }
        default:
            error("Unexpected character: " + std::string(1, currentChar));
        }
    }

    return Token(TokenType::EOF_TOKEN, "");
}