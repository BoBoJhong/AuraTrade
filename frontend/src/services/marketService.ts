/**
 * Market Data Service
 * 市場資料服務 - 基本面分析、股利資訊、法人動態
 */
import axios from '@/lib/axios';

// 基本面資料介面
export interface FundamentalData {
  symbol: string;
  name: string;
  pe_ratio: number | null;  // 本益比
  dividend_yield: number | null;  // 殖利率 (%)
  pb_ratio: number | null;  // 股價淨值比
}

// 股利資訊介面
export interface DividendInfo {
  symbol: string;
  name: string;
  cash_dividend: number;  // 現金股利
  stock_dividend: number;  // 股票股利
  ex_dividend_date: string;  // 除息日
  total_dividend: number;  // 合計股利
}

// 法人資料介面
export interface InstitutionalData {
  symbol: string;
  name: string;
  foreign_buy: number;
  foreign_sell: number;
  foreign_net: number;  // 外資買賣超
  trust_net: number;  // 投信買賣超
  dealer_net: number;  // 自營商買賣超
}

// 綜合資訊介面
export interface ComprehensiveStockInfo {
  symbol: string;
  fundamental: FundamentalData | null;
  dividend: DividendInfo | null;
}

/**
 * 獲取股票基本面資料
 */
export const getFundamentalData = async (symbol: string): Promise<FundamentalData> => {
  const response = await axios.get(`/market/fundamental/${symbol}`);
  return response.data.data;
};

/**
 * 獲取股票股利資訊
 */
export const getDividendInfo = async (symbol: string): Promise<DividendInfo> => {
  const response = await axios.get(`/market/dividend/${symbol}`);
  return response.data.data;
};

/**
 * 獲取三大法人買賣超資訊
 */
export const getInstitutionalData = async (date?: string): Promise<InstitutionalData[]> => {
  const params = date ? { date } : {};
  const response = await axios.get('/market/institutional', { params });
  return response.data.data;
};

/**
 * 獲取股票綜合資訊（一次取得所有資料）
 */
export const getComprehensiveStockInfo = async (symbol: string): Promise<ComprehensiveStockInfo> => {
  const response = await axios.get(`/market/stock-info/${symbol}`);
  return response.data.data;
};
