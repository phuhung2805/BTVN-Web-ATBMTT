// =============================================================================
// Mã nguồn của function node "Thuật toán /api/tacke" trong Node-RED.
// File này chỉ để đọc và test. Mã thật nằm trong LapTrinhWeb/nodered_flows.json
// (tạo lại bằng: node LapTrinhWeb/nodered/build_flows.js).
//
// BÀI TOÁN "TÁCH KÈ" (chia tiền quỹ lớp):
//   Mỗi sinh viên đã chi một số tiền (money) cho hoạt động chung.
//   API tính xem mỗi người phải đóng thêm / được nhận lại bao nhiêu để ai cũng
//   chi bằng nhau, rồi tìm danh sách chuyển khoản ÍT GIAO DỊCH nhất (thuật toán
//   tham lam: người nợ nhiều nhất trả cho người được nhận nhiều nhất).
//
// Đầu vào:
//   GET  /api/tacke?sort=desc|asc|name&q=<tên>&min=<số>&max=<số>&top=<n>
//   POST /api/tacke   body: {"dssv":[{"name":"An","money":100}, ...]}
//                      (các tham số lọc vẫn đọc từ query string)
// Đầu ra (giữ đúng khung đề bài, thêm trường mở rộng):
//   {"ok":1,"msg":"thành công","dssv":[{"name":"Cốp","money":123,...}],
//    "thongke":{...},"chuyenkhoan":[{"tu":"A","den":"B","sotien":10}]}
// =============================================================================

const DSSV_MAU = [
    { name: "Cốp", money: 123 },
    { name: "David", money: 456 },
    { name: "Nguyễn Văn An", money: 300 },
    { name: "Trần Thị Bình", money: 0 },
    { name: "Lê Minh Châu", money: 250 },
    { name: "Phạm Quốc Dũng", money: 89 },
    { name: "Hoàng Thu Hà", money: 512 },
    { name: "Vũ Đức Khang", money: 170 }
];

function traLoi(statusCode, body) {
    msg.statusCode = statusCode;
    msg.headers = { "Content-Type": "application/json; charset=utf-8" };
    msg.payload = body;
    return msg;
}

function loi(text) {
    return traLoi(400, { ok: 0, msg: text, dssv: [] });
}

// Bỏ dấu tiếng Việt để tìm kiếm "an" khớp cả "An", "Ân"...
function boDau(s) {
    return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "")
        .replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase().trim();
}

function lam2(x) {
    return Math.round(x * 100) / 100;
}

// Đọc một tham số số (không bắt buộc). Trả về null nếu không có, NaN nếu sai.
function docSo(v) {
    if (v === undefined || v === null || v === "") return null;
    const n = Number(v);
    return Number.isFinite(n) ? n : NaN;
}

const query = (msg.req && msg.req.query) || {};
const method = (msg.req && msg.req.method) || "GET";

// ---- 1. Lấy và kiểm tra dữ liệu đầu vào ------------------------------------
let ds = DSSV_MAU;
if (method === "POST") {
    let body = msg.payload;
    if (typeof body === "string") {
        try { body = JSON.parse(body); } catch (e) { return loi("Body không phải JSON hợp lệ"); }
    }
    if (!body || !Array.isArray(body.dssv)) return loi('Body phải có dạng {"dssv":[{"name":..,"money":..}]}');
    ds = body.dssv;
}
if (ds.length > 1000) return loi("Tối đa 1000 sinh viên");

const sach = [];
for (let i = 0; i < ds.length; i++) {
    const sv = ds[i] || {};
    const name = typeof sv.name === "string" ? sv.name.trim() : "";
    const money = Number(sv.money);
    if (!name) return loi(`Sinh viên thứ ${i + 1} thiếu tên`);
    if (!Number.isFinite(money) || money < 0) return loi(`Số tiền của "${name}" phải là số >= 0`);
    sach.push({ name: name, money: lam2(money) });
}

