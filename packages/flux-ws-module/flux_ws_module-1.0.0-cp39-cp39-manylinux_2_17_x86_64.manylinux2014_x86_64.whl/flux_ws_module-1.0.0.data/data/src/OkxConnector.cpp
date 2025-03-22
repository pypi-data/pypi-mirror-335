#include "OkxConnector.h"
#include "CryptoExtensions.h"
#include <chrono>
#include <sstream>

#include <queue>
#include <future>

#include <time.h>
#include <stdio.h>
#include <iomanip>
#include <memory>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <thread>
#include <future>
#include "BaseExchangeConnector.h"

using json = nlohmann::json;

OkxConnector::OkxConnector(const std::string API_key,
                               const std::string API_secret,
                               const std::string API_pass){
    m_client.clear_access_channels(websocketpp::log::alevel::all);
    m_client.init_asio();
    
    m_client.set_open_handler(bind(&OkxConnector::on_open, this, ::_1));
    m_client.set_close_handler(bind(&OkxConnector::on_close, this, ::_1));
    m_client.set_message_handler(bind(&OkxConnector::on_message, this, ::_1, ::_2));
    m_client.set_tls_init_handler(bind(&OkxConnector::on_tls_init, this));
    m_client.set_fail_handler([this](websocketpp::connection_hdl) {
        std::cout << "Connection failed" << std::endl;
    });

    cryptoExtensions = CryptoExtensions();

    // TBD: API_key, API_secret, API_passphrase
    _API_key = API_key;
    _API_secret = API_secret;
    _API_pass = API_pass;
}

OkxConnector::~OkxConnector() {
    disconnect();
}

context_ptr OkxConnector::on_tls_init() {
    auto ctx = std::make_shared<boost::asio::ssl::context>(boost::asio::ssl::context::sslv23);
    try {
        ctx->set_options(boost::asio::ssl::context::default_workarounds |
                        boost::asio::ssl::context::no_sslv2 |
                        boost::asio::ssl::context::no_sslv3 |
                        boost::asio::ssl::context::single_dh_use);
    } catch (std::exception& e) {
        throw std::runtime_error("TLS init failed: " + std::string(e.what()));
    }
    return ctx;
}


//----------------------------------
// CONNECT AFTER ALL SUBS MADE
//----------------------------------
void OkxConnector::connect(const std::string& uri) {
    websocketpp::lib::error_code ec;
    auto con = m_client.get_connection(uri, ec);
    
    if (ec || !con) {
        throw std::runtime_error("Connection failed: " + ec.message());
    }

    m_client.connect(con);
    m_running = true;
    m_client_thread = std::thread([this]() {
        try {
            m_client.run();
        } catch (const std::exception& e) {
            if (m_running) {
                std::cerr << "WebSocket error: " << e.what() << std::endl;
            }
        }
    });
}

void OkxConnector::connect_private(const std::string& uri,
                                     const std::string& api_key,
                                     const std::string& secret,
                                     const std::string& pass_phrase) {
    websocketpp::lib::error_code ec;
    auto con = m_client.get_connection(uri, ec);
    
    if (ec || !con) {
        throw std::runtime_error("Connection failed: " + ec.message());
    }
    m_client.connect(con);
    m_running = true;
    m_client_thread = std::thread([this]() {
        try {
            m_client.run();
        } catch (const std::exception& e) {
            if (m_running) {
                std::cerr << "WebSocket error: " << e.what() << std::endl;
            }
        }
    });
}

//----------------------------------------
// DISCONNECT WITH THREAD KILL
//----------------------------------------
// TBD: add unsubscribe if disconnected gracefully?
void OkxConnector::disconnect() {
    if (m_running.exchange(false)) {
        m_client.stop();
        m_cv.notify_all();
        if (m_client_thread.joinable()) {
            m_client_thread.join();
        }
    }
}

// -----------------------------
// ON EVENT HANDLERS
// -----------------------------
void OkxConnector::on_open(websocketpp::connection_hdl hdl) {
    m_hdl = hdl;
    m_connected = true;

    // TODO:
    // login только для private подключения

    login(_API_key, _API_secret, _API_pass);
    
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_subscriptions.empty()) {
        json msg;
        msg["op"] = "subscribe";
        auto& args = msg["args"] = json::array();
        
        for (const auto& [channel, inst_id] : m_subscriptions) {
            args.push_back({{"channel", channel}, {"instId", inst_id}});
        }
        send_message(msg);
    }
}

void OkxConnector::on_close(websocketpp::connection_hdl hdl) {
    m_connected = false;
    m_cv.notify_all();
}

void OkxConnector::on_message(websocketpp::connection_hdl, message_ptr msg) {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_messages.push(msg->get_payload());
    m_cv.notify_one();
}

