
# Phantom Mask API 

- 所有 API 回傳皆為 JSON 格式。  
- API 伺服器預設位址：`http://127.0.0.1:8000/`

---

## 1.List all pharmacies open at a specific time and on a day of the week if requested.
```
GET /pharmacies/open 
```
- **說明**：依據星期與時間，列出有營業的藥局
- **參數**：
    - `day`: (Optional) 星期幾 (Mon, Tue, Wed, Thur, Fri, Sat, Sun)
    - `time`: (Optional) 24小時制時間 (10:00)
- **回傳**：
    - id: 藥局代號
    - name: 藥局名稱
    - day_of_week: 星期幾
    - open_time: 開門時間
    - close_time: 關門時間
- **範例**：
    ```
    GET /pharmacies/open?day=Mon&time=10:00
    ```
- **回傳範例**：
    ```json
    [
      {
        "id": 1,
        "name": "DFW Wellness",
        "day_of_week": "Mon",
        "open_time": "08:00:00",
        "close_time": "12:00:00"
      }
    ]
    ```

---
## 2.List all masks sold by a given pharmacy, sorted by mask name or price.
```
GET /pharmacies/{pharmacy_name}/masks 
```
- **說明**：查詢指定藥局的所有口罩，可依名稱或價格排序，並指定升/降冪
- **參數**：
    - pharmacy_name: (required) 藥局名稱
    - sort: (Optional) name 或 price，預設 name
    - order: (Optional) asc 或 desc，預設 asc
- **回傳**：
    - name: 口罩名稱
    - price: 口罩價錢
- **範例**：
    ```
    GET /pharmacies/Carepoint/masks?sort_by=name&order=asc
    ```
- **回傳範例**：
    ```json
    [
        {
            "name": "Masquerade (blue) (6 per pack)",
            "price": 7.05
        }
    ]
    ```
---

## 3.List all pharmacies with more or fewer than x mask products within a specific price range.
```
GET /pharmacies/mask_count
```
- **說明**：列出在特定價格範圍內，販售的口罩數量多於或少於 X 種的藥局
- **參數**：
    - min_price: (required) 最小價格
    - max_price: (required) 最大價格
    - count: (required) 比較的口罩種類數量 X
    - op: (required) 運算子，'gt' , 'lt'
    - op_map = {
        'gt': '>',
        'lt': '<'
      }
- **回傳**：
    - id: 藥局代號
    - name: 藥局名稱
    - mask_count: 口罩種類數量
    - mask.name: 口罩名稱
    - mask.price: 口罩價錢
- **範例**：
    GET /pharmacies//mask_count?min_price=5&max_price=7&count=2&op=gt
- **回傳範例**：
    ```json
    [
        {
            "id": 9,
            "name": "Centrico",
            "mask_count": 3,
            "masks": [
            {
                "name": "Cotton Kiss (green) (3 per pack)",
                "price": 6.46
            },
            {
                "name": "True Barrier (green) (3 per pack)",
                "price": 6.5
            },
            {
                "name": "Masquerade (black) (6 per pack)",
                "price": 6.27
            }
            ]
        }
        ]
    ```

---
##　4.Retrieve the top x users by total transaction amount of masks within a date range.
```
GET /users/top_users 
```
- **說明**：查詢特定日期範圍內，總口罩交易金額最高的前 x 位用戶，如果沒有指定日期就會計算全部的資料
- **參數**：
    - start_date: (Optional) 起始日期，格式 YYYY-MM-DD
    - end_date: (Optional) 結束日期，格式 YYYY-MM-DD
    - top: (Optional) 前幾名，預設5，最小為0
- **回傳**：
    - id: 用戶代號
    - name: 用戶名稱
    - cash_balance: 用戶餘額
    - total_amount: 總花費
- **範例**：
    GET /users/top_users?top=2&start_date=2021-01-01&end_date=2021-01-20
