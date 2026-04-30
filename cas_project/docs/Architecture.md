# Architecture & System Diagrams

The Currency Analytics System (CAS) design incorporates several UML diagrams describing the software's components, control flow, and interactions.

## 1. System Architecture Description
The system follows a modular Monolithic Architecture. The core elements include:
- **CLI Interface (`main.py`)**: Handles user input and navigation.
- **Analysis Engine (`analysis.py`)**: Performs statistical rules processing offline (Mode, Median, Standard Deviation, Variation Coefficient) and histogram calculations.
- **NBP API Integration (`api.py`)**: Connects to the external NBP Web API. Handles URL parsing, date ranges, HTTP errors and returns sanitized variables.
- **File Exporter (`export.py`)**: Utility feature for dumping arrays into CSV files.

---

## 2. Component Diagram
```mermaid
graph TD;
    CLI[CLI Application] --> API_Module[NBP API Module];
    CLI --> Stats_Module[Statistical & Session Module];
    CLI --> Export_Module[CSV Export Module];
    API_Module --> NBP_API[External NBP REST API];
```

---

## 3. Sequence Diagram (Session Analysis Flow)
```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant API_Module
    participant NBP_External
    participant Stats_Module

    User->>CLI: Selects Session Analysis
    CLI->>User: Prompts for Currency & Period
    User->>CLI: Enters 'USD' & '1 Month'
    CLI->>API_Module: Request rates for USD (23 sessions)
    API_Module->>NBP_External: GET /api/exchangerates/rates/A/USD/last/23
    NBP_External-->>API_Module: Returns JSON Array
    API_Module-->>CLI: Returns Python List of rates
    CLI->>Stats_Module: Execute session_analysis(rates)
    Stats_Module-->>CLI: Return Rises, Falls, Unchanged
    CLI->>User: Print analysis results
```

---

## 4. Activity Diagram
```mermaid
stateDiagram-v2
    [*] --> StartCLI
    StartCLI --> DisplayMenu
    DisplayMenu --> SelectAction
    
    SelectAction --> EnterCurrencyAndPeriod: Option 1 or 2
    EnterCurrencyAndPeriod --> FetchData
    
    SelectAction --> EnterPairAndPeriod: Option 3
    EnterPairAndPeriod --> FetchCrossData
    FetchCrossData --> FetchData
    
    FetchData --> ValidateResponse
    ValidateResponse --> CalculateStats: Valid Data
    ValidateResponse --> DisplayError: Invalid/No Data
    DisplayError --> DisplayMenu
    
    CalculateStats --> RenderOutput
    RenderOutput --> PromptExport
    PromptExport --> ExportToCSV: User selects 'Y'
    PromptExport --> DisplayMenu: User selects 'N'
    ExportToCSV --> DisplayMenu
    
    SelectAction --> Exit: Option 4
    Exit --> [*]
```
