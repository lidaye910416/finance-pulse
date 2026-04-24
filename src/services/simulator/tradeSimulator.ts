/**
 * 模拟交易系统
 * 
 * 支持买入/卖出/撤单/持仓管理
 * 参考 ai-hedge-fund 架构
 */

import { StockData } from '../analysis/types';

// ========== 交易相关类型 ==========

export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit';
export type OrderStatus = 'pending' | 'filled' | 'cancelled' | 'rejected';
export type PositionSide = 'long' | 'short';

export interface Order {
  id: string;
  code: string;           // 股票代码
  name: string;           // 股票名称
  side: OrderSide;         // 买入/卖出
  type: OrderType;         // 市价/限价
  price: number;          // 委托价格
  quantity: number;        // 委托数量
  filledQty: number;       // 已成交数量
  avgPrice: number;        // 成交均价
  status: OrderStatus;     // 订单状态
  positionSide: PositionSide; // 持仓方向
  createdAt: number;      // 创建时间
  updatedAt: number;      // 更新时间
  filledAt?: number;      // 成交时间
  reason?: string;        // 拒绝/撤单原因
}

export interface Position {
  code: string;
  name: string;
  quantity: number;       // 持仓数量
  avgCost: number;        // 持仓成本
  side: PositionSide;      // 持仓方向
  unrealizedPnL: number;  // 浮动盈亏
  realizedPnL: number;    // 已实现盈亏
  todayBuyQty: number;    // 今日买入数量
  todaySellQty: number;   // 今日卖出数量
  availableQty: number;   // 可用数量
}

export interface Account {
  cash: number;           // 可用资金
  frozenCash: number;     // 冻结资金
  totalAssets: number;     // 总资产
  marketValue: number;     // 市值
  totalProfit: number;     // 总盈亏
  profitPercent: number;   // 收益率
}

export interface TradeRecord {
  date: string;
  code: string;
  name: string;
  side: OrderSide;
  price: number;
  quantity: number;
  amount: number;
  commission: number;     // 手续费
}

export interface SimulatorConfig {
  initialCash: number;     // 初始资金
  commissionRate: number;  // 手续费率 (默认万3)
  stampTaxRate: number;    // 印花税率 (卖出收万10)
  minCommission: number;   // 最低佣金
}

interface QuoteMap {
  [code: string]: StockData;
}

// ========== 模拟交易引擎 ==========

export class TradeSimulator {
  private orders: Order[] = [];
  private positions: Map<string, Position> = new Map();
  private tradeHistory: TradeRecord[] = [];
  private account: Account;
  private config: SimulatorConfig;
  private quotes: QuoteMap = {};
  
  // 统计
  private totalOrders = 0;
  private filledOrders = 0;
  private cancelledOrders = 0;

  constructor(config?: Partial<SimulatorConfig>) {
    this.config = {
      initialCash: 100000,  // 默认10万
      commissionRate: 0.0003,
      stampTaxRate: 0.001,
      minCommission: 5,
      ...config,
    };
    
    this.account = {
      cash: this.config.initialCash,
      frozenCash: 0,
      totalAssets: this.config.initialCash,
      marketValue: 0,
      totalProfit: 0,
      profitPercent: 0,
    };
    
    console.log(`[TradeSimulator] 初始化完成，初始资金: ¥${this.config.initialCash.toLocaleString()}`);
  }

  // 更新行情
  updateQuotes(quotes: StockData[]) {
    quotes.forEach(q => {
      this.quotes[q.code] = q;
    });
    this.calculateAccount();
  }

  // ========== 订单操作 ==========

  // 市价买入
  buyMarket(code: string, name: string, quantity: number): Order {
    return this.createOrder(code, name, 'buy', 'market', 0, quantity);
  }

  // 限价买入
  buyLimit(code: string, name: string, price: number, quantity: number): Order {
    return this.createOrder(code, name, 'buy', 'limit', price, quantity);
  }

  // 市价卖出
  sellMarket(code: string, name: string, quantity: number): Order {
    return this.createOrder(code, name, 'sell', 'market', 0, quantity);
  }

  // 限价卖出
  sellLimit(code: string, name: string, price: number, quantity: number): Order {
    return this.createOrder(code, name, 'sell', 'limit', price, quantity);
  }

