#pragma once
#include <string>
#include <vector>
#include <memory>

// Token types for JSON
enum class TokenType
{
    LBRACE,     // {
    RBRACE,     // }
    LBRACKET,   // [
    RBRACKET,   // ]
    COMMA,      // ,
    COLON,      // :
    STRING,     // "text"
    NUMBER,     // 123, -45.67, 1e10
    TRUE,       // true
    FALSE,      // false
    NULL_TOKEN, // null (NULL is reserved in C++)
    EOF_TOKEN,  // end of input
    INVALID     // invalid token
};

struct Token
{
    TokenType type;
    std::string value;

    Token(TokenType t, const std::string &v = "") : type(t), value(v) {}
};

// Forward declaration for JSON values
class JsonValue;
using JsonPtr = std::shared_ptr<JsonValue>;

// Lexer class - converts text to tokens
class Lexer
{
private:
    std::string text;
    size_t pos;
    size_t line;
    size_t column;
    char currentChar;

    void advance();
    void skipWhitespace();
    std::string parseString();
    std::string parseNumber();
    std::string parseKeyword();
    void error(const std::string &msg);

public:
    explicit Lexer(const std::string &input);
    Token getNextToken();
};

// Parser class - converts tokens to JSON structure
class Parser
{
private:
    Lexer &lexer;
    Token currentToken;

    void checkToken(TokenType expected);
    JsonPtr parseValue();
    JsonPtr parseObject();
    JsonPtr parseArray();
    JsonPtr parseString();
    JsonPtr parseNumber();
    JsonPtr parseBoolean();
    JsonPtr parseNull();

public:
    explicit Parser(Lexer &lex);
    JsonPtr parse();
};

// JSON Value types
enum class JsonType
{
    OBJECT,
    ARRAY,
    STRING,
    NUMBER,
    BOOLEAN,
    NULL_VALUE
};

// Base class for JSON values
class JsonValue
{
public:
    JsonType type;

    explicit JsonValue(JsonType t) : type(t) {}
    virtual ~JsonValue() = default;
    virtual std::string toString(int indent = 0) const = 0;
};

// Specific JSON value types
class JsonObject : public JsonValue
{
public:
    std::vector<std::pair<std::string, JsonPtr>> properties;

    JsonObject() : JsonValue(JsonType::OBJECT) {}
    std::string toString(int indent = 0) const override;
};

class JsonArray : public JsonValue
{
public:
    std::vector<JsonPtr> elements;

    JsonArray() : JsonValue(JsonType::ARRAY) {}
    std::string toString(int indent = 0) const override;
};

class JsonString : public JsonValue
{
public:
    std::string value;

    explicit JsonString(const std::string &val) : JsonValue(JsonType::STRING), value(val) {}
    std::string toString(int indent = 0) const override;
};

class JsonNumber : public JsonValue
{
public:
    double value;

    explicit JsonNumber(double val) : JsonValue(JsonType::NUMBER), value(val) {}
    std::string toString(int indent = 0) const override;
};

class JsonBoolean : public JsonValue
{
public:
    bool value;

    explicit JsonBoolean(bool val) : JsonValue(JsonType::BOOLEAN), value(val) {}
    std::string toString(int indent = 0) const override;
};

class JsonNull : public JsonValue
{
public:
    JsonNull() : JsonValue(JsonType::NULL_VALUE) {}
    std::string toString(int indent = 0) const override;
};
