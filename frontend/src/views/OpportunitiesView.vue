<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchOpportunities, type Opportunity } from "@/api/opportunities";

const items = ref<Opportunity[]>([]);
const loading = ref(true);

onMounted(async () => {
  items.value = await fetchOpportunities();
  loading.value = false;
});
</script>

<template>
  <div>
    <h1>Steam Flip Opportunities</h1>

    <div v-if="loading">Loading…</div>

    <table v-else>
      <thead>
        <tr>
          <th>Item</th>
          <th>Buy</th>
          <th>Sell</th>
          <th>Profit</th>
          <th>ROI</th>
          <th>Volume</th>
          <th>Risk</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.item_name">
          <td>{{ item.item_name }}</td>
          <td>{{ item.buy_price }}</td>
          <td>{{ item.sell_price }}</td>
          <td>{{ item.net_profit }}</td>
          <td>{{ (item.profit_pct * 100).toFixed(2) }}%</td>
          <td>{{ item.volume }}</td>
          <td :class="item.risk_level.toLowerCase()">
            {{ item.risk_level }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.low {
  color: green;
}
.medium {
  color: orange;
}
.high {
  color: red;
}
</style>
