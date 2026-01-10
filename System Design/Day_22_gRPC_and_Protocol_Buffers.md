# Day 22: gRPC & Protocol Buffers

## 🎯 Goal
Understand high-performance inter-service communication.
**Focus**: Binary Protocols, IDL (Interface Definition Language), and HTTP/2.

---

## 📡 What is gRPC?
**gRPC** (Google Remote Procedure Call) is a framework to call methods on remote servers as if they were local functions.
*   **Transport**: HTTP/2 (Multiplexing, Streaming).
*   **Format**: Protocol Buffers (Binary, Small, Typed).
*   **Use Case**: Microservices internal communication (East-West traffic).

---

## 📦 Protocol Buffers (Protobuf)
XML and JSON are text-based and bulky. Protobuf is binary.

### `.proto` File
You define the schema first (IDL).
```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
}

message UserRequest {
  int32 id = 1; // Field tags (1, 2) are crucial for serialization
}

message UserResponse {
  string name = 1;
  string email = 2;
  repeated string roles = 3; // Array
}
```

### Advantages over JSON
1.  **Smaller Payload**: Field names (`name`, `email`) are not sent. Only field tags (`1`, `2`) and values.
2.  **Faster Serialization**: Binary parsing is CPU efficient.
3.  **Strict Typing**: No "string or number" ambiguity.
4.  **Code Generation**: Generates Client/Server code in Java, Go, Python, etc.

---

## 🚀 HTTP/2 Features
gRPC leverages HTTP/2.
1.  **Multiplexing**: Multiple requests over a single TCP connection. (No Head-of-Line Blocking).
2.  **Binary Framing**: Headers are compressed (HPACK).
3.  **Server Push**: Server can send data before client asks (not used much in gRPC, but available).
4.  **Streaming**: Bidirectional streaming.

---

## 🔄 Types of gRPC APIs

1.  **Unary**: Standard Req -> Res. `rpc GetUser(Req) returns (Res)`
2.  **Server Streaming**: Req -> Stream of Res. `rpc ListTweets(Req) returns (stream Tweet)`
    *   *Use Case*: Stock Ticker, Log tailing.
3.  **Client Streaming**: Stream of Req -> Res. `rpc UploadPhotos(stream Photo) returns (Status)`
    *   *Use Case*: File Upload.
4.  **Bidirectional Streaming**: Stream Req <-> Stream Res. `rpc Chat(stream Msg) returns (stream Msg)`
    *   *Use Case*: Real-time Chat, Gaming.

---

## ⚖️ gRPC vs REST

| Feature | REST | gRPC |
| :--- | :--- | :--- |
| **Protocol** | HTTP/1.1 (Text) | HTTP/2 (Binary) |
| **Payload** | JSON (Human readable) | Protobuf (Compact) |
| **Browser Support** | Native (Fetch/XHR) | Poor (Requires gRPC-Web proxy) |
| **Streaming** | No (WebSockets needed) | Native |
| **Best For** | Public APIs (External) | Microservices (Internal) |

---

## 🛠️ Practical Task
**Task**: Define a `.proto` file for a **Ride Sharing Service**.
1.  **Service**: `RideService`
2.  **Methods**:
    *   `RequestRide(RideRequest)` -> `RideResponse` (Unary)
    *   `TrackRide(RideID)` -> `stream Location` (Server Streaming - Updates every 5s)
    *   `Chat(stream Message)` -> `stream Message` (Bi-di - Driver/Rider chat)

**Question**: How does Protobuf handle Backward Compatibility?
*   *Answer*: If you add a new field `int32 age = 3`, old clients just ignore tag `3`. If you delete a field, do **not** reuse its tag number (reserve it), or old clients will read new data as the old field.
