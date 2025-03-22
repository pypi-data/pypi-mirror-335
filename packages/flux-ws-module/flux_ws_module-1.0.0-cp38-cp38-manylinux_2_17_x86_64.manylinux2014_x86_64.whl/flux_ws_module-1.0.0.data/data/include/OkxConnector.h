#pragma once
#include <websocketpp/config/asio_client.hpp>
#include <websocketpp/client.hpp>
#include <BaseExchangeConnector.h>

#include <queue>
#include <mutex>
#include <condition_variable>

#include <atomic>
#include <thread>

#include <string>
#include <nlohmann/json.hpp>
#include <CryptoExtensions.h>

namespace py = pybind11;

using websocketpp::lib::placeholders::_1;
using websocketpp::lib::placeholders::_2;
using websocketpp::lib::bind;

typedef websocketpp::client<websocketpp::config::asio_tls_client> client;
typedef websocketpp::config::asio_tls_client::message_type::ptr message_ptr;
typedef std::shared_ptr<boost::asio::ssl::context> context_ptr;

class OkxConnector : public BaseExchangeConnector {
public: 
    OkxConnector(const std::string API_key,
                   const std::string API_secret,
                   const std::string API_pass);
    ~OkxConnector();

    void connect(const std::string& uri) override;
    void connect_private(const std::string& uri,
                         const std::string& api_key,
                         const std::string& secret,
                         const std::string& pass_phrase) override;
    void disconnect() override;
    
    void subscribe(const std::string& channel, const std::string& inst_id) override;
    void subscribe_private(const std::string& channel) override;
    void unsubscribe(const std::string& channel, const std::string& inst_id) override;

    void place_order(const std::string& ord_id, const std::string& inst_id,
                    const std::string& side, const std::string& sz) override;
    void cancel_order(const std::string& msg_id, const std::string& ord_id, const std::string& inst_id) override;
    // void change_order()
    // place multiple orders - задержка выставления ордера по таймингам
    // cancel all orders
    // spot feature option 
    

private:
    client m_client;
    std::thread m_client_thread;
    std::atomic<bool> m_running{false};
    std::atomic<bool> m_connected{false};
    std::queue<std::string> m_messages;
    std::mutex m_mutex;
    std::condition_variable m_cv;
    websocketpp::connection_hdl m_hdl;
    std::vector<std::pair<std::string, std::string>> m_subscriptions;
    CryptoExtensions cryptoExtensions;
    context_ptr on_tls_init();

    std::string _API_key;
    std::string _API_secret;
    std::string _API_pass;
    
    void on_message(websocketpp::connection_hdl, message_ptr msg);
    void on_open(websocketpp::connection_hdl hdl);
    void on_close(websocketpp::connection_hdl hdl);
    void send_message(const nlohmann::json& msg);

    std::string generate_sign(const std::string& secret, 
                              const std::string& timestamp);
    void login(const std::string& api_key,
               const std::string& secret,
               const std::string& passphrase);

    friend class WebSocketIterator;  // Allow iterator to access private members

};

class WebSocketIterator {
    public:
        explicit WebSocketIterator(OkxConnector& ws);
        std::string next();
    
    private:
        OkxConnector& m_ws;
};