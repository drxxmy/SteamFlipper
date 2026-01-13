<script setup lang="ts">
import { useAsyncState } from "@vueuse/core";
import SortableTh from "@/components/SortableTh.vue";
import AddWatchlist from "@/components/AddWatchlist.vue";
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

const { state: items, isLoading: loading } = useAsyncState<Opportunity[]>(
  fetchOpportunities,
  [],
  { immediate: true },
);

/* ---------------- helpers ---------------- */

function openSteam(item_name: string) {
  window.open(
    "https://steamcommunity.com/market/listings/730/" + item_name,
    "_blank",
    "noopener,noreferrer",
  );
}

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
      return "bg-green text-green-900";
    case "MEDIUM":
      return "bg-yellow text-yellow-900";
    case "HIGH":
      return "bg-red text-red-900";
    default:
      return "bg-muted text-gray-900";
  }
}

function onAdded(opportunity: Opportunity | null) {
  if (!opportunity) return;

  // avoid duplicates
  if (items.value.some((i) => i.item_name === opportunity.item_name)) return;

  items.value = [opportunity, ...items.value];
}
</script>

<template>
  <div class="p-6 mx-auto max-w-7xl">
    <h1 class="mb-4 text-2xl font-semibold">Steam Flip Opportunities</h1>

    <div v-if="loading" class="text-muted">Loading…</div>

    <div v-else class="overflow-x-auto my-2 rounded-lg border border-border">
      <table class="min-w-full text-sm">
        <thead class="sticky top-0 text-xs uppercase text-muted bg-panel">
          <tr>
            <SortableTh
              label="Item"
              field="item_name"
              align="left"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />

            <SortableTh
              label="Buy"
              field="buy_price"
              align="right"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />

            <SortableTh
              label="Sell"
              field="sell_price"
              align="right"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />

            <SortableTh
              label="Profit"
              field="net_profit"
              align="right"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />

            <SortableTh
              label="ROI"
              field="profit_pct"
              align="right"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />

            <SortableTh
              label="Volume"
              field="volume"
              align="right"
              :sort-key="sortKey"
              :sort-dir="sortDir"
              @sort="sortBy"
            />
            <th class="py-3 px-4 text-center">Risk</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-border">
          <tr
            v-for="item in sortedItems"
            :key="item.id"
            class="hover:cursor-pointer hover:bg-panel-light"
            @click="openSteam(item.item_name)"
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
              :class="item.net_profit >= 0 ? 'text-green' : 'text-red'"
            >
              {{ item.net_profit.toFixed(2) }}
            </td>

            <td
              class="py-2 px-4 font-mono text-right"
              :class="item.profit_pct >= 0 ? 'text-green' : 'text-red'"
            >
              {{ (item.profit_pct * 100).toFixed(2) }}%
            </td>

            <td class="py-2 px-4 font-mono text-right text-muted">
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
    <AddWatchlist @added="onAdded" />
  </div>
</template>
