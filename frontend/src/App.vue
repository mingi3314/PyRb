<script setup>
import { ref } from 'vue';
import Account from './components/Account.vue';
import Rebalance from './components/Rebalance.vue';
import PortfolioTable from './components/PortfolioTable.vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

const isAccountModalOpen = ref(false);
const isRebalanceModalOpen = ref(false);
</script>

<template>
  <div class="mx-5" id="app">
    <div class="flex justify-content-end p-3 gap-3">
      <Button label="계좌 등록하기" @click="isAccountModalOpen = true" />
      <Button label="리밸런싱 실행" @click="isRebalanceModalOpen = true" />
    </div>

    <Dialog v-model:visible="isAccountModalOpen" modal header="계좌 등록">
      <Account />
    </Dialog>

    <Dialog v-model:visible="isRebalanceModalOpen" modal header="주문 확인">
      <Rebalance />
    </Dialog>

    <PortfolioTable />
  </div>
</template>
