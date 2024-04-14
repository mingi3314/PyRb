<template>
    <div>
        <div v-if="orders.length">
            <DataTable :value="ordersTableData">
                <Column field="symbol" header="종목코드"></Column>
                <Column field="price" header="가격"></Column>
                <Column field="quantity" header="수량"></Column>
                <Column field="side" header="종류"></Column>
            </DataTable>
        </div>
        <div v-else>주문 불러오는중...</div>
        <div class="button-container p-fluid">
            <Button label="주문 실행" @click="placeOrders"></Button>
        </div>

        <div class="w-full text-center mt-3">
            <span class="p-text-secondary">모든 주문은 시장가 주문으로 제출됩니다.</span>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from 'axios';
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { toCurrency } from "./utils";

const orders = ref([]);
const ordersTableData = computed(() => {
    return orders.value.map(order => ({
        symbol: order.symbol,
        price: toCurrency(order.price),
        quantity: order.quantity,
        side: order.side === 'SELL' ? '매도' : '매수'
    }));
});

onMounted(async () => {
    orders.value = await fetchOrders();
})

async function fetchOrders() {
    try {
        const response = await axios.get('http://localhost:8000/strategies/all-weather-kr/orders');
        console.log(response.data); // 성공 응답 처리
        return response.data.orders;
    } catch (error) {
        console.error('계좌 등록에 실패했습니다:', error);
    }
}

async function placeOrders() {
    try {
        const response = await axios.post('http://localhost:8000/strategies/all-weather-kr/orders', { 'orders': orders.value });
        console.log(response.data); // 성공 응답 처리
    } catch (error) {
        console.error('계좌 등록에 실패했습니다:', error);
    }
}
</script>


<style scoped>
.button-container {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
}
</style>