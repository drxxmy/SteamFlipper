<script setup lang="ts">
import { computed } from "vue";
import { ArrowUp, ArrowDown } from "lucide-vue-next";

type Align = "left" | "right" | "center";

const props = defineProps<{
  label: string;
  field: string;
  sortKey: string;
  sortDir: "asc" | "desc";
  align?: Align;
}>();

const emit = defineEmits<{
  (e: "sort", field: string): void;
}>();

const isActive = computed(() => props.sortKey === props.field);
</script>

<template>
  <th
    @click="emit('sort', field)"
    class="py-3 px-4 whitespace-nowrap transition cursor-pointer select-none hover:bg-panel-light"
    :class="{
      'text-left': align === 'left',
      'text-right': align === 'right',
      'text-center': align === 'center',
    }"
  >
    <span class="inline-flex gap-1 items-center">
      {{ label }}

      <!-- sort icon -->
      <span v-if="isActive" class="inline-flex">
        <ArrowUp v-if="isActive && sortDir === 'asc'" class="w-4 h-4" />
        <ArrowDown v-else-if="isActive" class="w-4 h-4" />
        <ArrowUp v-else class="w-4 h-4 opacity-30" />
      </span>
    </span>
  </th>
</template>
