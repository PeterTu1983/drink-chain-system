import os
import psycopg2
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

BRANCHES = {
    "ty-1": {"name": "桃園一店", "host": "db-ty-1", "db": "branch_ty_1", "port": 5431},
    "ty-2": {"name": "桃園二店", "host": "db-ty-2", "db": "branch_ty_2", "port": 5432},
    "ty-3": {"name": "桃園三店", "host": "db-ty-3", "db": "branch_ty_3", "port": 5433},
    "tpe-1": {"name": "台北一店", "host": "db-tpe-1", "db": "branch_tpe_1", "port": 5434},
    "txg-1": {"name": "台中一店", "host": "db-txg-1", "db": "branch_txg_1", "port": 5435},
    "tnn-1": {"name": "台南一店", "host": "db-tnn-1", "db": "branch_tnn_1", "port": 5436},
}

DB_USER = os.getenv("DB_USER", "chain_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "chain_secret")

def get_conn(branch_code):
    b = BRANCHES[branch_code]
    return psycopg2.connect(
        host=b["host"],
        port=5432,
        dbname=b["db"],
        user=DB_USER,
        password=DB_PASSWORD,
    )

HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>連鎖飲料店分散式菜單與營收系統</title>
  <style>
    body { font-family: Arial, "Microsoft JhengHei", sans-serif; margin: 24px; background: #f6f7f9; color: #222; }
    .container { max-width: 1080px; margin: auto; }
    .card { background: #fff; border-radius: 10px; padding: 18px; margin-bottom: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
    h1, h2, h3 { margin-top: 0; }
    .row { display: flex; gap: 16px; flex-wrap: wrap; }
    .col { flex: 1; min-width: 300px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; }
    button { padding: 6px 12px; border: none; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    input, select { padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #e0e7ff; color: #1e40af; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>連鎖飲料店分散式菜單與經營管理系統</h1>
      <label>目前分店節點：</label>
      <select id="branchSelect" onchange="loadAll()">
        <option value="ty-1">桃園一店 (ty-1)</option>
        <option value="ty-2">桃園二店 (ty-2)</option>
        <option value="ty-3">桃園三店 (ty-3)</option>
        <option value="tpe-1">台北一店 (tpe-1)</option>
        <option value="txg-1">台中一店 (txg-1)</option>
        <option value="tnn-1">台南一店 (tnn-1)</option>
      </select>
      <span class="badge" id="currentBranchLabel"></span>
    </div>

    <div class="row">
      <div class="col card">
        <h2>分店菜單與點餐</h2>
        <h3>固定連鎖飲品</h3>
        <table>
          <thead><tr><th>品項</th><th>價格</th><th>操作</th></tr></thead>
          <tbody id="baseMenuBody"></tbody>
        </table>

        <h3 style="margin-top:16px;">本店特色飲品</h3>
        <table>
          <thead><tr><th>品項</th><th>價格</th><th>操作</th></tr></thead>
          <tbody id="specialMenuBody"></tbody>
        </table>

        <h3 style="margin-top:16px;">新增本店特色飲品</h3>
        <input id="newDrinkName" placeholder="特色飲品名稱" />
        <input id="newDrinkPrice" type="number" placeholder="價格 (元)" style="width:100px;" />
        <button onclick="addSpecialDrink()">新增特色飲品</button>
      </div>

      <div class="col card">
        <h2>分店店長：本店經營資訊</h2>
        <div id="branchStats"></div>
        <h3>近期訂單</h3>
        <table>
          <thead><tr><th>品項</th><th>金額</th><th>時間</th></tr></thead>
          <tbody id="ordersBody"></tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h2>老闆視角：全連鎖各分店營收彙整</h2>
      <button onclick="loadOwnerReport()">重新整理全分店營收</button>
      <table>
        <thead>
          <tr>
            <th>分店</th>
            <th>節點代號</th>
            <th>訂單數</th>
            <th>總營收 (元)</th>
            <th>特色飲品數</th>
          </tr>
        </thead>
        <tbody id="ownerBody"></tbody>
      </table>
    </div>
  </div>

  <script>
    function getBranch() {
      return document.getElementById("branchSelect").value;
    }

    async function loadBranchData() {
      const b = getBranch();
      const res = await fetch(`/api/branch/${b}`);
      const data = await res.json();
      document.getElementById("currentBranchLabel").textContent = `${data.branch_name} 獨立資料庫已連線`;

      const baseBody = document.getElementById("baseMenuBody");
      baseBody.innerHTML = data.base_menu.map(item => `
        <tr>
          <td>${item.name}</td>
          <td>${item.price} 元</td>
          <td><button onclick="createOrder('${item.name}', ${item.price})">點餐</button></td>
        </tr>
      `).join("");

      const spBody = document.getElementById("specialMenuBody");
      spBody.innerHTML = data.special_drinks.length ? data.special_drinks.map(item => `
        <tr>
          <td>${item.name}</td>
          <td>${item.price} 元</td>
          <td><button onclick="createOrder('${item.name}', ${item.price})">點餐</button></td>
        </tr>
      `).join("") : `<tr><td colspan="3">尚未新增特色飲品</td></tr>`;

      document.getElementById("branchStats").innerHTML = `
        <p><strong>累計訂單數：</strong>${data.stats.order_count} 筆 ｜ <strong>本店總營收：</strong>${data.stats.total_revenue} 元</p>
      `;

      const ordersBody = document.getElementById("ordersBody");
      ordersBody.innerHTML = data.recent_orders.map(o => `
        <tr>
          <td>${o.item_name}</td>
          <td>${o.amount} 元</td>
          <td>${o.created_at}</td>
        </tr>
      `).join("");
    }

    async function addSpecialDrink() {
      const b = getBranch();
      const name = document.getElementById("newDrinkName").value.trim();
      const price = parseInt(document.getElementById("newDrinkPrice").value, 10);
      if (!name || !price || price <= 0) {
        alert("請輸入正確的飲品名稱與價格");
        return;
      }
      await fetch(`/api/branch/${b}/special-drinks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, price })
      });
      document.getElementById("newDrinkName").value = "";
      document.getElementById("newDrinkPrice").value = "";
      loadAll();
    }

    async function createOrder(itemName, amount) {
      const b = getBranch();
      await fetch(`/api/branch/${b}/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_name: itemName, amount })
      });
      loadAll();
    }

    async function loadOwnerReport() {
      const res = await fetch("/api/owner/summary");
      const rows = await res.json();
      document.getElementById("ownerBody").innerHTML = rows.map(r => `
        <tr>
          <td>${r.branch_name}</td>
          <td>${r.branch_code}</td>
          <td>${r.order_count}</td>
          <td>${r.total_revenue} 元</td>
          <td>${r.special_count}</td>
        </tr>
      `).join("");
    }

    function loadAll() {
      loadBranchData();
      loadOwnerReport();
    }

    loadAll();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/branch/<branch_code>")
def branch_detail(branch_code):
    if branch_code not in BRANCHES:
        return jsonify({"error": "Invalid branch"}), 404
    conn = get_conn(branch_code)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM base_menu ORDER BY id;")
    base_menu = [{"id": r[0], "name": r[1], "price": r[2]} for r in cur.fetchall()]

    cur.execute("SELECT id, name, price FROM branch_special_drinks WHERE branch_code=%s ORDER BY id DESC;", (branch_code,))
    special_drinks = [{"id": r[0], "name": r[1], "price": r[2]} for r in cur.fetchall()]

    cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM orders WHERE branch_code=%s;", (branch_code,))
    cnt, total = cur.fetchone()

    cur.execute("SELECT item_name, amount, to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') FROM orders WHERE branch_code=%s ORDER BY id DESC LIMIT 10;", (branch_code,))
    recent_orders = [{"item_name": r[0], "amount": r[1], "created_at": r[2]} for r in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify({
        "branch_code": branch_code,
        "branch_name": BRANCHES[branch_code]["name"],
        "base_menu": base_menu,
        "special_drinks": special_drinks,
        "stats": {"order_count": cnt, "total_revenue": total},
        "recent_orders": recent_orders,
    })

@app.route("/api/branch/<branch_code>/special-drinks", methods=["POST"])
def add_special_drink(branch_code):
    if branch_code not in BRANCHES:
        return jsonify({"error": "Invalid branch"}), 404
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    price = int(data.get("price") or 0)
    if not name or price <= 0:
        return jsonify({"error": "Invalid input"}), 400
    conn = get_conn(branch_code)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO branch_special_drinks (branch_code, name, price) VALUES (%s, %s, %s);",
        (branch_code, name, price),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 201

@app.route("/api/branch/<branch_code>/orders", methods=["POST"])
def create_order(branch_code):
    if branch_code not in BRANCHES:
        return jsonify({"error": "Invalid branch"}), 404
    data = request.get_json(force=True)
    item_name = (data.get("item_name") or "").strip()
    amount = int(data.get("amount") or 0)
    if not item_name or amount <= 0:
        return jsonify({"error": "Invalid input"}), 400
    conn = get_conn(branch_code)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (branch_code, item_name, amount) VALUES (%s, %s, %s);",
        (branch_code, item_name, amount),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 201

@app.route("/api/owner/summary")
def owner_summary():
    result = []
    for code, info in BRANCHES.items():
        conn = get_conn(code)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM orders WHERE branch_code=%s;", (code,))
        cnt, total = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM branch_special_drinks WHERE branch_code=%s;", (code,))
        sp_cnt = cur.fetchone()[0]
        cur.close()
        conn.close()
        result.append({
            "branch_code": code,
            "branch_name": info["name"],
            "order_count": cnt,
            "total_revenue": total,
            "special_count": sp_cnt,
        })
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