- **回傳範例**：
    ```json
    [
        {
            "id": 8,
            "name": "Timothy Schultz",
            "cash_balance": 221.03,
            "total_amount": 165.19
        },
        {
            "id": 17,
            "name": "Wilbert Love",
            "cash_balance": 796.2,
            "total_amount": 128.37
        }
        ]
    ```


---
## 5.Calculate the total number of masks and the total transaction value within a date range.
```
GET /transactions/summary 
```
- **說明**：計算在特定日期範圍內，總共販售的口罩數量與交易金額總額，如果沒有指定日期就會計算全部的資料
- **參數**：
    - start_date: (Optional) 起始日期，格式 YYYY-MM-DD
    - end_date: (Optional) 結束日期，格式 YYYY-MM-DD
- **回傳**：
    - total_transaction: 總數量
    - total_amount: 總金額
- **範例**：
    GET /purchase/summary?start_date=2021-01-01&end_date=2021-01-31
- **回傳範例**：
    ```json
    {
        "total_transactions": 100,
        "total_amount": 1849.52
    }
    ```
---
## 6.Search for pharmacies or masks by name and rank the results by relevance to the search term.
```
GET /search 
```
- **說明**：依名稱搜尋藥局或口罩，並依與關鍵字相關性排序結果
- **參數**：
    - keyword: (required) 關鍵字
- **回傳**：
    - type: 藥局或口罩
    - name: 藥局或口罩的名字
    - relevance: 相關性
- **範例**：
    GET /search?keyword=c
- **回傳範例**：
    ```json
    [
        {
            "type": "pharmacy",
            "name": "Centrico",
            "relevance": 0.125
        }, ...,
        {
            "type": "mask",
            "name": "MaskT (blue) (6 per pack)",
            "relevance": 0.04
        }
    ]
    ```
---

## 7.Handle the process of a user purchasing masks, possibly from different pharmacies.
```
POST /purchase
```
- **說明**：處理用戶購買口罩的過程，可同時從多個藥局購買
- **輸入**：
    - user_id: 用戶ID
    - items: 陣列，每個元素 { pharmacy_id, mask_id, quantity }
- **回傳**：
    - success: 是否成功
    - total_cost: 本次交易總金額
    - purchases: 每一項商品購買明細
- **範例輸入**：
    ```json
    {
        "user_id": 1,
        "purchases": [
            {
            "pharmacy_id": 1,
            "mask_id": 2,
            "quantity": 1
            },
            {
            "pharmacy_id": 2,
            "mask_id": 6,
            "quantity": 1
            }
        ]
    }
    ```
- **或是在cmd輸入下列字元**:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/purchase' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1,
  "purchases": [
    {
    "pharmacy_id": 1,
    "mask_id": 2,
    "quantity": 1
    },
    {
    "pharmacy_id": 2,
    "mask_id": 6,
    "quantity": 1
    }
  ]
}'
```
- **回傳範例**：
    ```json
    {
        "message": "Purchase successful",
        "total_cost": 48.91,
        "remaining_balance": 142.92,
        "details": [
            {
            "pharmacy_id": 1,
            "pharmacy_name": "DFW Wellness",
            "mask_id": 2,
            "mask_name": "MaskT (green) (10 per pack)",
            "quantity": 1,
            "unit_price": 41.86,
            "total_price": 41.86
            },
            {
            "pharmacy_id": 2,
            "pharmacy_name": "Carepoint",
            "mask_id": 6,
            "mask_name": "Masquerade (blue) (6 per pack)",
            "quantity": 1,
            "unit_price": 7.05,
            "total_price": 7.05
            }
        ]
    }
    ```
- **若失敗**：
- 無符合用戶
```json 
{"detail": "User not found"}
```
- 無符合口罩
```json 
{"detail": "Mask 1 not found in pharmacy 2"}
```
- 餘額不足
```json 
{"detail": "Insufficient balance"}
```
