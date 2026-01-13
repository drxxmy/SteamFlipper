import { api } from "./client";

export interface Opportunity {
  id: number;
  app_id: number;
  item_name: string;
  buy_price: number;
  sell_price: number;
  net_profit: number;
  profit_pct: number;
  volume: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  detected_at: string;
}

export async function fetchOpportunities(): Promise<Opportunity[]> {
  const res = await api.get("/opportunities");
  return res.data;
}
