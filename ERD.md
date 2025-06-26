## ERD ##
```mermaid
erDiagram
    USER ||--o{ PURCHASEHISTORY : makes
    PHARMACY ||--|{ MASK : has
    PHARMACY ||--|{ OPENINGHOUR : has
    PHARMACY ||--o{ PURCHASEHISTORY : fulfills

    USER {
        uint ID PK
        string Name
        float CashBalance
    }

    PHARMACY {
        uint ID PK
        string Name
        float CashBalance
    }

    MASK {
        uint ID PK
        string Name
        float Price
        uint PharmacyID FK
    }

    PURCHASEHISTORY {
        uint ID PK
        uint UserID FK
        uint PharmacyID FK
        string MaskName
        float TransactionAmount
        datetime TransactionDate
    }

    OPENINGHOUR {
        uint ID PK
        uint PharmacyID FK
        string DayOfWeek
        time OpenTime
        time CloseTime
    }
```