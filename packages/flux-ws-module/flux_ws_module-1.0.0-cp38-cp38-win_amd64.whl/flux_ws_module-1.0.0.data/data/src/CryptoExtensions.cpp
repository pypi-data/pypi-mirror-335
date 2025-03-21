#include "CryptoExtensions.h"
#include <websocketpp/config/asio_client.hpp>
#include <websocketpp/client.hpp>
#include <time.h>
#include <stdio.h>
#include <iomanip>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/archive/iterators/binary_from_base64.hpp>
#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/transform_width.hpp>
#include <boost/algorithm/string.hpp>
  
std::string CryptoExtensions::encode64(const std::string& val) {
    using namespace boost::archive::iterators;
    using It = base64_from_binary<transform_width<std::string::const_iterator, 6, 8>>;
    auto tmp = std::string(It(std::begin(val)), It(std::end(val)));
    return tmp.append((3 - val.size() % 3) % 3, '=');
}

std::string CryptoExtensions::CalcHmacSHA256(std::string decodedKey, std::string msg)
{
    std::array<unsigned char, EVP_MAX_MD_SIZE> hash;
    unsigned int hashLen;

    HMAC(
        EVP_sha256(),
        decodedKey.data(),
        static_cast<int>(decodedKey.size()),
        reinterpret_cast<unsigned char const*>(msg.data()),
        static_cast<int>(msg.size()),
        hash.data(),
        &hashLen
    );

    return std::string{ reinterpret_cast<char const*>(hash.data()), hashLen };
}
