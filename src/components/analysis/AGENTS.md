# Analysis Components - Developer Guide

## Component Architecture

### Page Layout (PRD Section 12.1)
The `AnalysisPage.tsx` arranges components in a 2-column grid layout:
- `StockHeader` - Search and quote display (full width)
- `AnalysisParams` - Mode, leader, convergence, risk controls (full width)
- `KlineChart` - Spans 2 columns on large screens
- `FundFlowPanel` / `SignalPanel` - Side by side
- `RecommendationCard` / `SummaryText` - Side by side

### Key Types
- `AnalysisMode` exported from `AnalysisParams.tsx`: `'tradingagents' | 'aihedgefund' | 'fusion'`
- Use `string | null` for leaderId (not `undefined`)
- Risk levels: `'conservative' | 'moderate' | 'aggressive'`

## API Integration
Components expect data from these endpoints:
- `GET /api/leaders` - Leader list for `AnalysisParams`
- `GET /api/config/convergence` - Convergence presets
- `GET /api/config/risk-levels` - Risk preferences

## Component Props Patterns
- All components provide fallback/sample data when APIs are unavailable
- Use `Card` component as wrapper for consistent styling
- Optional props typically have default values in component implementation
