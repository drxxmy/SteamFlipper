<script setup lang="ts">
import { ref } from "vue";
import { addWatchlistItem } from "@/api/watchlist";

const url = ref("");
const loading = ref(false);

async function submit() {
  if (!url.value) return;

  loading.value = true;
  await addWatchlistItem(url.value);
  url.value = "";
  loading.value = false;
}
</script>

<template>
  <div class="flex gap-2">
    <input
      v-model="url"
      class="flex-1 py-2 px-3 rounded-lg border bg-bg border-border"
      placeholder="Steam Market item link"
    />
    <button
      @click="submit"
      :disabled="loading"
      class="py-2 px-4 font-semibold text-black rounded-lg bg-red"
    >
      Add
    </button>
  </div>
</template>
