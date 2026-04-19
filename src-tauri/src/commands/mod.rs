use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
pub struct MarketQuote {
    pub symbol: String,
    pub name: String,
    pub price: String,
    pub change: String,
    pub change_percent: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MarketData {
    pub quotes: Vec<MarketQuote>,
    pub forex_rates: std::collections::HashMap<String, f64>,
    pub fear_greed_index: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SentimentData {
    pub fear_greed_index: i32,
    pub phase: String,
    pub limit_up_count: i32,
    pub limit_down_count: i32,
    pub volume: String,
    pub northbound_flow: String,
    pub margin_balance: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MacroData {
    pub gdp: f64,
    pub cpi: f64,
    pub pmi: f64,
    pub lpr: f64,
}

fn get_data_dir() -> PathBuf {
    dirs::data_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("hermes")
        .join("daily-report")
}

#[tauri::command]
pub fn load_market_data() -> Result<MarketData, String> {
    let data_path = get_data_dir().join("market_data.json");

    if data_path.exists() {
        let content = fs::read_to_string(&data_path)
            .map_err(|e| format!("Failed to read market data: {}", e))?;
        serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse market data: {}", e))
    } else {
        // Return mock data if file doesn't exist
        Ok(MarketData {
            quotes: vec![
                MarketQuote {
                    symbol: "S&P 500".to_string(),
                    name: "S&P 500".to_string(),
                    price: "7,126".to_string(),
                    change: "+1.20%".to_string(),
                    change_percent: 1.20,
                },
                MarketQuote {
                    symbol: "BTC".to_string(),
                    name: "Bitcoin".to_string(),
                    price: "$75,951".to_string(),
                    change: "-1.86%".to_string(),
                    change_percent: -1.86,
                },
            ],
            forex_rates: vec![
                ("USD/CNY".to_string(), 6.83),
                ("USD/EUR".to_string(), 0.848),
            ]
            .into_iter()
            .collect(),
            fear_greed_index: 26,
        })
    }
}

#[tauri::command]
pub fn load_sentiment_data() -> Result<SentimentData, String> {
    let data_path = get_data_dir().join("sentiment_data.json");

    if data_path.exists() {
        let content = fs::read_to_string(&data_path)
            .map_err(|e| format!("Failed to read sentiment data: {}", e))?;
        serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse sentiment data: {}", e))
    } else {
        // Return mock data if file doesn't exist
        Ok(SentimentData {
            fear_greed_index: 26,
            phase: "冰点/修复".to_string(),
            limit_up_count: 47,
            limit_down_count: 8,
            volume: "7,821亿".to_string(),
            northbound_flow: "+23亿".to_string(),
            margin_balance: "1.58万亿".to_string(),
        })
    }
}

#[tauri::command]
pub fn load_macro_data() -> Result<MacroData, String> {
    let data_path = get_data_dir().join("macro_data.json");

    if data_path.exists() {
        let content = fs::read_to_string(&data_path)
            .map_err(|e| format!("Failed to read macro data: {}", e))?;
        serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse macro data: {}", e))
    } else {
        // Return mock data if file doesn't exist
        Ok(MacroData {
            gdp: 5.0,
            cpi: 1.2,
            pmi: 49.2,
            lpr: 3.45,
        })
    }
}
