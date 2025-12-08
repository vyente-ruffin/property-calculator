# Property Investment Calculator

**Make smarter property investment decisions in seconds.** Instantly analyze residential and commercial properties with comprehensive financial metrics, shareable calculations, and professional-grade accuracy.

🚀 **[Live Demo](https://property-calculator.azurewebsites.net/)** | **[GitHub Repository](https://github.com/david-ruffin/property-calculator)**

## 🏆 Why Property Investment Calculator?

- **Save Hours of Manual Calculations** → Get instant cash flow, ROI, and deal analysis
- **Make Data-Driven Decisions** → Compare properties objectively with standardized metrics  
- **Share Analysis Instantly** → Send complete calculations via shareable URLs
- **Avoid Costly Mistakes** → Spot bad deals before you invest with color-coded indicators

## 🚀 Quick Start

**Get running in 2 minutes:**

1. **Clone & Setup**
   ```bash
   git clone [repository-url]
   cd property-calculator-1
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Launch the App**
   ```bash
   streamlit run app.py
   ```

3. **Start Analyzing** → Open http://localhost:8501 and enter your first property

## 💡 How It Works

**Simple 3-step workflow:**
1. **Choose Property Type** → Residential (≤4 units) or Commercial (5+ units)
2. **Enter Property Details** → Purchase price, down payment, rents, location
3. **Get Instant Analysis** → Cash flow, ROI, and investment recommendation

**Smart Features:**
- All inputs update instantly (no sticky behavior)
- State-specific tax/insurance rates for accurate estimates
- Excel-validated commercial formulas for professional accuracy
- Shareable URLs preserve your complete analysis

## 🏡 Key Features

### Residential Properties (≤4 Units)
- **Comprehensive Analysis** → Monthly expenses, cash flow scenarios (75%/90%/100% occupancy)
- **Investment Recommendation** → Clear guidance based on 75% occupancy stress test
- **Loan Amortization** → First-year payment breakdown with visual balance chart
- **State Tax Rates** → Accurate calculations for AZ, CA, IN, NV, TX, MI

### Commercial Properties (5+ Units)  
- **Professional NOI Analysis** → Excel-validated formulas for accurate commercial calculations
- **Operating Expense Breakdown** → Monthly/annual costs with industry explanations
- **Cash-on-Cash Returns** → Investment performance metrics used by commercial investors
- **Deal Evaluation** → Color-coded recommendations (Good Deal/Bad Deal)
- **Smart Down Payment Alerts** → Visual indicators for financing thresholds

### Universal Features
- **Instant Updates** → No sticky inputs or multiple clicks required
- **Shareable Analysis** → Complete calculations preserved in URL for easy sharing
- **Property URL Integration** → Store and access listing URLs directly from calculator
- **Enhanced Link Sharing** → Custom favicon and descriptive page titles for professional appearance
- **State-Specific Data** → Tax and insurance rates for 6 major investment markets  
- **Visual Indicators** → Color-coded metrics for quick decision making

## 🔧 Advanced Details

### Technical Architecture
- **Streamlit Framework** → Fast, responsive web application with real-time updates
- **Callback-Based Inputs** → Prevents sticky behavior and race conditions  
- **Query Parameter Sync** → Complete state preservation in shareable URLs
- **Excel Formula Validation** → Commercial calculations match industry-standard spreadsheets

### Supported Markets
| State | Tax Rate | Insurance Rate | Market Focus |
|-------|----------|----------------|--------------|
| Arizona | 0.62% | 0.5% | Growing sunbelt market |
| California | 1.25% | 1.25% | High-value coastal properties |
| Indiana | 1.37% | 0.5% | Midwest cash flow markets |
| Nevada | 0.65% | 0.5% | Tax-advantaged investing |
| Texas | 1.7% | 0.5% | No state income tax benefits |
| Michigan | 3.21% | 0.5% | Affordable entry markets |

## 🚀 Deployment & CI/CD

### ✅ Production Deployment
**Live on Microsoft Azure**:
- **Azure Web App**: [property-calculator.azurewebsites.net](https://property-calculator.azurewebsites.net/)
- **Python 3.11** runtime with Streamlit on Linux (B1 tier for WebSocket support)
- **Startup Command**: `python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`
- **Custom domain ready** for professional deployment

### ✅ Continuous Integration/Deployment
**Automated GitHub Actions pipeline with OIDC authentication**:
- **Triggers**: Push to main branch or manual dispatch
- **Authentication**: Azure AD federated identity (OIDC) - no secrets to rotate
- **Build Process**: Checkout → Azure Login → Deploy to Web App
- **Deploy Time**: ~4 minutes per deployment
- **Zero-downtime deployments** with Azure Web Apps

## 🤖 Claude Code Integration

This project includes a property listing parser that extracts multifamily property data and sends it to Google Sheets via n8n webhooks.

### Prerequisites
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- n8n instance (self-hosted or cloud)
- Google Sheets for data destination

### Setup

#### 1. Clone and Configure Environment
```bash
git clone https://github.com/david-ruffin/property-calculator.git
cd property-calculator
cp .env.example .env
# Edit .env with your Rentcast API key
```

#### 2. Install n8n MCP Server
The n8n MCP server allows Claude Code to interact with your n8n workflows.

**Source**: [leonardsellem/n8n-mcp-server](https://github.com/leonardsellem/n8n-mcp-server)

In Claude Code, run:
```
/mcp add n8n
```

Configure with:
| Setting | Value |
|---------|-------|
| Command | `npx` |
| Args | `["-y", "@leonardsellem/n8n-mcp-server"]` |
| N8N_API_URL | `https://your-n8n-instance/api/v1` |
| N8N_API_KEY | Your n8n API key |

#### 3. Using the Property Parser
```
@Property-Prompt.md [paste your listing text here]
```

### Google Sheets Column Structure
| Column | Description |
|--------|-------------|
| Price | Listing price |
| Address | Street address only |
| City | City, ST ZIP |
| Cap Rate | Capitalization rate |
| Date On Market | YYYY-MM-DD |
| Monthly Rental Income (Projected) | Scheduled/market rent |
| Monthly Rental Income (Actual) | Current collected rent |
| Annual Rent Income (Projected) | Projected × 12 |
| Annual Rent Income (Actual) | Actual × 12 |
| NOI | Net Operating Income |
| Lot / building size | SF / SF |
| Total Units | Number of units |
| Unit Mix Summary | Using actual rents |
| Link | Listing URL |
| Description | One-line summary |
| Analyze | (manual) |
| Investible | (manual) |
| Cashflow | (manual) |
| Notes | (manual) |

## 🚀 Future Roadmap

### ✅ Phase 1: Property URL Integration (Completed!)
**One-click property access is now live**:
- ✅ **Property URL Fields** → Store listing URLs (LoopNet, Zillow, etc.) alongside calculations
- ✅ **"View Property Listing" Button** → Opens property listings in new tabs with single click
- ✅ **Enhanced Sharing** → Calculator URLs now include property context for team collaboration
- ✅ **Complete URL Preservation** → Share analysis with direct access to original listing

### Phase 2: Auto-Population (Next Up)
**Eliminate manual data entry entirely**:
- **Smart URL Parsing** → Paste listing URL, auto-fill purchase price, rents, taxes
- **Multi-Platform Support** → LoopNet, Zillow, Crexi, and other major listing sites
- **Time Savings** → Go from listing to analysis in under 30 seconds

## 📊 Data Sources & Accuracy

**Commercial Calculations**: Sourced from `Commercial_Prop_Screening_Tool.xlsx`
- Industry-standard NOI methodology
- Excel cell references maintained for accuracy
- Validated against real commercial deals

**Tax & Insurance Rates**: Based on state averages
- Updated annually for accuracy
- Covers 85%+ of U.S. investment markets
- Conservative estimates for reliable projections