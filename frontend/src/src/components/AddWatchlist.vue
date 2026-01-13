<script setup lang="ts">
import { ref } from "vue";
import { addWatchlistItem } from "@/api/watchlist";

const emit = defineEmits<{
  (e: "added"): void;
}>();

const url = ref("");
const loading = ref(false);

async function submit() {
  if (!url.value) return;

  loading.value = true;
  try {
    await addWatchlistItem(url.value);
    emit("added"); // notify parent
    url.value = "";
  } finally {
    loading.value = false;
  }
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
      class="py-2 px-4 font-semibold rounded-lg border transition text-text bg-panel border-border hover:bg-panel-light"
    >
      Add
    </button>
  </div>
</template>