// ---- 2. Đọc tham số lọc / sắp xếp ------------------------------------------
const sort = String(query.sort || "desc").toLowerCase();
if (!["desc", "asc", "name"].includes(sort)) return loi("sort chỉ nhận desc, asc hoặc name");
const min = docSo(query.min);
const max = docSo(query.max);
const top = docSo(query.top);
if (Number.isNaN(min) || Number.isNaN(max)) return loi("min/max phải là số");
if (min !== null && max !== null && min > max) return loi("min không được lớn hơn max");
if (Number.isNaN(top) || (top !== null && (!Number.isInteger(top) || top < 1))) return loi("top phải là số nguyên >= 1");
const tuKhoa = boDau(query.q || "");

// ---- 3. Thuật toán chia đều + chuyển khoản tối thiểu (trên TOÀN BỘ danh sách)
// Làm việc bằng số nguyên để không sai số: tiền đổi sang xu (x100), rồi nhân
// với n để trung bình cũng là số nguyên  =>  chenh_i = xu_i * n - tongXu.
const n = sach.length;
const tongXu = sach.reduce((s, sv) => s + Math.round(sv.money * 100), 0);
const tong = tongXu / 100;
const trungBinh = n ? tong / n : 0;

const chenh = sach.map(sv => ({ name: sv.name, v: Math.round(sv.money * 100) * n - tongXu }));
const no = chenh.filter(x => x.v < 0).map(x => ({ name: x.name, v: -x.v })).sort((a, b) => b.v - a.v);
const co = chenh.filter(x => x.v > 0).sort((a, b) => b.v - a.v);

const chuyenKhoan = [];
let i = 0, j = 0;
while (i < no.length && j < co.length) {
    const t = Math.min(no[i].v, co[j].v);
    chuyenKhoan.push({ tu: no[i].name, den: co[j].name, sotien: lam2(t / n / 100) });
    no[i].v -= t;
    co[j].v -= t;
    if (no[i].v === 0) i++;
    if (co[j].v === 0) j++;
}

// ---- 4. Xếp hạng (đồng tiền thì đồng hạng: 1, 2, 2, 4) ----------------------
const theoTien = sach.slice().sort((a, b) => b.money - a.money);
const hang = new Map();
theoTien.forEach((sv, k) => {
    const truoc = theoTien[k - 1];
    hang.set(sv, truoc && truoc.money === sv.money ? hang.get(truoc) : k + 1);
});

// ---- 5. Lọc, sắp xếp, cắt top cho danh sách trả về --------------------------
let ketQua = sach.filter(sv =>
    (!tuKhoa || boDau(sv.name).includes(tuKhoa)) &&
    (min === null || sv.money >= min) &&
    (max === null || sv.money <= max)
);
if (sort === "desc") ketQua.sort((a, b) => b.money - a.money || a.name.localeCompare(b.name, "vi"));
if (sort === "asc") ketQua.sort((a, b) => a.money - b.money || a.name.localeCompare(b.name, "vi"));
if (sort === "name") ketQua.sort((a, b) => a.name.localeCompare(b.name, "vi"));
if (top !== null) ketQua = ketQua.slice(0, top);

const dssv = ketQua.map(sv => ({
    name: sv.name,
    money: sv.money,
    hang: hang.get(sv),
    chenhlech: lam2(sv.money - trungBinh)   // > 0: được nhận lại, < 0: phải đóng thêm
}));

// Trung vị
const tienTang = sach.map(sv => sv.money).sort((a, b) => a - b);
const trungVi = n === 0 ? 0 : n % 2 ? tienTang[(n - 1) / 2] : lam2((tienTang[n / 2 - 1] + tienTang[n / 2]) / 2);

return traLoi(200, {
    ok: 1,
    msg: "thành công",
    dssv: dssv,
    thongke: {
        soluong: n,
        sotrave: dssv.length,
        tong: lam2(tong),
        trungbinh: lam2(trungBinh),
        trungvi: trungVi,
        caonhat: n ? tienTang[n - 1] : 0,
        thapnhat: n ? tienTang[0] : 0
    },
    chuyenkhoan: chuyenKhoan
});
