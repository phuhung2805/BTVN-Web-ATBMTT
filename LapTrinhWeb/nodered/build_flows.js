// Tạo lại LapTrinhWeb/nodered_flows.json từ api_tacke.js
// Chạy: node LapTrinhWeb/nodered/build_flows.js
const fs = require("fs");
const path = require("path");

const func = fs.readFileSync(path.join(__dirname, "api_tacke.js"), "utf8");
const tab = "tab_btvn_web_api";

const flows = [
    {
        id: tab, type: "tab", label: "BTVN API Service", disabled: false,
        info: "API /api/tacke: http in -> function (thuật toán chia tiền) -> http response.\nNginx proxy /api/ tới container nodered:1880."
    },
    {
        id: "node_http_in_tacke_get", type: "http in", z: tab, name: "GET /api/tacke",
        url: "/api/tacke", method: "get", upload: false, swaggerDoc: "",
        x: 150, y: 140, wires: [["node_func_tacke"]]
    },
    {
        id: "node_http_in_tacke_post", type: "http in", z: tab, name: "POST /api/tacke",
        url: "/api/tacke", method: "post", upload: false, swaggerDoc: "",
        x: 150, y: 200, wires: [["node_func_tacke"]]
    },
    {
        id: "node_func_tacke", type: "function", z: tab, name: "Thuật toán /api/tacke",
        func: func, outputs: 1, timeout: 0, noerr: 0, initialize: "", finalize: "", libs: [],
        x: 400, y: 170, wires: [["node_http_response_tacke"]]
    },
    {
        id: "node_http_response_tacke", type: "http response", z: tab, name: "HTTP Response",
        statusCode: "", headers: {}, x: 640, y: 170, wires: []
    }
];

const out = path.join(__dirname, "..", "nodered_flows.json");
fs.writeFileSync(out, JSON.stringify(flows, null, 4) + "\n");
console.log("Đã ghi", out);
