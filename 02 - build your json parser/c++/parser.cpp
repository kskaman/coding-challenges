#include "json_parser.hpp"
#include <iostream>
#include <stdexcept>
#include <sstream>
#include <string>

// Parser implementation
Parser::Parser(Lexer &lex) : lexer(lex), currentToken(TokenType::INVALID)
{
    currentToken = lexer.getNextToken(); // Prime the parser
}

void Parser::checkToken(TokenType expected)
{
    if (currentToken.type != expected)
    {
        std::ostringstream oss;
        oss << "Expected token type " << static_cast<int>(expected)
            << " but got " << static_cast<int>(currentToken.type);
        throw std::runtime_error(oss.str());
    }
    currentToken = lexer.getNextToken();
}

JsonPtr Parser::parse()
{
    JsonPtr result = parseValue();

    // Check for trailing content
    if (currentToken.type != TokenType::EOF_TOKEN)
    {
        throw std::runtime_error("Extra content after JSON value");
    }

    return result;
}

JsonPtr Parser::parseValue()
{
    switch (currentToken.type)
    {
    case TokenType::LBRACE:
        return parseObject();
    case TokenType::LBRACKET:
        return parseArray();
    case TokenType::STRING:
        return parseString();
    case TokenType::NUMBER:
        return parseNumber();
    case TokenType::TRUE:
    case TokenType::FALSE:
        return parseBoolean();
    case TokenType::NULL_TOKEN:
        return parseNull();
    default:
        throw std::runtime_error("Unexpected token in value");
    }
}

JsonPtr Parser::parseObject()
{
    auto obj = std::make_shared<JsonObject>();
    checkToken(TokenType::LBRACE); // consume {

    // Handle empty object
    if (currentToken.type == TokenType::RBRACE)
    {
        checkToken(TokenType::RBRACE);
        return obj;
    }

    while (true)
    {
        // Expect string key
        if (currentToken.type != TokenType::STRING)
        {
            throw std::runtime_error("Expected string key in object");
        }
        std::string key = currentToken.value;
        checkToken(TokenType::STRING);

        // Expect colon
        checkToken(TokenType::COLON);

        // Parse value
        JsonPtr value = parseValue();
        obj->properties.push_back({key, value});

        // Check for continuation
        if (currentToken.type == TokenType::COMMA)
        {
            checkToken(TokenType::COMMA);

            // Check for trailing comma
            if (currentToken.type == TokenType::RBRACE)
            {
                throw std::runtime_error("Trailing comma in object");
            }
        }
        else if (currentToken.type == TokenType::RBRACE)
        {
            break;
        }
        else
        {
            throw std::runtime_error("Expected comma or } in object");
        }
    }

    checkToken(TokenType::RBRACE);
    return obj;
}

JsonPtr Parser::parseArray()
{
    auto arr = std::make_shared<JsonArray>();
    checkToken(TokenType::LBRACKET); // consume [

    // Handle empty array
    if (currentToken.type == TokenType::RBRACKET)
    {
        checkToken(TokenType::RBRACKET);
        return arr;
    }

    while (true)
    {
        // Parse value
        JsonPtr value = parseValue();
        arr->elements.push_back(value);

        // Check for continuation
        if (currentToken.type == TokenType::COMMA)
        {
            checkToken(TokenType::COMMA);

            // Check for trailing comma
            if (currentToken.type == TokenType::RBRACKET)
            {
                throw std::runtime_error("Trailing comma in array");
            }
        }
        else if (currentToken.type == TokenType::RBRACKET)
        {
            break;
        }
        else
        {
            throw std::runtime_error("Expected comma or ] in array");
        }
    }

    checkToken(TokenType::RBRACKET);
    return arr;
}

JsonPtr Parser::parseString()
{
    auto str = std::make_shared<JsonString>(currentToken.value);
    checkToken(TokenType::STRING);
    return str;
}

JsonPtr Parser::parseNumber()
{
    double value = std::stod(currentToken.value);
    auto num = std::make_shared<JsonNumber>(value);
    checkToken(TokenType::NUMBER);
    return num;
}

JsonPtr Parser::parseBoolean()
{
    bool value = (currentToken.type == TokenType::TRUE);
    auto boolean = std::make_shared<JsonBoolean>(value);
    checkToken(currentToken.type); // consume true/false
    return boolean;
}

JsonPtr Parser::parseNull()
{
    auto null = std::make_shared<JsonNull>();
    checkToken(TokenType::NULL_TOKEN);
    return null;
}

// JSON Value toString implementations
std::string JsonObject::toString(int indent) const
{
    if (properties.empty())
    {
        return "{}";
    }

    std::string result = "{\n";
    std::string indentStr(indent + 2, ' ');

    for (size_t i = 0; i < properties.size(); i++)
    {
        result += indentStr + "\"" + properties[i].first + "\": ";
        result += properties[i].second->toString(indent + 2);

        if (i < properties.size() - 1)
        {
            result += ",";
        }
        result += "\n";
    }

    result += std::string(indent, ' ') + "}";
    return result;
}

std::string JsonArray::toString(int indent) const
{
    if (elements.empty())
    {
        return "[]";
    }

    std::string result = "[\n";
    std::string indentStr(indent + 2, ' ');

    for (size_t i = 0; i < elements.size(); i++)
    {
        result += indentStr + elements[i]->toString(indent + 2);

        if (i < elements.size() - 1)
        {
            result += ",";
        }
        result += "\n";
    }

    result += std::string(indent, ' ') + "]";
    return result;
}

std::string JsonString::toString(int indent) const
{
    return "\"" + value + "\"";
}

std::string JsonNumber::toString(int indent) const
{
    std::ostringstream oss;
    oss << value;
    return oss.str();
}

std::string JsonBoolean::toString(int indent) const
{
    return value ? "true" : "false";
}

std::string JsonNull::toString(int indent) const
{
    return "null";
}
