#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "BaseExchangeConnector.h"
#include "CryptoExtensions.h"
#include "OkxConnector.h"

namespace py = pybind11;

void bind_WebSocketClass(py::module_ &m) {
    // Bind BaseExchangeConnector with a module-level docstring.
    py::class_<BaseExchangeConnector>(m, "BaseExchangeConnector",
        R"pbdoc(
            BaseExchangeConnector

            A base class that provides common WebSocket connection functionality.
        )pbdoc");

    // Bind OkxConnector as the WebSocket class derived from BaseExchangeConnector.
    py::class_<OkxConnector, BaseExchangeConnector>(m, "OkxConnector",
        R"pbdoc(
            WebSocket

            A specialized connector for OKX exchanges, inheriting from BaseExchangeConnector.
        )pbdoc")
        .def(py::init<std::string, std::string, std::string>(),
            R"pbdoc(
                Constructor for WebSocket.

                Parameters:
                    param1 (str): Description for the first parameter.
                    param2 (str): Description for the second parameter.
                    param3 (str): Description for the third parameter.
            )pbdoc")
        .def("connect", &BaseExchangeConnector::connect,
            R"pbdoc(
                Connect to the WebSocket server.

                Parameters:
                    url (str): The URL of the WebSocket server.

                Returns:
                    A status or result of the connection attempt.
            )pbdoc", py::arg("url"))
        .def("connect_private", &BaseExchangeConnector::connect_private,
            R"pbdoc(
                Establish a private WebSocket connection.
            )pbdoc")
        .def("disconnect", &BaseExchangeConnector::disconnect,
            R"pbdoc(
                Disconnect from the WebSocket server.
            )pbdoc")
        .def("subscribe", &BaseExchangeConnector::subscribe,
            R"pbdoc(
                Subscribe to a channel and instrument.

                Parameters:
                    channel (str): The channel to subscribe.
                    inst (str): The instrument identifier.
            )pbdoc")
        .def("subscribe_private", &BaseExchangeConnector::subscribe_private,
            R"pbdoc(
                Subscribe to a private channel.

                Parameters:
                    channel (str): The channel to subscribe.
                    inst (str): The instrument identifier.
            )pbdoc")
        .def("unsubscribe", &BaseExchangeConnector::unsubscribe,
            R"pbdoc(
                Unsubscribe from a channel and instrument.

                Parameters:
                    channel (str): The channel to unsubscribe.
                    inst (str): The instrument identifier.
            )pbdoc")
        .def("place_order", &BaseExchangeConnector::place_order,
            R"pbdoc(
                Place an order.

                Returns:
                    Confirmation or status of the order placement.
            )pbdoc")
        .def("cancel_order", &BaseExchangeConnector::cancel_order,
            R"pbdoc(
                Cancel an existing order.

                Returns:
                    Confirmation or status of the order cancellation.
            )pbdoc")
        // .def("change_order", &OkxConnector::change_order)
        .def("wsrun", [](OkxConnector &self) {
            return WebSocketIterator(self);
        }, py::keep_alive<0, 1>());

    py::class_<WebSocketIterator>(m, "WebSocketIterator")
        .def("__iter__", [](WebSocketIterator &it) -> WebSocketIterator& { return it; })
        .def("__next__", &WebSocketIterator::next);
}


void bind_CryptoExtensions(py::module_ &m) {
    py::class_<CryptoExtensions>(m, "CryptoExtensions")
        .def("encode64", &CryptoExtensions::encode64)
        .def("CalcHmacSHA256", &CryptoExtensions::CalcHmacSHA256);
}

PYBIND11_MODULE(_flux_ws_module, m) {
    m.doc() = R"pbdoc(
        flux_ws_module
        -------------------
        A C++ library that provides WebSocket connections to different exchanges with same interface.

        This module allows connection to WebSocket servers, subscription to channels,
        placing and cancelling orders, and includes cryptographic functions for data encoding and hashing.
    )pbdoc";

    bind_WebSocketClass(m);
    bind_CryptoExtensions(m);
}