//---------------------------------
// LOGIN
//---------------------------------
std::string OkxConnector::generate_sign(const std::string& secret,
                                          const std::string& timestamp) {
    // Construct the signature payload
    const std::string method = "GET";
    const std::string endpoint = "/users/self/verify";
    const std::string sign_payload = timestamp + method + endpoint;

    // Calculate HMAC-SHA256 (returns binary string)
    std::string hmac_digest = cryptoExtensions.CalcHmacSHA256(secret, sign_payload);

    // Base64 encode the binary result
    return cryptoExtensions.encode64(hmac_digest);
}

void OkxConnector::login(const std::string& api_key,
                           const std::string& secret,
                           const std::string& passphrase) {
    // Generate timestamp in seconds
    const auto now = std::chrono::system_clock::now();
    const std::string timestamp = std::to_string(
        std::chrono::duration_cast<std::chrono::seconds>(
            now.time_since_epoch()).count());

    // Generate cryptographic signature
    const std::string signature = generate_sign(secret, timestamp);

    // Construct JSON message
    json msg;
    msg["op"] = "login";
    msg["args"] = json::array({
        {
            {"apiKey", api_key},
            {"passphrase", passphrase},
            {"timestamp", timestamp},
            {"sign", signature}
        }
    });

    send_message(msg);
}

// --------------------------------
// SUBSCRIBE UNSUBSCRIBE ACTIONS
// --------------------------------
void OkxConnector::subscribe(const std::string& channel, const std::string& inst_id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    if (m_connected) {
        // Send immediate subscription
        json msg;
        msg["op"] = "subscribe";
        msg["args"] = json::array({
            {{"channel", channel}, {"instId", inst_id}}
        });
        send_message(msg);
    }
    
    // Add to subscription list for reconnect scenarios
    m_subscriptions.emplace_back(channel, inst_id);
}

void OkxConnector::subscribe_private(const std::string& channel) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // Send immediate subscription
    json msg;
    msg["op"] = "subscribe";
    msg["args"] = json::array({
        {{"channel", channel}}
    });
    send_message(msg);
    
    // Add to subscription list for reconnect scenarios
    // m_subscriptions.emplace_back(channel);
}

void OkxConnector::unsubscribe(const std::string& channel, const std::string& inst_id) {
    std::lock_guard<std::mutex> lock(m_mutex);
    
    // Remove from subscriptions
    m_subscriptions.erase(
        std::remove_if(m_subscriptions.begin(), m_subscriptions.end(),
            [&](const auto& sub) {
                return sub.first == channel && sub.second == inst_id;
            }),
        m_subscriptions.end()
    );
    
    if (m_connected) {
        // Send unsubscribe request
        json msg;
        msg["op"] = "unsubscribe";
        msg["args"] = json::array({
            {{"channel", channel}, {"instId", inst_id}}
        });
        send_message(msg);
    }
}

//---------------------------
// SEND
// --------------------------
void OkxConnector::send_message(const json& msg) {
    websocketpp::lib::error_code ec;
    m_client.send(m_hdl, msg.dump(), websocketpp::frame::opcode::text, ec);
    if (ec) {
        throw std::runtime_error("Send failed: " + ec.message());
    }
}

//--------------------------
// ORDERS
//--------------------------
void OkxConnector::place_order(const std::string& ord_id, const std::string& inst_id,
                               const std::string& side, const std::string& sz) {
    json msg;
    msg["id"] = ord_id;
    msg["op"] = "order";
    msg["args"] = json::array({
        {
            {"side", side},
            {"instId", inst_id},
            {"tdMode", "cash"},
            {"ordType", "market"},
            // {"px", 1},
            {"sz", sz}
        }
    });
    send_message(msg);
}

void OkxConnector::cancel_order(const std::string& msg_id, const std::string& ord_id, const std::string& inst_id) {
    json msg;
    msg["id"] = msg_id;
    msg["op"] = "cancel-order";
    msg["args"] = json::array({
        {
            {"ordId", ord_id},
            {"instId", inst_id}
        }
    });
    send_message(msg);
}

// void OkxConnector::change_order()

// ---------------------------------------------------------------------------

// Iterator implementation
WebSocketIterator::WebSocketIterator(OkxConnector& ws) : m_ws(ws) {}

std::string WebSocketIterator::next() {
    py::gil_scoped_release release;
    std::unique_lock<std::mutex> lock(m_ws.m_mutex);
    m_ws.m_cv.wait(lock, [this] {
        return !m_ws.m_messages.empty() || !m_ws.m_running.load();
    });

    if (!m_ws.m_running.load() && m_ws.m_messages.empty()) {
        throw py::stop_iteration();
    }

    auto msg = m_ws.m_messages.front();
    m_ws.m_messages.pop();
    return msg;
}