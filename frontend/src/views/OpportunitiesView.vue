<script setup lang="ts">
import { useAsyncState, useIntervalFn } from "@vueuse/core";
import { fetchOpportunities, type Opportunity } from "@/api/opportunities";

/* ---------------- sorting state ---------------- */

import { computed, ref } from "vue";

type SortKey =
  | "item_name"
  | "buy_price"
  | "sell_price"
  | "net_profit"
  | "profit_pct"
  | "volume"
  | "risk_level";

const sortKey = ref<SortKey>("net_profit");
const sortDir = ref<"asc" | "desc">("desc");

/* ---------------- sorted list of items ---------------- */

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => {
    const key = sortKey.value;
    const dir = sortDir.value === "asc" ? 1 : -1;

    const av = a[key];
    const bv = b[key];

    if (typeof av === "number" && typeof bv === "number") {
      return (av - bv) * dir;
    }

    return String(av).localeCompare(String(bv)) * dir;
  });
});

/* ---------------- data ---------------- */

const {
  state: items,
  isLoading: loading,
  execute: refresh,
} = useAsyncState<Opportunity[]>(fetchOpportunities, [], { immediate: true });

// useIntervalFn(refresh, 15_000); // Auto-refresh

/* ---------------- helpers ---------------- */

function sortBy(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = key;
    sortDir.value = "desc";
  }
}

function riskBadge(risk: string) {
  switch (risk) {
    case "LOW":
      return "bg-green-100 text-green-700";
    case "MEDIUM":
      return "bg-yellow-100 text-yellow-700";
    case "HIGH":
      return "bg-red-100 text-red-700";
    default:
      return "bg-gray-100 text-gray-700";
  }
}
</script>

<template>
  <div class="p-6 mx-auto max-w-7xl">
    <h1 class="mb-4 text-2xl font-semibold">Steam Flip Opportunities</h1>

    <div v-if="loading" class="text-gray-500">Loading…</div>

    <div v-else class="overflow-x-auto rounded-lg border border-gray-200">
      <table class="min-w-full text-sm">
        <thead class="sticky top-0 text-xs text-gray-700 uppercase bg-gray-100">
          <tr>
            <th
              class="py-3 px-4 text-left cursor-pointer select-none"
              @click="sortBy('item_name')"
            >
              Item
              <span v-if="sortKey === 'item_name'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th
              class="py-3 px-4 text-right cursor-pointer select-none"
              @click="sortBy('buy_price')"
            >
              Buy
              <span v-if="sortKey === 'buy_price'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th
              class="py-3 px-4 text-right cursor-pointer select-none"
              @click="sortBy('sell_price')"
            >
              Sell
              <span v-if="sortKey === 'sell_price'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th
              class="py-3 px-4 text-right cursor-pointer select-none"
              @click="sortBy('net_profit')"
            >
              Profit
              <span v-if="sortKey === 'net_profit'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th
              class="py-3 px-4 text-right cursor-pointer select-none"
              @click="sortBy('profit_pct')"
            >
              ROI
              <span v-if="sortKey === 'profit_pct'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th
              class="py-3 px-4 text-right cursor-pointer select-none"
              @click="sortBy('volume')"
            >
              Volume
              <span v-if="sortKey === 'volume'">
                {{ sortDir === "asc" ? "▲" : "▼" }}
              </span>
            </th>
            <th class="py-3 px-4 text-center">Risk</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="item in sortedItems"
            :key="item.id"
            class="hover:bg-gray-50"
          >
            <td class="py-2 px-4 font-medium whitespace-nowrap">
              {{ item.item_name }}
            </td>

            <td class="py-2 px-4 font-mono text-right">
              {{ item.buy_price.toFixed(2) }}
            </td>

            <td class="py-2 px-4 font-mono text-right">
              {{ item.sell_price.toFixed(2) }}
            </td>

            <td
              class="py-2 px-4 font-mono text-right"
              :class="item.net_profit >= 0 ? 'text-green-600' : 'text-red-600'"
            >
              {{ item.net_profit.toFixed(2) }}
            </td>

            <td
              class="py-2 px-4 font-mono text-right"
              :class="item.profit_pct >= 0 ? 'text-green-600' : 'text-red-600'"
            >
              {{ (item.profit_pct * 100).toFixed(2) }}%
            </td>

            <td class="py-2 px-4 font-mono text-right text-gray-700">
              {{ item.volume }}
            </td>

            <td class="py-2 px-4 text-center">
              <span
                class="py-1 px-2 text-xs font-semibold rounded-full"
                :class="riskBadge(item.risk_level)"
              >
                {{ item.risk_level }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
