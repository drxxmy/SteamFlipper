import { createRouter, createWebHistory } from "vue-router";
import OpportunitiesView from "@/views/OpportunitiesView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: OpportunitiesView },
  ],
});
