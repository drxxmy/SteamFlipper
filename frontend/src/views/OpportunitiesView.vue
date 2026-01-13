<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchOpportunities, type Opportunity } from "@/api/opportunities";

const items = ref<Opportunity[]>([]);
const loading = ref(true);

onMounted(async () => {
  items.value = await fetchOpportunities();
  loading.value = false;
});

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
            <th class="py-3 px-4 text-left">Item</th>
            <th class="py-3 px-4 text-right">Buy</th>
            <th class="py-3 px-4 text-right">Sell</th>
            <th class="py-3 px-4 text-right">Profit</th>
            <th class="py-3 px-4 text-right">ROI</th>
            <th class="py-3 px-4 text-right">Volume</th>
            <th class="py-3 px-4 text-center">Risk</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="item in items"
            :key="item.item_name"
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
