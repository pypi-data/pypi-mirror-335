#pragma once
#include <string>
#include <pybind11/pybind11.h>

class BaseExchangeConnector
{
public:
    virtual void connect(const std::string& uri) = 0;
    
    virtual void connect_private(const std::string& uri,
        const std::string& api_key,
        const std::string& secret,
        const std::string& pass_phrase) = 0;
    
    virtual void disconnect() = 0;

    virtual void subscribe(const std::string& channel, const std::string& inst_id) = 0;
    
    virtual void subscribe_private(const std::string& channel) = 0;

    virtual void unsubscribe(const std::string& channel, const std::string& inst_id) = 0;

    virtual void place_order(const std::string& ord_id, const std::string& inst_id,
        const std::string& side, const std::string& sz) = 0;

    virtual void cancel_order(const std::string& msg_id, const std::string& ord_id, const std::string& inst_id) = 0;
};