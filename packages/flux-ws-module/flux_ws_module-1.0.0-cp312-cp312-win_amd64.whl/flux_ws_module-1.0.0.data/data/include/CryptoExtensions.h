#pragma once
#include <string>

class CryptoExtensions {
public:
    std::string CalcHmacSHA256(std::string decodedKey, std::string msg);
    std::string encode64(const std::string& input);
};