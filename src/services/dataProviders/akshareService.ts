/**
 * AKShare 数据服务
 *
 * 免费开源的金融数据接口
 * https://akshare.akfamily.cn/
 */

export type KLinePeriod = 'daily' | 'weekly' | 'monthly';

export class AKShareService {
  private baseUrl = 'https://akshare.akfamily.cn';

  /**
   * 获取实时行情
   */
  async getRealtimeQuote(codes: string[]): Promise<Record<string, any>> {
    try {
      const codeStr = codes.join(',');
      const response = await fetch(
        `${this.baseUrl}/api/quote/real?codes=${encodeURIComponent(codeStr)}`
      );
      const data = await response.json();
      
      // 格式化数据
      const result: Record<string, any> = {};
      for (const item of data.data || []) {
        result[item[1]] = {
          code: item[1],
          name: item[2],
          price: item[3],
          change: item[31],
          changePercent: item[32],
          volume: item[4],
          amount: item[5],
          high: item[33],
          low: item[34],
          open: item[1],
          prevClose: item[2],
        };
      }
      return result;
    } catch (error) {
      console.error('[AKShare] 获取实时行情失败:', error);
      return {};
    }
  }

  /**
   * 获取K线数据
   */
  async getKlineHistory(
    code: string,
    period: 'daily' | 'weekly' | 'monthly' = 'daily',
    startDate?: string,
    endDate?: string
  ): Promise<any[]> {
    try {
      const params = new URLSearchParams({
        symbol: code,
        period: period,
        adjust: 'qfq',
      });
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await fetch(
        `${this.baseUrl}/api/quote/kline?${params.toString()}`
      );
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('[AKShare] 获取K线失败:', error);
      return [];
    }
  }

  /**
   * 获取资金流向
   */
  async getMoneyFlow(code: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/quote/money_flow?symbol=${code}`
      );
      const data = await response.json();
      return data.data;
    } catch (error) {
      console.error('[AKShare] 获取资金流向失败:', error);
      return null;
    }
  }

  /**
   * 获取北向资金
   */
  async getNorthboundMoney(): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/quote/hsgt/north_money`
      );
      const data = await response.json();
      return data.data;
    } catch (error) {
      console.error('[AKShare] 获取北向资金失败:', error);
      return null;
    }
  }

  /**
   * 获取板块资金流向
   */
  async getSectorMoneyFlow(): Promise<any[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/quote/sector/money_flow`
      );
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('[AKShare] 获取板块资金流向失败:', error);
      return [];
    }
  }

  /**
   * 获取恐惧贪婪指数
   */
  async getFearGreedIndex(): Promise<{ value: number; phase: string }> {
    try {
      // AlternativeMe 的 API
      const response = await fetch('https://api.alternative.me/fng/');
      const data = await response.json();
      const value = parseInt(data.data[0].value);
      
      let phase = '中性';
      if (value < 25) phase = '极度恐惧';
      else if (value < 45) phase = '恐惧';
      else if (value < 55) phase = '中性';
      else if (value < 75) phase = '贪婪';
      else phase = '极度贪婪';

      return { value, phase };
    } catch (error) {
      console.error('[AKShare] 获取恐惧贪婪指数失败:', error);
      return { value: 50, phase: '中性' };
    }
  }

  /**
   * 获取宏观经济数据
   */
  async getMacroData(indicator: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/macro/${indicator}`
      );
      const data = await response.json();
      return data.data;
    } catch (error) {
      console.error('[AKShare] 获取宏观数据失败:', error);
      return null;
    }
  }
}

// 导出单例
export const akshareService = new AKShareService();
