// Test thuật toán /api/tacke mà không cần Docker: node LapTrinhWeb/nodered/test_api.js
// Chạy đúng đoạn mã nằm trong function node của nodered_flows.json.
const assert = require("assert");
const flows = require("../nodered_flows.json");
const code = flows.find(n => n.type === "function").func;
const run = new Function("msg", code);

function goi(method, query, payload) {
    return run({ req: { method, query: query || {} }, payload });
}

// 1. Mặc định: đúng khung đề bài, sắp giảm dần theo tiền
let r = goi("GET");
assert.strictEqual(r.statusCode, 200);
assert.strictEqual(r.payload.ok, 1);
assert.strictEqual(r.payload.msg, "thành công");
assert.ok(r.payload.dssv.every(sv => typeof sv.name === "string" && typeof sv.money === "number"));
const tien = r.payload.dssv.map(sv => sv.money);
assert.deepStrictEqual(tien, tien.slice().sort((a, b) => b - a));

// 2. Sau khi chuyển khoản, mọi người chi bằng nhau
function kiemTraChiaDeu(dssvVao, ck) {
    const so = {};
    dssvVao.forEach(sv => { so[sv.name] = sv.money; });
    ck.forEach(c => { so[c.tu] += c.sotien; so[c.den] -= c.sotien; });
    const tb = dssvVao.reduce((s, sv) => s + sv.money, 0) / dssvVao.length;
    Object.values(so).forEach(v => assert.ok(Math.abs(v - tb) < 0.05, `lệch ${v} vs ${tb}`));
    assert.ok(ck.length <= dssvVao.length - 1, "số giao dịch phải <= n-1");
}
const vao = [{ name: "A", money: 100 }, { name: "B", money: 0 }, { name: "C", money: 50 }, { name: "D", money: 10 }];
r = goi("POST", {}, { dssv: vao });
assert.strictEqual(r.payload.ok, 1);
assert.strictEqual(r.payload.thongke.trungbinh, 40);
kiemTraChiaDeu(vao, r.payload.chuyenkhoan);

// Trung bình lẻ (100/3)
const le = [{ name: "X", money: 100 }, { name: "Y", money: 0 }, { name: "Z", money: 0 }];
r = goi("POST", {}, JSON.stringify({ dssv: le }));
kiemTraChiaDeu(le, r.payload.chuyenkhoan);

// 3. Lọc theo tên không dấu, min/max, top, sort
r = goi("GET", { q: "nguyen" });
assert.deepStrictEqual(r.payload.dssv.map(s => s.name), ["Nguyễn Văn An"]);
r = goi("GET", { min: "100", max: "300", sort: "asc" });
assert.ok(r.payload.dssv.every(s => s.money >= 100 && s.money <= 300));
r = goi("GET", { top: "3" });
assert.strictEqual(r.payload.dssv.length, 3);
assert.strictEqual(r.payload.dssv[0].hang, 1);

// 4. Đồng hạng
r = goi("POST", {}, { dssv: [{ name: "A", money: 5 }, { name: "B", money: 5 }, { name: "C", money: 1 }] });
assert.deepStrictEqual(r.payload.dssv.map(s => s.hang), [1, 1, 3]);

// 5. Lỗi đầu vào -> 400, ok:0
for (const [m, q, p] of [
    ["GET", { sort: "xyz" }],
    ["GET", { min: "abc" }],
    ["GET", { min: "10", max: "1" }],
    ["GET", { top: "0" }],
    ["POST", {}, { dssv: [{ name: "", money: 1 }] }],
    ["POST", {}, { dssv: [{ name: "A", money: -1 }] }],
    ["POST", {}, "khong phai json"],
    ["POST", {}, {}]
]) {
    r = goi(m, q, p);
    assert.strictEqual(r.statusCode, 400, JSON.stringify(q) + JSON.stringify(p));
    assert.strictEqual(r.payload.ok, 0);
}

console.log("Tất cả test đều qua. Ví dụ phản hồi mặc định:");
console.log(JSON.stringify(goi("GET").payload, null, 2));