  // 创建订单
  private createOrder(
    code: string,
    name: string,
    side: OrderSide,
    type: OrderType,
    price: number,
    quantity: number
  ): Order {
    this.totalOrders++;
    
    // 检查持仓是否足够卖出
    if (side === 'sell') {
      const position = this.positions.get(code);
      if (!position || position.availableQty < quantity) {
        const order: Order = {
          id: this.generateId(),
          code,
          name,
          side,
          type,
          price,
          quantity,
          filledQty: 0,
          avgPrice: 0,
          status: 'rejected',
          positionSide: position?.side || 'long',
          createdAt: Date.now(),
          updatedAt: Date.now(),
          reason: '持仓不足',
        };
        this.orders.push(order);
        return order;
      }
    }
    
    // 检查资金是否足够买入
    if (side === 'buy') {
      const quote = this.quotes[code];
      const estimatedCost = (price || quote?.price || 0) * quantity;
      const totalCost = this.calculateTotalCost(estimatedCost, 'buy');
      if (this.account.cash < totalCost) {
        const order: Order = {
          id: this.generateId(),
          code,
          name,
          side,
          type,
          price,
          quantity,
          filledQty: 0,
          avgPrice: 0,
          status: 'rejected',
          positionSide: 'long',
          createdAt: Date.now(),
          updatedAt: Date.now(),
          reason: '资金不足',
        };
        this.orders.push(order);
        return order;
      }
    }

    const quote = this.quotes[code];
    const orderPrice = type === 'market' ? quote?.price || price : price;
    
    const order: Order = {
      id: this.generateId(),
      code,
      name,
      side,
      type,
      price: orderPrice,
      quantity,
      filledQty: 0,
      avgPrice: 0,
      status: 'pending',
      positionSide: 'long',
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    
    this.orders.push(order);
    
    // 如果是市价单，立即成交
    if (type === 'market') {
      this.fillOrder(order.id, orderPrice);
    }
    
    return order;
  }

  // 撤单
  cancelOrder(orderId: string): boolean {
    const order = this.orders.find(o => o.id === orderId);
    if (!order) return false;
    
    if (order.status !== 'pending') {
      return false;
    }
    
    order.status = 'cancelled';
    order.updatedAt = Date.now();
    order.reason = '用户撤单';
    this.cancelledOrders++;
    
    console.log(`[TradeSimulator] 撤单成功: ${orderId}`);
    return true;
  }

  // 成交订单
  private fillOrder(orderId: string, fillPrice: number) {
    const order = this.orders.find(o => o.id === orderId);
    if (!order) return;
    
    const quantity = order.quantity;
    const amount = fillPrice * quantity;
    const commission = this.calculateCommission(amount, order.side);
    
    order.filledQty = quantity;
    order.avgPrice = fillPrice;
    order.status = 'filled';
    order.filledAt = Date.now();
    order.updatedAt = Date.now();
    
    this.filledOrders++;
    
    // 更新持仓
    this.updatePosition(order, fillPrice, commission);
    
    // 记录交易
    this.tradeHistory.push({
      date: new Date().toISOString().split('T')[0],
      code: order.code,
      name: order.name,
      side: order.side,
      price: fillPrice,
      quantity,
      amount,
      commission,
    });
    
    // 计算账户
    this.calculateAccount();
    
    console.log(`[TradeSimulator] 成交: ${order.side} ${order.name} ${quantity}股 @ ¥${fillPrice}`);
  }

  // 更新持仓
  private updatePosition(order: Order, price: number, commission: number) {
    const { code, name, side, quantity } = order;
    let position = this.positions.get(code);
    
    if (side === 'buy') {
      if (!position) {
        position = {
          code,
          name,
          quantity: 0,
          avgCost: 0,
          side: 'long',
          unrealizedPnL: 0,
          realizedPnL: 0,
          todayBuyQty: 0,
          todaySellQty: 0,
          availableQty: 0,
        };
        this.positions.set(code, position);
      }
      
      // 计算新的持仓成本
      const totalCost = position.avgCost * position.quantity + price * quantity + commission;
      const totalQty = position.quantity + quantity;
      position.avgCost = totalQty > 0 ? totalCost / totalQty : 0;
      position.quantity += quantity;
      position.availableQty += quantity;
      position.todayBuyQty += quantity;
      
      // 冻结资金
      const totalFrozen = price * quantity + commission;
      this.account.cash -= totalFrozen;
      this.account.frozenCash -= totalFrozen;
    } else {
      if (position) {
        // 卖出，减少持仓
        const sellAmount = price * quantity - commission;
        const profit = (price - position.avgCost) * quantity;
        
        position.quantity -= quantity;
        position.availableQty -= quantity;
        position.realizedPnL += profit;
        position.todaySellQty += quantity;
        
        // 解冻资金
        this.account.cash += sellAmount;
        
        // 如果持仓为0，清除持仓记录
        if (position.quantity <= 0) {
          this.positions.delete(code);
        }
      }
    }
  }

  // 计算手续费
  private calculateCommission(amount: number, side: OrderSide): number {
    let commission = amount * this.config.commissionRate;
    
    // 印花税（仅卖出）
    if (side === 'sell') {
      commission += amount * this.config.stampTaxRate;
    }
    
    // 最低佣金
    return Math.max(commission, this.config.minCommission);
  }

  // 计算总成本（含手续费）
  private calculateTotalCost(amount: number, side: OrderSide): number {
    return amount + this.calculateCommission(amount, side);
  }

  // 计算账户
  private calculateAccount() {
    let marketValue = 0;
    
    this.positions.forEach((position) => {
      const quote = this.quotes[position.code];
      if (quote) {
        const value = quote.price * position.quantity;
        position.unrealizedPnL = (quote.price - position.avgCost) * position.quantity;
        marketValue += value;
      }
    });
    
    this.account.marketValue = marketValue;
    this.account.totalAssets = this.account.cash + marketValue;
    this.account.totalProfit = this.account.totalAssets - this.config.initialCash;
    this.account.profitPercent = (this.account.totalProfit / this.config.initialCash) * 100;
  }

  // 生成ID
  private generateId(): string {
    return `ORD_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // ========== 查询接口 ==========

  // 获取账户信息
  getAccount(): Account {
    this.calculateAccount();
    return { ...this.account };
  }

  // 获取所有持仓
  getPositions(): Position[] {
    return Array.from(this.positions.values());
  }

  // 获取持仓
  getPosition(code: string): Position | undefined {
    return this.positions.get(code);
  }

  // 获取所有订单
  getOrders(status?: OrderStatus): Order[] {
    if (status) {
      return this.orders.filter(o => o.status === status);
    }
    return [...this.orders];
  }

  // 获取交易历史
  getTradeHistory(): TradeRecord[] {
    return [...this.tradeHistory];
  }

  // 获取统计数据
  getStatistics() {
    const totalTrades = this.tradeHistory.length;
    const buyTrades = this.tradeHistory.filter(t => t.side === 'buy').length;
    const sellTrades = this.tradeHistory.filter(t => t.side === 'sell').length;
    const totalCommission = this.tradeHistory.reduce((sum, t) => sum + t.commission, 0);
    
    return {
      totalOrders: this.totalOrders,
      filledOrders: this.filledOrders,
      cancelledOrders: this.cancelledOrders,
      totalTrades,
      buyTrades,
      sellTrades,
      totalCommission,
      winRate: this.calculateWinRate(),
    };
  }

  // 计算胜率
  private calculateWinRate(): number {
    const closedPositions = this.tradeHistory.filter(t => t.side === 'sell');
    if (closedPositions.length === 0) return 0;
    
    const winningTrades = closedPositions.filter(_t => {
      // 需要找到对应的买入记录来计算盈亏
      return true; // 简化计算
    }).length;
    
    return (winningTrades / closedPositions.length) * 100;
  }

  // ========== 批量操作 ==========

  // 批量市价买入
  batchBuyMarket(orders: Array<{ code: string; name: string; quantity: number }>): Order[] {
    return orders.map(o => this.buyMarket(o.code, o.name, o.quantity));
  }

  // 批量市价卖出（清仓）
  clearPosition(code: string): Order | null {
    const position = this.positions.get(code);
    if (!position) return null;
    return this.sellMarket(code, position.name, position.availableQty);
  }

  // 一键清仓
  clearAllPositions(): Order[] {
    const orders: Order[] = [];
    this.positions.forEach((position) => {
      const order = this.clearPosition(position.code);
      if (order) orders.push(order);
    });
    return orders;
  }

  // 重置账户
  reset() {
    this.orders = [];
    this.positions.clear();
    this.tradeHistory = [];
    this.account = {
      cash: this.config.initialCash,
      frozenCash: 0,
      totalAssets: this.config.initialCash,
      marketValue: 0,
      totalProfit: 0,
      profitPercent: 0,
    };
    this.totalOrders = 0;
    this.filledOrders = 0;
    this.cancelledOrders = 0;
    
    console.log('[TradeSimulator] 账户已重置');
  }
}

// ========== 单例导出 ==========

export const tradeSimulator = new TradeSimulator();
export default tradeSimulator;
